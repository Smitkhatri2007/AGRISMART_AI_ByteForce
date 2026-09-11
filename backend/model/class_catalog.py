"""
AgriSmart AI - Crop Disease Class Catalog & Precaution Knowledge Base
Defines the official ~15-20 shared crop-disease classes across PlantVillage and PlantDoc,
with corresponding farmer-friendly precautions, symptoms, and organic/chemical remedies.
Ref: SIH 2026 Problem Statement 1, Page 3 (Section 4.1) & Page 4 (Section 5).
"""

CLASS_METADATA = {
    # ------------------ Tomato ------------------
    "Tomato Early Blight": {
        "crop": "Tomato",
        "disease_name": "Early Blight",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Remove affected lower leaves immediately. Avoid overhead sprinkler watering and mulch soil around plants to prevent soil-splash spores.",
        "organic_remedy": "Apply copper-based fungicides or neem oil spray every 7–10 days during warm, humid spells.",
        "chemical_remedy": "Apply Chlorothalonil or Mancozeb at the first appearance of concentric brown ring spots.",
        "regional_guidance": {
            "hi": "संक्रमित निचली पत्तियों को तुरंत हटा दें। फव्वारा सिंचाई से बचें और पौधों के चारों ओर गीली घास (मल्च) लगाएं।",
            "mr": "संसर्ग झालेली खालची पाने त्वरित काढून टाका. वरून पाणी देणे टाळा आणि तांब्याचा बुरशीनाशक फवारा."
        }
    },
    "Tomato Late Blight": {
        "crop": "Tomato",
        "disease_name": "Late Blight",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Destroy heavily infected plants to stop rapid community spread. Ensure wide plant spacing for aeration.",
        "organic_remedy": "Use copper hydroxide spray proactively before extended rainy periods.",
        "chemical_remedy": "Apply systemic fungicides containing Metalaxyl-M or Dimethomorph immediately.",
        "regional_guidance": {
            "hi": "गंभीर रूप से संक्रमित पौधों को नष्ट करें। हवा के प्रवाह के लिए पौधों के बीच दूरी बनाए रखें।",
            "mr": "तीव्र संसर्ग झालेली झाडे नष्ट करा. रोपांमध्ये पुरेशी हवा खेळती राहील याची काळजी घ्या."
        }
    },
    "Tomato Leaf Mould": {
        "crop": "Tomato",
        "disease_name": "Leaf Mold",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Reduce greenhouse and canopy humidity below 85%. Increase ventilation and drip irrigate.",
        "organic_remedy": "Bio-fungicides like Bacillus subtilis applied to leaf undersides.",
        "chemical_remedy": "Apply Difenoconazole or Azoxystrobin spray.",
        "regional_guidance": {
            "hi": "हवा में नमी को 85% से कम रखें। वेंटिलेशन बढ़ाएं और केवल ड्रिप सिंचाई का उपयोग करें।",
            "mr": "हवेतील ओलावा कमी ठेवा. वेंटिलेशन वाढवा आणि ठिबक सिंचनाचा वापर करा."
        }
    },
    "Tomato Bacterial Spot": {
        "crop": "Tomato",
        "disease_name": "Bacterial Spot",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Use certified disease-free seeds. Never handle plants when leaves are wet to prevent bacterial spread.",
        "organic_remedy": "Spray fixed copper mixed with Mancozeb for synergistic bacterial suppression.",
        "chemical_remedy": "Streptomycin sulfate + Tetracycline bactericide formulations where permitted.",
        "regional_guidance": {
            "hi": "प्रमाणित रोगमुक्त बीजों का उपयोग करें। गीले होने पर पौधों को न छुएं।",
            "mr": "प्रमाणित बियाणे वापरा. पाने ओली असताना झाडांना स्पर्श करू नका."
        }
    },
    "Tomato healthy": {
        "crop": "Tomato",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Maintain standard nutrient feeding schedule and routine scouting for early signs of pests.",
        "organic_remedy": "Routine preventative neem oil spraying once a month.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "फसल स्वस्थ है। नियमित पोषण और निगरानी बनाए रखें।",
            "mr": "पीक निरोगी आहे. नियमित पोषण आणि देखरेख ठेवा."
        }
    },

    # ------------------ Potato ------------------
    "Potato Early Blight": {
        "crop": "Potato",
        "disease_name": "Early Blight",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Practice at least a 2-year crop rotation away from solanaceous crops. Maintain balanced nitrogen fertilization.",
        "organic_remedy": "Trichoderma viride bio-agent soil treatment and foliar spray.",
        "chemical_remedy": "Foliar application of Mancozeb (2.5g/L) or Propineb.",
        "regional_guidance": {
            "hi": "कम से कम 2 साल का फसल चक्र अपनाएं। संतुलित नाइट्रोजन खाद का प्रयोग करें।",
            "mr": "किमान २ वर्षांचे पीक फेरपालट करा. संतुलित खतांचा वापर करा."
        }
    },
    "Potato Late Blight": {
        "crop": "Potato",
        "disease_name": "Late Blight",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Kill potato haulms 10–14 days before harvest to prevent tuber rot. Store seed tubers in cool, dry conditions.",
        "organic_remedy": "Prophylactic spray of Bordeaux mixture (1%) before cool cloudy weather sets in.",
        "chemical_remedy": "Apply Cymoxanil + Mancozeb or Fenamidone + Mancozeb upon disease alert.",
        "regional_guidance": {
            "hi": "कटाई से 10 दिन पहले बेल काट दें ताकि कंदों तक बीमारी न पहुंचे।",
            "mr": "बटाटा काढणीपूर्वी १० दिवस फांद्या कापून टाका जेणेकरून कंदांना संसर्ग होणार नाही."
        }
    },
    "Potato healthy": {
        "crop": "Potato",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Continue regular earthing-up and balanced irrigation during tuber expansion.",
        "organic_remedy": "Foliar spray of vermiwash or seaweed extract for plant vitality.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "आलू की फसल स्वस्थ है। कंद बनने के समय पर्याप्त नमी बनाए रखें।",
            "mr": "बटाटा पीक निरोगी आहे. कंद वाढीच्या काळात योग्य पाणी द्या."
        }
    },

    # ------------------ Corn (Maize) ------------------
    "Corn Common Rust": {
        "crop": "Corn",
        "disease_name": "Common Rust",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Plant rust-resistant hybrid varieties. Plant early to avoid high humidity cycles.",
        "organic_remedy": "Sulfur-based dusts or wettable sulfur applications.",
        "chemical_remedy": "Apply Azoxystrobin + Difenoconazole or Propiconazole if pustules reach upper canopy.",
        "regional_guidance": {
            "hi": "रोग प्रतिरोधी किस्मों की बुआई करें। संक्रमण दिखने पर प्रोपिकोनाजोल का छिड़काव करें।",
            "mr": "रोगप्रतिकारक वाणांची लागवड करा. बुरशीचा प्रादुर्भाव वाढल्यास बुरशीनाशक फवारा."
        }
    },
    "Corn Grey Leaf Spot": {
        "crop": "Corn",
        "disease_name": "Grey Leaf Spot",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Incorporate crop debris deeply into soil after harvest to bury overwintering fungal mycelium.",
        "organic_remedy": "Crop rotation with non-host crops such as Soybean or Pulses.",
        "chemical_remedy": "Apply Pyraclostrobin or Tebuconazole before tasseling stage.",
        "regional_guidance": {
            "hi": "कटाई के बाद अवशेषों को जमीन में गहराई से दबाएं और दलहनी फसलों के साथ फसल चक्र अपनाएं।",
            "mr": "कापणीनंतर पिकाचे अवशेष जमिनीत खोल गाडा आणि कडधान्यांसोबत फेरपालट करा."
        }
    },
    "Corn healthy": {
        "crop": "Corn",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Keep fields free from weeds to maximize sunlight penetration and airflow.",
        "organic_remedy": "Maintain soil organic carbon with compost.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "मक्का की फसल पूर्णतः स्वस्थ है। नियमित पोषण जारी रखें।",
            "mr": "मका पीक उत्तम स्थितीत आहे. नियमित खत व्यवस्थापन ठेवा."
        }
    },

    # ------------------ Apple ------------------
    "Apple Scab": {
        "crop": "Apple",
        "disease_name": "Apple Scab",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Rake and compost or shred fallen leaves in autumn to eliminate primary spore reservoirs.",
        "organic_remedy": "Lime sulfur spray at green-tip stage.",
        "chemical_remedy": "Apply Captan, Myclobutanil, or Dodine at pink bud and petal fall stages.",
        "regional_guidance": {
            "hi": "पतझड़ में गिरी पत्तियों को नष्ट करें। कली खिलने के समय कैप्टन का छिड़काव करें।",
            "mr": "झाडावरून पडलेली पाने गोळा करून नष्ट करा."
        }
    },
    "Apple Black Rot": {
        "crop": "Apple",
        "disease_name": "Black Rot",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Prune out dead wood, mummified fruits, and infected cankers during dormant winter season.",
        "organic_remedy": "Copper soap fungicide spray during delayed dormant phase.",
        "chemical_remedy": "Apply Thiophanate-methyl or Captan starting from petal fall through harvest.",
        "regional_guidance": {
            "hi": "सड़े हुए फलों और सूखी टहनियों को काटकर हटा दें।",
            "mr": "वाळलेल्या फांद्या आणि सडलेली फळे छाटून नष्ट करा."
        }
    },
    "Apple healthy": {
        "crop": "Apple",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Maintain annual canopy pruning for sunlight penetration and fruit thinning.",
        "organic_remedy": "Regular compost mulching around tree basins.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "सेब के पौधे स्वस्थ हैं।",
            "mr": "सफरचंदाचे झाड निरोगी आहे."
        }
    },

    # ------------------ Grape ------------------
    "Grape Black Rot": {
        "crop": "Grape",
        "disease_name": "Black Rot",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Remove all mummified berries from vines and ground. Prune vines to improve canopy air circulation.",
        "organic_remedy": "Bordeaux mixture spray during pre-bloom stage.",
        "chemical_remedy": "Apply Myclobutanil or Mancozeb every 10–14 days from early shoot development.",
        "regional_guidance": {
            "hi": "काले सूखे अंगूरों को बेल से हटा दें। वायु प्रवाह के लिए छंटाई करें।",
            "mr": "वाळलेली द्राक्षे वेलीवरून काढून टाका आणि वेलींची छाटणी करा."
        }
    },
    "Grape healthy": {
        "crop": "Grape",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Maintain wire trellis management and balanced potash application for berry sweetness.",
        "organic_remedy": "Neem cake soil application.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "अंगूर की बेल स्वस्थ है।",
            "mr": "द्राक्ष वेल निरोगी आहे."
        }
    },

    # ------------------ Bell Pepper ------------------
    "Bell Pepper Bacterial Spot": {
        "crop": "Bell Pepper",
        "disease_name": "Bacterial Spot",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Avoid working in the field when plants are damp. Rotate crops with non-solanaceous crops.",
        "organic_remedy": "Copper sulfate pentahydrate spray.",
        "chemical_remedy": "Copper hydroxide mixed with Mancozeb for preventive control.",
        "regional_guidance": {
            "hi": "शिमला मिर्च की फसल पर जीवाणु धब्बा। तांबा युक्त कवकनाशी का छिड़काव करें।",
            "mr": "शिमला मिरचीवरील जिवाणूजन्य ठिपके रोखण्यासाठी तांब्याची फवारणी करा."
        }
    },
    "Bell Pepper healthy": {
        "crop": "Bell Pepper",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Keep adequate spacing between beds and monitor for aphid and thrip vectors.",
        "organic_remedy": "Yellow sticky traps for preventive vector scouting.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "शिमला मिर्च की फसल स्वस्थ है।",
            "mr": "शिमला मिरची पीक निरोगी आहे."
        }
    }
}

# The complete list of shared classes
ALL_CLASSES = list(CLASS_METADATA.keys())
