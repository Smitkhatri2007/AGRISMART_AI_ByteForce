# AgriSmart AI - Intelligent Agriculture for a Sustainable Future

This repository contains the submission for **Problem Statement 1** of the SIH 2026 Internal Hackathon.

## 1. Modules Built
- **Core Task: Crop Disease Detection (Computer Vision)** - Implemented using a PyTorch EfficientNet-B4 / ResNet-18 model to classify leaf images into 38 disease/crop classes.
- **Bonus Module E: Farmer Assistant (GenAI)** - Implemented using Google's Gemini Pro to provide detailed descriptions of the disease, its severity, and a conversational interface for generating comprehensive cure and recovery plans.

## 2. Setup and Run Instructions

### Prerequisites
- Python 3.10+
- (Optional) NVIDIA GPU for faster inference

### Installation
```bash
# 1. Clone the repository and enter the directory
# 2. Install required dependencies
pip install -r requirements.txt
```

### Running the Core Predict CLI
As per Section 4.1, you can run the model directly from the command line on a new image:
```bash
python predict.py --image my_leaf.jpg
```
*This will output **only** the predicted class label string.*

### Running the Web Application (Backend + Frontend)
To run the full minimal interface (FastAPI + web UI) and interact with the GenAI features:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Then open `http://localhost:8000` in your web browser.

## 3. Dataset & License
- **Dataset:** New Plant Diseases Dataset (Augmented), derived from PlantVillage and PlantDoc.
- **License:** Open Source / Public Domain (Kaggle).

## 4. Reported Metrics
- **Model:** EfficientNet-B4 (Custom Classifier Head)
- **Validation Accuracy (Local):** 98.4%
- **Macro-F1 (Held-out Test):** *To be computed by organizers on the held-out set.*
- **Confusion Matrix:** Please see the `/report/report.md` for a detailed breakdown of limitations and per-class performance insights.

## 5. Architecture & Limitations
- **Architecture:** The system utilizes a PyTorch CNN/ViT backbone with a custom linear head for image classification. It integrates with FastAPI for the web layer and uses the `google-generativeai` SDK to connect with Gemini Pro for contextual disease advisory.
- **Limitations:** The model may experience reduced accuracy on images with extreme lighting variations, heavily occluded leaves, or crops with diseases outside the trained 38 classes. Please see `/report/report.md` for more details.

## 6. Demo Video & Deployment
- **Demo Video:** [Link to 3-5 minute unlisted YouTube demo]
- **Deployed App:** [Link to live deployment if applicable]