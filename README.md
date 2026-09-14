# AgriSmart AI - Intelligent Agriculture for a Sustainable Future

AgriSmart AI is an end-to-end precision agritech platform combining edge-optimized computer vision, hyper-local meteorological intelligence, autonomous decision-making, and conversational generative AI for smallholder farmers and commercial growers.

---

## 1. Modules Built

### 🌿 Core Task: Crop Disease Detection (Computer Vision)
- **Model**: Custom fine-tuned PyTorch **ResNet-18** CNN classifier.
- **Classes**: 38 plant disease and healthy crop categories spanning Tomato, Potato, Corn, Apple, Grape, Pepper, Strawberry, and more.
- **Accuracy**: 98.4% local validation accuracy; handles single-leaf, multi-leaf, grayscale, and transparent RGBA formats.
- **Offline Fallback**: Seamless client-side color-histogram and edge-gradient heuristics guarantee 100% operational uptime in remote fields without connectivity.

### 🤖 Module E & AgriBot: Conversational Web AI Agronomist
- **Online Intelligence**: Powered by **Groq** (`llama-3.3-70b-versatile`) with sub-second inference speeds. Converses naturally about general farming, crop health, organic recipes, safe spray windows, and personalized disease treatment in English, Hindi, and Gujarati.
- **Deterministic Local Dialogue Engine**: Functions fully offline without an API key or internet connection. Classifies farmer intent (greetings, identity, neem spray preparation, soil fertility, drip guidelines, chemical safety, recovery tracking) and delivers structured, agronomist-grade answers.
- **Dynamic Quick Chips**: Context-aware suggested queries before and after leaf diagnosis.
- **Enterprise Security**: Sanitized against DOM XSS attacks and script injection.

### 🌾 Module A: Crop Recommendation Engine
- **Agronomic Grounding**: Formulated according to **ICAR** (Indian Council of Agricultural Research) & **FAO** agro-ecological guidelines.
- **Parameters**: Evaluates soil texture (Loamy, Clay, Sandy, Alluvial, Black, Red), pH, seasonal temperature, rainfall forecast, and previous crop rotation history.
- **Safety Gates**: Enforces biological viability gates (pH < 4.0 or > 9.5; temperatures < 5°C or > 48°C) to prevent catastrophic crop failure and prescribes precise soil conditioning (lime or gypsum amendments).
- **Rotation Economics**: Incentivizes nitrogen-fixing legumes (Rhizobium) and penalizes monoculture cycles to eliminate pathogen buildup.

### 💧 Module B: Smart Irrigation Advisor
- **Scientific Foundation**: FAO-56 Evapotranspiration & Management Allowed Depletion (MAD) models.
- **Soil Factoring**: Dynamically adjusts runtime and water volumes for Sandy (rapid drainage), Loamy (balanced), and Clay (high retention) soils.
- **Drought Priority Protection**: Evaluates near-wilting soil moisture (≤ 60% of critical depletion threshold) to prescribe emergency short cycles (2.5 L/m²), preventing permanent crop collapse even when rain is forecast.

### 🌦️ Module C: Hyper-local Weather Intelligence
- **Open-Meteo Integration**: Real-time GPS-based weather analytics with 24-hour and 7-day precipitation forecasts, wind speeds, and relative humidity.
- **Rain-Delay Irrigation Alert**: Automatically signals irrigation holds when natural rainfall (> 4.0 mm, ≥ 40% probability) will replenish the crop root zone, conserving vital groundwater.

### 🌱 Module D: Farm Sustainability & Resource Conservation Index
- **Transparent Reproducible Formula**:
  $$\text{Sustainability Score } (S) = (0.35 \times H) + (0.35 \times W) + (0.30 \times O) - P_{\text{chem}}$$
  - $H$: Crop Health Index (0–100, mapped across None/Healthy, Low, Medium, High, and Critical severity).
  - $W$: Water Efficiency Index (0–100, factoring smart rain delays).
  - $O$: Organic Stewardship Index (0–100, adoption of bio-agents like *Trichoderma* and cold-pressed neem).
  - $P_{\text{chem}}$: Chemical Runoff Penalty (0–20).
- **Impact Metrics**: Computes liters of groundwater conserved per acre cycle and chemical runoff reduction percentages.

### 💊 Module F: Chemical & Organic Dosage Precision Calculator
- **Dynamic Dilution Math**: Accurately computes active ingredient required for knapsack sprayers (15 L, 20 L) up to multi-acre tractor tanks.
- **Health-Aware Logic**: Zeroes chemical dosage when crops are diagnosed healthy, promoting preventative organic maintenance instead of unnecessary pesticide costs.
- **Safe Bounds**: Guarded against divide-by-zero, negative acreage, or null tank capacities.

### 🧠 Module G: Autonomous Agentic Decision Cycle
- **Multi-Signal Synthesis**: Synthesizes leaf pathology, 24-hour weather forecast, soil moisture, and crop phenology into a unified, actionable farm directive.

### 📲 Universal Multi-App Sharing
- **Native Web Share API**: Shares formatted diagnosis cards, dosages, and irrigation plans directly to WhatsApp, Telegram, Gmail, SMS, or any native mobile/desktop app, with automatic clipboard copy fallback.

---

## 2. Setup and Run Instructions

### Prerequisites
- Python 3.10+
- Node.js (Optional, for running standalone JS test suites)
- A valid [Groq API Key](https://console.groq.com/keys) *(Optional: the platform includes a full offline conversational engine that works without any API keys)*

### Automated Setup (Windows)
1. Clone the repository and enter the directory:
   ```bash
   git clone https://github.com/Smitkhatri2007/AGRISMART_AI_ByteForce.git
   cd AGRISMART_AI_ByteForce
   ```
2. Double click **`run.bat`** (or execute `.\run.bat` from terminal).
   - This creates a virtual environment, installs backend dependencies, and initializes `backend/.env`.
3. *(Optional)* Add your `GROQ_API_KEY` in `backend/.env`.
4. Press any key to start the Uvicorn server, then open `http://localhost:8000` in your web browser.

### Manual Setup (Linux / macOS / Bash)
1. Navigate to the backend directory and set up Python virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Add your GROQ_API_KEY if available (optional)
   ```
3. Start the application:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Access the web interface at `http://localhost:8000`.

---

## 3. Running CLI Prediction
You can classify an image directly from the command line:
```bash
cd backend
python predict.py --image path/to/leaf.jpg
```
*Outputs strictly the predicted class label string.*

---

## 4. Dataset & License
- **Dataset**: New Plant Diseases Dataset (Augmented), derived from PlantVillage and PlantDoc.
- **License**: Open Source / Public Domain (Kaggle).

---

## 5. Reported Metrics & Architecture
- **Model Backbone**: ResNet-18 (Custom Linear Classification Head)
- **Validation Accuracy**: 98.4%
- **Architecture**: PyTorch CNN core with TorchScript serialization support $\rightarrow$ FastAPI asynchronous backend $\rightarrow$ Responsive Vanilla HTML5/CSS3/ES6 frontend.
- **Limitations**: The model may experience reduced confidence on images with extreme overexposure, severe leaf occlusion, or crops outside the trained 38 classes. Please refer to `/report/report.md` for per-class confusion matrices and error analyses.
