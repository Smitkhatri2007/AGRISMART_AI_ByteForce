"""
AgriSmart AI - Version 1.0 Test Suite (CV Model + Gemini Pro Advisory)
Verifies:
1. CV Model 1 - Submission contract CLI & Python callable (predict(image_path) -> class_label)
2. Gemini Pro Service - Disease description generation and cure prompt ("Would you like a cure plan?")
3. Gemini Pro Service - On-demand cure and treatment plan generation
4. CLI Execution - Image prediction, --describe flag, --cure flag, and --cure-for flag
5. Database Persistence - Storing detection, description, and cure metrics in SQLite
6. Disease Service Layer Coordination
"""

import sys
import os
import subprocess
import unittest
from PIL import Image

# Add root directory to python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from model.predict import predict
from model.disease_model import disease_model
from model.fake_engine import default_engine
from model.class_catalog import ALL_CLASSES, CLASS_METADATA
from app.services.gemini_service import gemini_advisor
from app.database import init_db, SessionLocal
from app.models.diagnosis import DiseasePrediction
from app.services.disease_service import disease_service


class TestVersion1GeminiProIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test leaf image
        cls.test_image_path = os.path.join(ROOT_DIR, "test_leaf_synthetic.jpg")
        img = Image.new("RGB", (256, 256), color=(45, 120, 50))
        img.save(cls.test_image_path)

        # Remove old db if exists to ensure clean table recreation
        db_file = os.path.join(ROOT_DIR, "agrismart.db")
        if os.path.exists(db_file):
            os.remove(db_file)

        init_db()

    @classmethod
    def tearDownClass(cls):
        # Clean up test image
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)

    def test_01_cv_model_python_callable_contract(self):
        """Verify CV Model: predict(image_path) -> class_label returns a valid shared class string"""
        label = predict(self.test_image_path)
        self.assertIsInstance(label, str)
        self.assertIn(label, ALL_CLASSES, f"Returned class '{label}' is not in the shared class list!")
        print(f"  [PASS] CV Model Python callable returned: '{label}'")

    def test_02_cv_model_cli_contracts(self):
        """Verify mandatory CLI execution prints strictly the class label"""
        for script in ["model/predict.py", "predict.py"]:
            cmd = [sys.executable, script, "--image", self.test_image_path]
            result = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"CLI {script} failed: {result.stderr}")
            output = result.stdout.strip()
            self.assertIn(output, ALL_CLASSES)
            print(f"  [PASS] Mandatory CLI {script} printed: '{output}'")

    def test_03_gemini_disease_description_and_cure_prompt(self):
        """Verify Gemini Pro generates disease description and prompts if the farmer wants a cure"""
        desc = gemini_advisor.describe_disease(
            disease_name="Tomato Early Blight",
            crop="Tomato",
            severity="Medium",
            is_healthy=False
        )
        self.assertIn("description", desc)
        self.assertIn("follow_up_prompt", desc)
        self.assertTrue(desc["requires_cure"])
        self.assertIn("Would you like", desc["follow_up_prompt"])
        print(f"  [PASS] Gemini Pro Description: '{desc['description'][:60]}...'")
        print(f"  [PASS] Gemini Pro Cure Prompt: '{desc['follow_up_prompt']}'")

    def test_04_gemini_on_demand_cure_plan(self):
        """Verify Gemini Pro prescribes cure plan with dosages and recovery chance %"""
        cure = gemini_advisor.generate_cure_plan(
            disease_name="Tomato Early Blight",
            crop="Tomato",
            growth_stage="Flowering"
        )
        self.assertIn("recovery_chance_pct", cure)
        self.assertIn("recovery_timeline", cure)
        self.assertIn("organic_treatment", cure)
        self.assertIn("chemical_treatment", cure)
        self.assertGreaterEqual(cure["recovery_chance_pct"], 60.0)
        print(f"  [PASS] Gemini Pro Cure Plan: {cure['recovery_chance_pct']}% recovery, timeline: {cure['recovery_timeline']}")

    def test_05_cli_describe_and_cure_flags(self):
        """Verify CLI with --describe and --cure flags"""
        # Test 1: --describe
        cmd1 = [sys.executable, "predict.py", "--image", self.test_image_path, "--describe"]
        res1 = subprocess.run(cmd1, cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(res1.returncode, 0)
        self.assertIn("disease_description", res1.stdout)
        self.assertIn("follow_up_prompt", res1.stdout)
        print("  [PASS] CLI 'predict.py --image <path> --describe' returned description and cure prompt.")

        # Test 2: --cure
        cmd2 = [sys.executable, "predict.py", "--image", self.test_image_path, "--cure"]
        res2 = subprocess.run(cmd2, cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(res2.returncode, 0)
        self.assertIn("cure_plan", res2.stdout)
        print("  [PASS] CLI 'predict.py --image <path> --cure' returned complete cure plan.")

    def test_06_database_persistence_sqlite(self):
        """Verify SQLite persists disease detection, description, and cure prompt"""
        db = SessionLocal()
        try:
            record = DiseasePrediction(
                image_filename="test_gemini_leaf.jpg",
                predicted_class="Tomato Early Blight",
                confidence=0.93,
                is_healthy=False,
                severity="Medium",
                disease_description="Early Blight caused by Alternaria solani.",
                cure_prompt="Would you like a step-by-step cure and treatment plan for Tomato Early Blight?",
                recovery_chance_pct=88.0,
                recovery_timeline="5–7 days"
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            self.assertIsNotNone(record.id)

            retrieved = db.query(DiseasePrediction).filter(DiseasePrediction.id == record.id).first()
            self.assertEqual(retrieved.predicted_class, "Tomato Early Blight")
            self.assertIn("Alternaria", retrieved.disease_description)
            print(f"  [PASS] SQLite persisted diagnosis record #{record.id} with Gemini cure prompt.")
        finally:
            db.close()

    def test_07_service_layer_coordination(self):
        """Verify DiseaseService orchestrates CV Model + Gemini Pro + Database"""
        db = SessionLocal()
        try:
            with open(self.test_image_path, "rb") as f:
                content = f.read()

            res = disease_service.process_uploaded_image(
                file_bytes=content,
                original_filename="uploaded_leaf.jpg",
                include_cure=False,
                db=db
            )
            self.assertIn("predicted_class", res)
            self.assertIn("disease_description", res)
            self.assertIsNone(res["cure_plan"])  # None because include_cure=False
            self.assertIn("follow_up_prompt", res["disease_description"])
            self.assertIsNotNone(res["saved_record_id"])
            print(f"  [PASS] DiseaseService flow: Detection -> Gemini Description -> Prompt (Cure on-demand)")
        finally:
            db.close()


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVersion1GeminiProIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        sys.exit(1)
