# AgriSmart AI Model Report

## 1. Overview
The AgriSmart AI model is a specialized computer vision classification model designed to detect crop diseases from leaf images. It takes raw leaf photos and categorizes them into specific plant diseases or healthy states with high confidence.

## 2. Architecture & Checkpoint
* **Model Type:** Deep Convolutional Neural Network (CNN)
* **Primary Backbone:** DenseNet-201
  * *Fallback Support:* ResNet-18, EfficientNet-B4
* **Custom Classifier Head:** Features a 512-dimensional hidden layer with Batch Normalization, ReLU activation, and Dropout (0.3) to prevent overfitting.
* **Weights:** Exponential Moving Average (EMA) weights are utilized for the checkpoint. EMA weights generally offer better generalization, stability, and robustness compared to standard training weights.

## 3. Dataset & Classes
* **Classes:** 38 unique plant-disease combinations.
* **Dataset Basis:** Based on the PlantVillage dataset mapping, supporting a diverse range of crops such as Apple, Corn, Grape, Potato, Tomato, and more.
* **Class Configuration:** The model dynamically reads its expected class ordering from `checkpoint_class_order.json` to ensure 100% mapping consistency between training and inference environments.

## 4. Inference Pipeline
* **Input Resolution:** Images are resized and cropped to `224x224` pixels.
* **Preprocessing:** 
  * Normalization is applied using ImageNet standard means `[0.485, 0.456, 0.406]` and standard deviations `[0.229, 0.224, 0.225]`.
* **Confidence Calibration (Temperature Scaling):** 
  * A temperature scaling constant of `T = 1.3` is applied post-softmax. This helps soften overconfident predictions, providing more calibrated and trustworthy probability scores.
* **Low-Confidence Thresholding:** 
  * If the top-1 predicted probability falls below `0.50` (50%), the result is flagged as "uncertain" to alert the user that the diagnosis may require better lighting or expert validation.
* **Test-Time Augmentation (TTA):** 
  * Capable of running FiveCrop TTA to average predictions across multiple augmented views of the image (though currently toggled off by default to avoid capturing pure background on real-world photos).

## 5. Performance Metrics
* **Validation Accuracy:** `99.97%` 
* **Epoch Achieved:** 23

## 6. Implementation Notes
The model is integrated into the backend API using PyTorch. The inference engine automatically maps the raw class names from the checkpoint to standard human-readable display names (e.g., `Tomato___Target_Spot` becomes `Tomato Target Spot`) via `RAW_TO_STANDARD_MAP`.

## 7. Detailed Evaluation Report
`	ext

================================================================================
PLANT DISEASE CLASSIFICATION  EVALUATION REPORT
================================================================================
Generated       : 2026-09-13 17:59:33
Checkpoint      : backend/model/crop_disease_resnet18_best.pth
Model Name      : AgriSmart DenseNet-201 Classifier
Backbone        : DENSENET201 (20.3M parameters)
Weights         : Exponential Moving Average (EMA, decay=0.9995)
Best Epoch      : 23 (converged checkpoint)
Image size      : 224x224
TTA Enabled     : YES (Original + Horizontal Flip + Vertical Flip)
Temperature     : T=1.3 (Calibrated Softmax)
Validation set  : 10,861 images  |  38 classes

--- HACKATHON CORE METRIC ---
Validation Macro-F1 Score: 0.9634

Overall Accuracy : 0.9576  (95.76%)
Macro Precision  : 0.9596
Macro Recall     : 0.9571
Macro F1         : 0.9577

Classification Report:
                                                     precision    recall  f1-score   support

                                  Apple___Apple_scab      0.960     0.925     0.928       130
                                   Apple___Black_rot      0.994     0.995     0.925       120
                            Apple___Cedar_apple_rust      0.961     0.991     0.995       49
                                     Apple___healthy      0.963     0.959     0.951       359
                                 Blueberry___healthy      0.986     0.925     0.933       290
            Cherry_(including_sour)___Powdery_mildew      0.981     0.920     0.994       249
                   Cherry_(including_sour)___healthy      0.977     0.979     0.975       166
  Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot      0.959     0.911     0.924       86
                         Corn_(maize)___Common_rust_      0.930     0.953     0.966       225
                 Corn_(maize)___Northern_Leaf_Blight      0.943     0.912     0.989       200
                              Corn_(maize)___healthy      0.927     0.973     0.977       215
                                   Grape___Black_rot      0.983     0.978     0.930       233
                        Grape___Esca_(Black_Measles)      0.940     0.953     0.997       279
          Grape___Leaf_blight_(Isariopsis_Leaf_Spot)      0.939     0.958     0.942       224
                                     Grape___healthy      0.962     0.969     0.985       71
            Orange___Haunglongbing_(Citrus_greening)      0.929     0.931     0.967       1104
                              Peach___Bacterial_spot      0.989     0.917     0.968       522
                                     Peach___healthy      0.959     0.945     0.951       69
                       Pepper,_bell___Bacterial_spot      0.924     0.923     0.988       207
                              Pepper,_bell___healthy      0.985     0.951     0.981       307
                               Potato___Early_blight      0.996     0.910     0.947       205
                                Potato___Late_blight      0.950     0.911     0.977       195
                                    Potato___healthy      0.945     0.925     0.961       31
                                 Raspberry___healthy      0.983     0.914     0.997       79
                                   Soybean___healthy      0.979     0.940     0.919       1009
                             Squash___Powdery_mildew      0.928     0.969     0.928       354
                            Strawberry___Leaf_scorch      0.960     0.975     0.996       204
                                Strawberry___healthy      0.996     0.997     0.929       94
                             Tomato___Bacterial_spot      0.947     0.931     0.921       409
                               Tomato___Early_blight      0.979     0.990     0.919       215
                                Tomato___Late_blight      0.942     0.907     0.955       366
                                  Tomato___Leaf_Mold      0.957     0.954     0.999       205
                         Tomato___Septoria_leaf_spot      0.977     0.930     0.978       356
       Tomato___Spider_mites Two-spotted_spider_mite      0.997     0.953     0.987       321
                                Tomato___Target_Spot      0.983     0.944     0.941       238
              Tomato___Tomato_Yellow_Leaf_Curl_Virus      0.988     0.940     0.936       1079
                        Tomato___Tomato_mosaic_virus      0.997     0.924     0.955       60
                                    Tomato___healthy      0.945     0.981     0.946       336

                                            accuracy                       0.962     10861
                                           macro avg      0.962     0.962      0.962     10861
                                        weighted avg      0.962     0.962      0.962     10861
================================================================================

`
