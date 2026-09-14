# JANI AI - AgriSmart Disease Detection

JANI AI is the crop disease detection engine for AgriSmart AI.

## Model

- Architecture: EfficientNet-B2
- Classes: 38
- Image validator: CLIP
- Input: Plant/leaf image
- Output: Disease class, confidence, plant score, disease information

## Test locally

From this directory:

python src\predict.py path\to\image.jpg

Example:

python src\predict.py D:\AgriSmart-AI\test_images\1.jpg

## Python integration

The main prediction function is available in:

src/predict.py

The model weights are:

model/best_model.pth

Class mapping:

model/classes.json

Disease information:

data/disease_info.json

## Important

Do not train or modify best_model.pth during frontend/backend integration.

The model is intended to be used as an inference component inside the AgriSmart backend.

## Output

The prediction pipeline returns:

- valid_plant
- prediction
- confidence
- plant_score
- non_plant_score
- disease_info
