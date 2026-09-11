"""
AgriSmart AI - Version 1.0 Dual Model Test Suite
Verifies:
1. Model 1 (Disease Detection) - Submission contract CLI & Python callable
2. Model 2 (Cureness & Treatment) - Direct and chained cureness prescriptions
3. Detailed inference metadata with confidence & recovery chance %
4. Disease Catalog & Precaution Knowledge Base
5. Database ORM Table Creation & Dual Model Persistence in SQLite
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

from model.predict import predict, predict_cure
from model.disease_model import disease_model
from model.cure_model import cure_model
from model.fake_engine import default_engine
from model.class_catalog import ALL_CLASSES, CLASS_METADATA
from app.database import init_db, SessionLocal
from app.models.diagnosis import DiseasePrediction
from app.services.disease_service import disease_service


class TestVersion1DualModelContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test leaf image
        cls.test_image_path = os.path.join(ROOT_DIR, "test_leaf_synthetic.jpg")
        img = Image.new("RGB", (256, 256), color=(45, 120, 50))
        img.save(cls.test_image_path)

        # Initialize test database
        init_db()

    @classmethod
    def tearDownClass(cls):
        # Clean up test image
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)

    def test_01_model1_predict_python_callable_contract(self):
        """Verify Model 1: predict(image_path) -> class_label returns a valid shared class string"""
        label = predict(self.test_image_path)
        self.assertIsInstance(label, str)
        self.assertIn(label, ALL_CLASSES, f"Returned class '{label}' is not in the shared class list!")
        print(f"  [PASS] Model 1 Python callable returned: '{label}'")

    def test_02_model1_predict_cli_contracts(self):
        """Verify CLI execution: python model/predict.py --image <path> and root predict.py"""
        for script in ["model/predict.py", "predict.py"]:
            cmd = [sys.executable, script, "--image", self.test_image_path]
            result = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"CLI {script} failed: {result.stderr}")
            output = result.stdout.strip()
            self.assertIn(output, ALL_CLASSES)
            print(f"  [PASS] CLI {script} printed: '{output}'")

    def test_03_model2_cureness_model_standalone(self):
        """Verify Model 2: Prescribes cureness plan, recovery timeline, and dosage"""
        # Test for diseased crop
        cure_plan = predict_cure("Tomato Early Blight", crop="Tomato", stage="Vegetative")
        self.assertIn("cureness_score", cure_plan)
        self.assertIn("recovery_chance_pct", cure_plan)
        self.assertIn("recovery_timeline", cure_plan)
        self.assertIn("dosage_guide", cure_plan)
        self.assertGreater(cure_plan["recovery_chance_pct"], 50.0)
        self.assertEqual(cure_plan["model_type"], "Model_2_Cureness_Prescriber")
        print(f"  [PASS] Model 2 cureness for Early Blight: {cure_plan['recovery_chance_pct']}% chance, urgency: {cure_plan['urgency_level']}")

        # Test for healthy crop
        healthy_plan = predict_cure("Tomato healthy", crop="Tomato", stage="Fruiting")
        self.assertEqual(healthy_plan["recovery_chance_pct"], 100.0)
        self.assertEqual(healthy_plan["urgency_level"], "MAINTENANCE")
        print(f"  [PASS] Model 2 for healthy crop: 100% recovery chance, urgency: MAINTENANCE")

    def test_04_dual_model_chained_inference(self):
        """Verify Dual Model Orchestrator chains Model 1 detection -> Model 2 cureness"""
        full_res = default_engine.predict_detailed(self.test_image_path, growth_stage="Flowering")
        self.assertIn("predicted_class", full_res)
        self.assertIn("cureness_plan", full_res)
        self.assertIn("recovery_chance_pct", full_res)
        self.assertIn("urgency_level", full_res)
        print(f"  [PASS] Chained Dual Model detected '{full_res['predicted_class']}' with recovery plan: {full_res['recovery_chance_pct']}%")

    def test_05_cli_with_cure_flag(self):
        """Verify CLI with --cure and --cure-for flags"""
        # 1. Image + cure plan
        cmd = [sys.executable, "predict.py", "--image", self.test_image_path, "--cure"]
        res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("cureness_plan", res.stdout)
        print(f"  [PASS] CLI 'predict.py --image <path> --cure' output verified.")

        # 2. Direct cure query
        cmd2 = [sys.executable, "predict.py", "--cure-for", "Potato Late Blight"]
        res2 = subprocess.run(cmd2, cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(res2.returncode, 0)
        self.assertIn("recovery_chance_pct", res2.stdout)
        print(f"  [PASS] CLI 'predict.py --cure-for ...' output verified.")

    def test_06_database_persistence_dual_model_fields(self):
        """Verify SQLite database persists both Model 1 detection and Model 2 cureness metrics"""
        db = SessionLocal()
        try:
            record = DiseasePrediction(
                image_filename="test_leaf_dual.jpg",
                predicted_class="Tomato Early Blight",
                confidence=0.94,
                is_healthy=False,
                severity="Medium",
                recovery_chance_pct=88.0,
                recovery_timeline="5–7 days with standard intervention",
                urgency_level="MODERATE (Act within 3–5 days)",
                precaution="Remove affected leaves immediately.",
                organic_remedy="Neem oil spray @ 4ml/L",
                prognosis_summary="With prompt treatment, your Tomato has a 88% chance of full recovery."
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            self.assertIsNotNone(record.id)

            retrieved = db.query(DiseasePrediction).filter(DiseasePrediction.id == record.id).first()
            self.assertEqual(retrieved.recovery_chance_pct, 88.0)
            self.assertEqual(retrieved.urgency_level, "MODERATE (Act within 3–5 days)")
            print(f"  [PASS] Database persisted dual model record #{record.id} with {retrieved.recovery_chance_pct}% recovery chance")
        finally:
            db.close()

    def test_07_service_layer_dual_model_coordination(self):
        """Verify DiseaseService orchestrates Model 1 + Model 2 and logs to database"""
        db = SessionLocal()
        try:
            res = disease_service.process_file_path(self.test_image_path, db=db)
            self.assertIn("predicted_class", res)
            self.assertIn("cureness_plan", res)
            self.assertIsNotNone(res["saved_record_id"])
            print(f"  [PASS] DiseaseService logged complete dual-model diagnosis #{res['saved_record_id']}")
        finally:
            db.close()


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVersion1DualModelContract)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if not res.wasSuccessful():
        sys.exit(1)
