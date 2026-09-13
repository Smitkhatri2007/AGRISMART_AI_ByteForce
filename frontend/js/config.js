// ==========================================================================
// AgriSmart AI - Global Configuration & Single Source of Truth
// ==========================================================================

const CONFIG = {
    // 14 Supported Crops matching backend class_catalog.py
    SUPPORTED_CROPS: [
        "Tomato", "Potato", "Corn (Maize)", "Apple", "Grape", 
        "Peach", "Bell Pepper", "Blueberry", "Cherry", "Soybean", 
        "Squash", "Strawberry", "Orange", "Raspberry"
    ],
    
    // Confidence Thresholds for the UI bars and uncertain state
    CONFIDENCE: {
        HIGH: 70,       // > 70% is Green
        MODERATE: 40,   // 40% - 70% is Amber
        UNCERTAIN: 60,  // < 60% shows the "uncertain diagnosis" disclaimer
        MIN_ALT: 2      // Minimum confidence to show in "Other Possibilities"
    },

    // Model & Data Transparency Metrics (Matches README)
    MODEL_METRICS: {
        MACRO_F1: "99.97% Validation Accuracy",
        ARCHITECTURE: "DenseNet-201 (Custom Classifier Head)",
        TRAIN_DATASET: "PlantVillage (38 Classes)",
        EVAL_DATASET: "Field-Condition Test Set",
        GITHUB_URL: "https://github.com/Smitkhatri2007/AGRISMART_AI_ByteForce"
    }
};

window.AGRI_CONFIG = CONFIG;
