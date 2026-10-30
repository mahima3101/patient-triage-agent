"""Medical Symptom Parser Tool.
Translates colloquial patient complaint narratives into standardized clinical terms (SNOMED-CT / ICD-10)
and detects vital emergency red-flag symptoms.
"""
import json
import re
from tools import Tool

# Standardized Clinical Mapping Dictionary
SYMPTOM_DICTIONARY = [
    {
        "patterns": [r"\bheadache\b", r"\bpounding head\b", r"\bhead throbbing\b", r"\btemple pain\b", r"\bmigraine\b"],
        "term": "Cephalea (Headache)",
        "icd10": "R51.9",
        "snomed": "25064002",
        "severity": "MODERATE",
        "red_flag": False
    },
    {
        "patterns": [r"\bworst headache of (?:my )?life\b", r"\bthunderclap\b", r"\bsudden severe headache\b"],
        "term": "Thunderclap Cephalea (Suspected Subarachnoid Hemorrhage)",
        "icd10": "G44.53",
        "snomed": "448937009",
        "severity": "CRITICAL",
        "red_flag": True
    },
    {
        "patterns": [r"\bdizz(?:y|iness)\b", r"\blightheaded\b", r"\bfeeling faint\b", r"\bpassed out\b", r"\broom spinning\b", r"\bvertigo\b"],
        "term": "Presyncope / Vertigo",
        "icd10": "R42",
        "snomed": "386705008",
        "severity": "MODERATE",
        "red_flag": False
    },
    {
        "patterns": [r"\bchest pain\b", r"\bchest tight(?:ness)?\b", r"\bpressure in chest\b", r"\bheart pain\b", r"\bheaviness in chest\b"],
        "term": "Angina Pectoris / Acute Coronary Syndrome",
        "icd10": "I20.9",
        "snomed": "225566008",
        "severity": "CRITICAL",
        "red_flag": True
    },
    {
        "patterns": [r"\bshort(?:ness)? of breath\b", r"\btrouble breathing\b", r"\bhard to breathe\b", r"\bwheezing\b", r"\bgasping\b", r"\bdyspnea\b"],
        "term": "Dyspnea (Respiratory Distress)",
        "icd10": "R06.0",
        "snomed": "267036007",
        "severity": "CRITICAL",
        "red_flag": True
    },
    {
        "patterns": [r"\bnausea\b", r"\bfeeling sick to (?:my )?stomach\b", r"\bqueasy\b"],
        "term": "Nausea",
        "icd10": "R11.0",
        "snomed": "422587007",
        "severity": "ROUTINE",
        "red_flag": False
    },
    {
        "patterns": [r"\bvomit(?:ing)?\b", r"\bthrowing up\b", r"\bpuking\b", r"\bemesis\b"],
        "term": "Emesis (Vomiting)",
        "icd10": "R11.1",
        "snomed": "300359004",
        "severity": "MODERATE",
        "red_flag": False
    },
    {
        "patterns": [r"\bcough\b", r"\bhacking\b", r"\btickling cough\b", r"\bdry cough\b"],
        "term": "Tussis (Cough)",
        "icd10": "R05",
        "snomed": "49727002",
        "severity": "ROUTINE",
        "red_flag": False
    },
    {
        "patterns": [r"\bsore throat\b", r"\bscratchy throat\b", r"\bpain swallow(?:ing)?\b", r"\bpharyngitis\b"],
        "term": "Pharyngalgia (Sore Throat)",
        "icd10": "J02.9",
        "snomed": "162397003",
        "severity": "ROUTINE",
        "red_flag": False
    },
    {
        "patterns": [r"\bfever\b", r"\bhigh temp(?:erature)?\b", r"\bchills\b", r"\bshivering\b"],
        "term": "Pyrexia (Fever)",
        "icd10": "R50.9",
        "snomed": "386661006",
        "severity": "MODERATE",
        "red_flag": False
    },
    {
        "patterns": [r"\bblack stools?\b", r"\btarry stools?\b", r"\bblood in (?:my )?stool\b", r"\bmelena\b", r"\bhematochezia\b"],
        "term": "Melena / Gastrointestinal Hemorrhage",
        "icd10": "K92.1",
        "snomed": "2901004",
        "severity": "CRITICAL",
        "red_flag": True
    },
    {
        "patterns": [r"\bpalpitation\b", r"\bracing heart\b", r"\bpounding heart\b", r"\bfluttering heart\b"],
        "term": "Palpitations (Cardiac Tachyarrhythmia Risk)",
        "icd10": "R00.2",
        "snomed": "80313002",
        "severity": "MODERATE",
        "red_flag": False
    },
    {
        "patterns": [r"\bmuscle weakness\b", r"\bnumbness\b", r"\btingling\b", r"\bparesthesia\b"],
        "term": "Paresthesia / Muscular Paresis",
        "icd10": "R20.2",
        "snomed": "91019004",
        "severity": "MODERATE",
        "red_flag": False
    },
    {
        "patterns": [r"\bface droop\b", r"\bslurred speech\b", r"\bweakness on one side\b", r"\bcannot move arm\b"],
        "term": "Acute Focal Neurological Deficit (Suspected Stroke / CVA)",
        "icd10": "I63.9",
        "snomed": "230690007",
        "severity": "CRITICAL",
        "red_flag": True
    }
]


class SymptomMedicalParser(Tool):
    name = "parse_symptoms"
    description = (
        "Parses unstructured patient complaint narratives into standardized clinical terms "
        "(SNOMED-CT / ICD-10 nomenclature) and detects critical emergency red-flag conditions."
    )
    args_doc = '{"raw_text": "patient complaint text"}'

    def execute(self, raw_text: str = "", **kwargs) -> str:
        if not raw_text:
            return json.dumps({
                "status": "error",
                "message": "raw_text parameter is required"
            })

        text_lower = raw_text.lower()
        matched_terms = []
        red_flags = []
        highest_severity = "ROUTINE"

        for entry in SYMPTOM_DICTIONARY:
            for pat in entry["patterns"]:
                if re.search(pat, text_lower):
                    matched_terms.append({
                        "clinical_term": entry["term"],
                        "icd10": entry["icd10"],
                        "snomed": entry["snomed"],
                        "severity": entry["severity"]
                    })
                    if entry["red_flag"]:
                        red_flags.append(entry["term"])
                        highest_severity = "CRITICAL"
                    elif highest_severity != "CRITICAL" and entry["severity"] == "MODERATE":
                        highest_severity = "MODERATE"
                    break

        if not matched_terms:
            # Fallback clinical extraction
            words = [w.capitalize() for w in re.findall(r"\b[a-zA-Z]{4,}\b", raw_text)[:4]]
            matched_terms.append({
                "clinical_term": f"Unspecified Symptom Presentation ({', '.join(words)})",
                "icd10": "R69",
                "snomed": "418042006",
                "severity": "ROUTINE"
            })

        result = {
            "status": "success",
            "extracted_terms": matched_terms,
            "overall_symptom_acuity": highest_severity,
            "is_emergency_red_flag": len(red_flags) > 0,
            "red_flags": red_flags,
            "summary": f"Identified {len(matched_terms)} clinical entities. Acuity: {highest_severity}."
        }
        return json.dumps(result, indent=2)
