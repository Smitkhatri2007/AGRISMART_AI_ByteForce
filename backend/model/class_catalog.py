"""
AgriSmart AI - Crop Disease Class Catalog & Precaution Knowledge Base
Defines all 38 official PlantVillage disease & healthy classes across 14 crops,
complete with farmer-friendly precautions, symptoms, organic/chemical remedies,
and regional language guidance (Hindi & Marathi).
Ref: SIH 2026 Problem Statement 1 & PlantVillage 38-Class Dataset.
"""

CLASS_METADATA = {
    # =========================================================================
    # 1. TOMATO (10 Classes)
    # =========================================================================
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
    "Tomato Septoria Leaf Spot": {
        "crop": "Tomato",
        "disease_name": "Septoria Leaf Spot",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Remove lower infected foliage. Avoid overhead irrigation and sanitize garden stakes after harvest.",
        "organic_remedy": "Copper soap fungicide applications every 7–10 days during rainy conditions.",
        "chemical_remedy": "Apply Chlorothalonil or Mancozeb at the first sign of circular spots with dark margins.",
        "regional_guidance": {
            "hi": "पत्तियों पर छोटे गोल काले धब्बे। निचली पत्तियों को हटाएं और क्लोरोथैलोनिल का छिड़काव करें।",
            "mr": "पानांवरील लहान गोलाकार डाग दिसताच खालची पाने काढा आणि बुरशीनाशक फवारा."
        }
    },
    "Tomato Two-Spotted Spider Mite": {
        "crop": "Tomato",
        "disease_name": "Two-Spotted Spider Mite",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Mist canopy during hot dry spells to deter mites. Introduce beneficial predatory mites (Phytoseiulus persimilis).",
        "organic_remedy": "Spray neem oil or insecticidal potassium soap thoroughly on leaf undersides.",
        "chemical_remedy": "Apply Abamectin or Spiromesifen miticide at high pressure.",
        "regional_guidance": {
            "hi": "सूखे मौसम में पत्तों के नीचे जाले और पीले धब्बे। नीम का तेल या एबामेक्टिन छिड़कें।",
            "mr": "पानांच्या मागच्या बाजूला जाळे दिसल्यास नीम तेल किंवा कीटकनाशक फवारा."
        }
    },
    "Tomato Target Spot": {
        "crop": "Tomato",
        "disease_name": "Target Spot",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Improve airflow by pruning suckers and avoid excessive nitrogen fertilization.",
        "organic_remedy": "Apply Bacillus amyloliquefaciens bio-fungicide.",
        "chemical_remedy": "Apply Boscalid or Azoxystrobin spray formulations.",
        "regional_guidance": {
            "hi": "पत्तियों पर गोलाकार रिंग जैसे टारगेट स्पॉट। एज़ोक्सीस्ट्रोबिन का छिड़काव करें।",
            "mr": "पानांवर गोलाकार निशाणे दिसल्यास बुरशीनाशकाची फवारणी करा."
        }
    },
    "Tomato Yellow Leaf Curl Virus": {
        "crop": "Tomato",
        "disease_name": "Yellow Leaf Curl Virus",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Install 50-mesh insect screens to exclude whiteflies. Remove and destroy stunted virus-infected plants.",
        "organic_remedy": "Deploy yellow sticky traps and spray neem oil to manage whitefly vectors.",
        "chemical_remedy": "Apply Imidacloprid or Acetamiprid to suppress vector populations.",
        "regional_guidance": {
            "hi": "सफेद मक्खी द्वारा फैलाया जाने वाला वायरस। पत्तियां मुड़कर पीली पड़ जाती हैं। सफेद मक्खी को नियंत्रित करें।",
            "mr": "पांढऱ्या माशीमुळे हा रोग पसरतो. पाने आकसून पिवळी पडतात. कीटक नियंत्रण करा."
        }
    },
    "Tomato Mosaic Virus": {
        "crop": "Tomato",
        "disease_name": "Mosaic Virus",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Disinfect tools in 20% non-fat milk solution. Wash hands thoroughly and avoid smoking near plants.",
        "organic_remedy": "No cure once infected; immediately rouge and burn infected plants to protect field.",
        "chemical_remedy": "None available for viral infections. Plant resistant hybrid seeds.",
        "regional_guidance": {
            "hi": "मोज़ेक वायरस लाइलाज है। संक्रमित पौधों को तुरंत उखाड़कर जला दें।",
            "mr": "विषाणूजन्य रोग असल्याने संसर्ग झालेली रोपे त्वरित उपटून नष्ट करा."
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

    # =========================================================================
    # 2. POTATO (3 Classes)
    # =========================================================================
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

    # =========================================================================
    # 3. CORN / MAIZE (4 Classes)
    # =========================================================================
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
    "Corn Northern Leaf Blight": {
        "crop": "Corn",
        "disease_name": "Northern Leaf Blight",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Plant resistant corn hybrids and avoid continuous corn monoculture.",
        "organic_remedy": "Foliar application of Trichoderma harzianum culture.",
        "chemical_remedy": "Apply Azoxystrobin + Propiconazole or Mancozeb at early tassel stage.",
        "regional_guidance": {
            "hi": "सिगार के आकार के बड़े भूरे धब्बे। फसल चक्र अपनाएं और प्रोपिकोनाजोल का छिड़काव करें।",
            "mr": "पानांवर लांबट तपकिरी डाग पडल्यास प्रोपिकोनाझोल बुरशीनाशकाची फवारणी करा."
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

    # =========================================================================
    # 4. APPLE (4 Classes)
    # =========================================================================
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
    "Apple Cedar Rust": {
        "crop": "Apple",
        "disease_name": "Cedar Apple Rust",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Remove nearby cedar/juniper galls within 1 mile of the apple orchard.",
        "organic_remedy": "Sulfur-based fungicides applied before early spring rains.",
        "chemical_remedy": "Apply Myclobutanil or Mancozeb from pink bud until petal fall.",
        "regional_guidance": {
            "hi": "पत्तियों पर चमकीले पीले-नारंगी धब्बे। मायक्लोबुटानिल का छिड़काव करें।",
            "mr": "पानांवर नारंगी रंगाचे डाग दिसल्यास बुरशीनाशक फवारा."
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

    # =========================================================================
    # 5. GRAPE (4 Classes)
    # =========================================================================
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
    "Grape Black Measles (Esca)": {
        "crop": "Grape",
        "disease_name": "Black Measles (Esca)",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Disinfect pruning shears between vine cuts and seal large pruning wounds with protective paint.",
        "organic_remedy": "Apply Trichoderma-based bio-protectants immediately to pruning cuts.",
        "chemical_remedy": "Prune back symptomatic cordons to healthy wood; no systemic curative chemical exists.",
        "regional_guidance": {
            "hi": "छांटाई के औजारों को रोगाणुरहित करें और बड़े घावों पर लेप लगाएं।",
            "mr": "छाटणीच्या अवजारांचे निर्जंतुकीकरण करा आणि छाटलेल्या भागावर बुरशीनाशक लावा."
        }
    },
    "Grape Leaf Blight": {
        "crop": "Grape",
        "disease_name": "Leaf Blight",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Manage canopy foliage to eliminate dense shaded pockets where moisture lingers.",
        "organic_remedy": "Apply copper oxychloride (2.5g/L) during warm humid periods.",
        "chemical_remedy": "Apply Difenoconazole or Mancozeb foliar spray.",
        "regional_guidance": {
            "hi": "पत्तियों पर बड़े अनियमित भूरे धब्बे। कॉपर ऑक्सीक्लोराइड का छिड़काव करें।",
            "mr": "पानांवरील करपा नियंत्रणासाठी कॉपर बुरशीनाशकाची फवारणी करा."
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

    # =========================================================================
    # 6. BELL PEPPER (2 Classes)
    # =========================================================================
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
    },

    # =========================================================================
    # 7. CHERRY (2 Classes)
    # =========================================================================
    "Cherry Powdery Mildew": {
        "crop": "Cherry",
        "disease_name": "Powdery Mildew",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Prune during dormant season to ensure canopy sunlight penetration and airflow.",
        "organic_remedy": "Potassium bicarbonate or wettable sulfur applied in early season.",
        "chemical_remedy": "Apply Myclobutanil or Quinoxyfen at shuck fall stage.",
        "regional_guidance": {
            "hi": "चेरी की पत्तियों पर सफेद फफूंद। पोटेशियम बाइकार्बोनेट का छिड़काव करें।",
            "mr": "पानांवर पांढरी बुरशी दिसल्यास पोटॅशियम बायकार्बोनेट फवारा."
        }
    },
    "Cherry healthy": {
        "crop": "Cherry",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Maintain balanced moisture during fruit development to prevent fruit splitting.",
        "organic_remedy": "Neem oil spray once a month.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "चेरी का पेड़ पूर्णतः स्वस्थ है।",
            "mr": "चेरीचे झाड निरोगी आहे."
        }
    },

    # =========================================================================
    # 8. PEACH (2 Classes)
    # =========================================================================
    "Peach Bacterial Spot": {
        "crop": "Peach",
        "disease_name": "Bacterial Spot",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Avoid planting in light sandy soils without windbreaks to minimize wind abrasion.",
        "organic_remedy": "Copper soap spray during dormant period.",
        "chemical_remedy": "Apply Oxytetracycline bactericide during petal fall through shuck split.",
        "regional_guidance": {
            "hi": "आड़ू की पत्तियों और फल पर जीवाणु धब्बा। कॉपर स्प्रे का प्रयोग करें।",
            "mr": "जिवाणूजन्य डाग नियंत्रणासाठी तांब्याची फवारणी करा."
        }
    },
    "Peach healthy": {
        "crop": "Peach",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Conduct regular winter pruning and thin fruit sets for optimal sizing.",
        "organic_remedy": "Mulch tree root zone with organic matter.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "आड़ू का पेड़ स्वस्थ है।",
            "mr": "झाड उत्तम स्थितीत आहे."
        }
    },

    # =========================================================================
    # 9. STRAWBERRY (2 Classes)
    # =========================================================================
    "Strawberry Leaf Scorch": {
        "crop": "Strawberry",
        "disease_name": "Leaf Scorch",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Remove dead foliage in autumn and avoid overhead sprinkler watering.",
        "organic_remedy": "Copper-based spray before blossom opening.",
        "chemical_remedy": "Apply Captan or Thiophanate-methyl early in spring.",
        "regional_guidance": {
            "hi": "स्ट्रॉबेरी की पत्तियों पर बैंगनी-काले धब्बे। पुरानी पत्तियां हटाएं और कैप्टन का छिड़काव करें।",
            "mr": "पानांवर जांभळे डाग दिसल्यास कॅप्टन बुरशीनाशक फवारा."
        }
    },
    "Strawberry healthy": {
        "crop": "Strawberry",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Keep dry straw mulch underneath plants to elevate berries above damp soil.",
        "organic_remedy": "Preventative neem oil spray.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "स्ट्रॉबेरी की फसल स्वस्थ है।",
            "mr": "स्ट्रॉबेरी पीक निरोगी आहे."
        }
    },

    # =========================================================================
    # 10. BLUEBERRY (1 Class)
    # =========================================================================
    "Blueberry healthy": {
        "crop": "Blueberry",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Maintain acidic soil pH (4.5–5.2) with pine bark mulching and regular drip irrigation.",
        "organic_remedy": "Organic compost and seaweed extract soil conditioning.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "ब्लूबेरी की फसल पूर्णतः स्वस्थ है। मिट्टी का पीएच 4.5 से 5.2 के बीच रखें।",
            "mr": "ब्लूबेरी पीक उत्तम स्थितीत आहे. मातीचा सामू आम्लधर्मी ठेवा."
        }
    },

    # =========================================================================
    # 11. ORANGE / CITRUS (1 Class)
    # =========================================================================
    "Orange Citrus Greening": {
        "crop": "Orange",
        "disease_name": "Citrus Greening (Huanglongbing)",
        "is_healthy": False,
        "severity": "High",
        "precaution": "Scout aggressively for Asian citrus psyllid vectors and remove heavily infected non-productive trees.",
        "organic_remedy": "Horticultural mineral oils to disrupt psyllid insect feeding.",
        "chemical_remedy": "Apply Imidacloprid or Thiamethoxam for psyllid vector control; foliar micronutrient blend.",
        "regional_guidance": {
            "hi": "सिट्रस ग्रीनिंग बीमारी। पत्तियां पीली और फल खट्टे-कड़वे। कीड़ों के नियंत्रण के लिए इमिडाक्लोप्रिड छिड़कें।",
            "mr": "संत्र्यावरील सिट्रस ग्रीनिंग रोखण्यासाठी मावा व तुडतुड्यांचे नियंत्रण करा."
        }
    },

    # =========================================================================
    # 12. RASPBERRY (1 Class)
    # =========================================================================
    "Raspberry healthy": {
        "crop": "Raspberry",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Prune spent floricanes immediately after fruiting to promote healthy primocane emergence.",
        "organic_remedy": "Annual organic compost top-dressing.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "रास्पबेरी की फसल स्वस्थ है। कटाई के बाद पुरानी शाखाओं की छंटाई करें।",
            "mr": "रास्पबेरी पीक निरोगी आहे. फळ काढणीनंतर जुन्या फांद्या छाटून टाका."
        }
    },

    # =========================================================================
    # 13. SOYBEAN (1 Class)
    # =========================================================================
    "Soybean healthy": {
        "crop": "Soybean",
        "disease_name": "Healthy",
        "is_healthy": True,
        "severity": "None",
        "precaution": "Maintain balanced potassium fertilization and practice rotational tillage.",
        "organic_remedy": "Seed inoculation with Rhizobium japonicum before planting.",
        "chemical_remedy": "None required.",
        "regional_guidance": {
            "hi": "सोयाबीन की फसल पूर्णतः स्वस्थ है। संतुलित पोटाश खाद बनाए रखें।",
            "mr": "सोयाबीन पीक उत्तम स्थितीत आहे. संतुलित खत व्यवस्थापन ठेवा."
        }
    },

    # =========================================================================
    # 14. SQUASH (1 Class)
    # =========================================================================
    "Squash Powdery Mildew": {
        "crop": "Squash",
        "disease_name": "Powdery Mildew",
        "is_healthy": False,
        "severity": "Medium",
        "precaution": "Plant resistant squash cultivars and space rows widely for maximum wind ventilation.",
        "organic_remedy": "Foliar spray of baking soda (5g/L) mixed with horticultural soap.",
        "chemical_remedy": "Apply Myclobutanil or Trifloxystrobin at the first sign of powdery talc spots.",
        "regional_guidance": {
            "hi": "कद्दू/लौकी वर्गीय पत्तियों पर सफेद पाउडर। बेकिंग सोडा या कवकनाशी का छिड़काव करें।",
            "mr": "पानांवरील पांढऱ्या बुरशीसाठी बेकिंग सोडा किंवा बुरशीनाशक फवारा."
        }
    }
}

# The complete list of 38 PlantVillage classes across 14 crops
ALL_CLASSES = list(CLASS_METADATA.keys())
