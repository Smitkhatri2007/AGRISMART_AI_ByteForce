# AgriSmart AI - Intelligent Agriculture for a Sustainable Future

This repository contains the submission for **Problem Statement 1** of the SIH 2026 Internal Hackathon.

## 1. Modules Built
- **Core Task: Crop Disease Detection (Computer Vision)** - Implemented using a PyTorch ResNet-18 model to classify leaf images into 38 disease/crop classes.
- **Bonus Module E: Farmer Assistant (GenAI)** - Implemented using **Groq** (formerly Gemini Pro) to provide lightning-fast descriptions of the disease, its severity, and a conversational interface for generating comprehensive cure and recovery plans in multiple regional languages.

## 2. Setup and Run Instructions

### Prerequisites
- Python 3.10+
- A valid [Groq API Key](https://console.groq.com/keys) (Optional, but required for the AI Chatbot features)

### Installation
```bash
# 1. Clone the repository and enter the directory
git clone https://github.com/Smitkhatri2007/AGRISMART_AI_ByteForce.git
cd AGRISMART_AI_ByteForce

# 2. Install required dependencies
pip install -r requirements.txt

# 3. Configure Environment Variables
cp .env.example .env
# Edit .env and insert your GROQ_API_KEY
```

### Running the Core Predict CLI
As per Section 4.1, you can run the model directly from the command line on a new image:
```bash
python predict.py --image path/to/leaf.jpg
```
*This will output **only** the predicted class label string.*

### Running the Web Application (Backend + Frontend)
To run the full minimal interface (FastAPI + web UI) and interact with the GenAI features locally:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Then open `http://localhost:8000` in your web browser.

## 3. Dataset & License
- **Dataset:** New Plant Diseases Dataset (Augmented), derived from PlantVillage and PlantDoc.
- **License:** Open Source / Public Domain (Kaggle).

## 4. Reported Metrics
- **Model:** ResNet-18 (Custom Classifier Head)
- **Validation Accuracy (Local):** 98.4%
- **Macro-F1 (Held-out Test):** *To be computed by organizers on the held-out set.*
- **Confusion Matrix:** Please see the `/report/report.md` for a detailed breakdown of limitations and per-class performance insights.

## 5. Architecture & Limitations
- **Architecture:** The system utilizes a PyTorch CNN backbone with a custom linear head for image classification. It integrates with FastAPI for the web layer and uses the `groq` SDK to connect with Groq's high-speed LLMs for contextual disease advisory.
- **Limitations:** The model may experience reduced accuracy on images with extreme lighting variations, heavily occluded leaves, or crops with diseases outside the trained 38 classes. Please see `/report/report.md` for more details.

## 6. Live Deployment Links
- **Frontend App (Vercel):** [https://agrismartai-byteforce.vercel.app/](https://agrismartai-byteforce.vercel.app/)
- **Backend API (Render):** [https://agrismart-ai-byteforce.onrender.com](https://agrismart-ai-byteforce.onrender.com)