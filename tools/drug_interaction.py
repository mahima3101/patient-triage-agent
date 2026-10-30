"""Drug Interaction Checker Tool.
Queries interactions.json and the 222,697 DrugBank DDI_data.csv records
to detect pairwise pharmacological contraindications, mechanisms, and risks.
"""
import csv
import json
import os
import re
from typing import Dict, List, Optional, Tuple
import config
from tools import Tool

# Common clinical brand name to generic mappings
BRAND_TO_GENERIC = {
    "coumadin": "warfarin",
    "jantoven": "warfarin",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "nurofen": "ibuprofen",
    "viagra": "sildenafil",
    "revatio": "sildenafil",
    "nitrostat": "nitroglycerin",
    "nitrolingual": "nitroglycerin",
    "nitro-dur": "nitroglycerin",
    "prinivil": "lisinopril",
    "zestril": "lisinopril",
    "zoloft": "sertraline",
    "nardil": "phenelzine",
    "plavix": "clopidogrel",
    "prilosec": "omeprazole",
    "glucophage": "metformin",
    "cipro": "ciprofloxacin",
    "lanoxin": "digoxin",
    "biaxin": "clarithromycin",
    "lipitor": "atorvastatin",
    "zocor": "simvastatin",
    "cordarone": "amiodarone",
    "tylenol": "acetaminophen",
    "paracetamol": "acetaminophen",
    "aspirin": "aspirin",
    "bayer": "aspirin"
}


class DrugInteractionChecker(Tool):
    name = "check_drug_interactions"
    description = (
        "Checks drug-drug contraindications and adverse interaction risks using the local clinical "
        "interactions.json and DrugBank DDI_data.csv databases. Returns severity, mechanism, and recommendations."
    )
    args_doc = '{"drugs": ["DrugA", "DrugB"], "current_symptoms": ["optional symptom list"]}'

    _ddi_index: Optional[Dict[Tuple[str, str], str]] = None
    _interactions_json_cache: Optional[List[Dict]] = None

    def __init__(self):
        super().__init__()
        self.data_dir = config.DATA_DIR

    def _normalize_name(self, name: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", name.strip().lower())
        return BRAND_TO_GENERIC.get(cleaned, cleaned)

    def _load_interactions_json(self) -> List[Dict]:
        if self._interactions_json_cache is not None:
            return self._interactions_json_cache

        json_path = os.path.join(self.data_dir, "interactions.json")
        if not os.path.exists(json_path):
            # Fallback to current working directory data
            json_path = os.path.join("data", "interactions.json")

        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self._interactions_json_cache = json.load(f)
            except Exception:
                self._interactions_json_cache = []
        else:
            self._interactions_json_cache = []
        return self._interactions_json_cache

    def _load_ddi_csv_index(self) -> Dict[Tuple[str, str], str]:
        if self._ddi_index is not None:
            return self._ddi_index

        self._ddi_index = {}
        csv_path = os.path.join(self.data_dir, "DDI_data.csv")
        if not os.path.exists(csv_path):
            csv_path = os.path.join("data", "DDI_data.csv")
        if not os.path.exists(csv_path):
            csv_path = "DDI_data.csv"

        if os.path.exists(csv_path):
            try:
                with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        d1 = row.get("drug1_name", "").strip().lower()
                        d2 = row.get("drug2_name", "").strip().lower()
                        itype = row.get("interaction_type", "").strip()
                        if d1 and d2:
                            self._ddi_index[(d1, d2)] = itype
                            self._ddi_index[(d2, d1)] = itype
            except Exception:
                pass
        return self._ddi_index

    def execute(self, drugs=None, current_symptoms=None, **kwargs) -> str:
        if not drugs:
            return json.dumps({
                "status": "error",
                "message": "At least one medication name must be provided in 'drugs'."
            })

        if isinstance(drugs, str):
            drugs = [d.strip() for d in re.split(r"[,;/]+", drugs) if d.strip()]

        normalized_drugs = [(d, self._normalize_name(d)) for d in drugs]
        json_interactions = self._load_interactions_json()
        ddi_index = self._load_ddi_csv_index()

        flagged_interactions = []
        overall_severity = "NONE"

        # Check pairwise combinations
        for i in range(len(normalized_drugs)):
            orig_a, norm_a = normalized_drugs[i]
            for j in range(i + 1, len(normalized_drugs)):
                orig_b, norm_b = normalized_drugs[j]

                match_found = False

                # 1. Search high-acuity interactions.json
                for rule in json_interactions:
                    rule_a = rule.get("drug_a", "").lower()
                    rule_b = rule.get("drug_b", "").lower()
                    aliases_a = [a.lower() for a in rule.get("aliases_a", [])]
                    aliases_b = [b.lower() for b in rule.get("aliases_b", [])]

                    cond1 = (norm_a == rule_a or norm_a in aliases_a) and (norm_b == rule_b or norm_b in aliases_b)
                    cond2 = (norm_b == rule_a or norm_b in aliases_a) and (norm_a == rule_b or norm_a in aliases_b)

                    if cond1 or cond2:
                        match_found = True
                        sev = rule.get("severity", "MAJOR")
                        flagged_interactions.append({
                            "pair": f"{orig_a} + {orig_b}",
                            "severity": sev,
                            "mechanism": rule.get("mechanism"),
                            "clinical_risk": rule.get("clinical_risk"),
                            "recommendation": rule.get("recommendation"),
                            "source": "interactions.json"
                        })
                        if sev == "CONTRAINDICATED":
                            overall_severity = "CONTRAINDICATED"
                        elif sev == "MAJOR" and overall_severity != "CONTRAINDICATED":
                            overall_severity = "MAJOR"
                        elif sev == "MODERATE" and overall_severity not in ["CONTRAINDICATED", "MAJOR"]:
                            overall_severity = "MODERATE"
                        break

                # 2. Search DrugBank DDI_data.csv if not already matched
                if not match_found and ddi_index:
                    interaction_type = ddi_index.get((norm_a, norm_b))
                    if interaction_type:
                        itype_lower = interaction_type.lower()
                        if "bleeding" in itype_lower or "cardiac" in itype_lower or "qtc" in itype_lower or "hypotensive" in itype_lower:
                            sev = "MAJOR"
                        else:
                            sev = "MODERATE"

                        flagged_interactions.append({
                            "pair": f"{orig_a} + {orig_b}",
                            "severity": sev,
                            "mechanism": f"DrugBank cataloged interaction: alters {interaction_type}.",
                            "clinical_risk": f"Increased risk of adverse pharmacological effects: {interaction_type}.",
                            "recommendation": "Monitor patient vitals; evaluate dosage adjustment or alternative therapy.",
                            "source": "DrugBank DDI_data.csv"
                        })
                        if sev == "MAJOR" and overall_severity != "CONTRAINDICATED":
                            overall_severity = "MAJOR"
                        elif sev == "MODERATE" and overall_severity not in ["CONTRAINDICATED", "MAJOR"]:
                            overall_severity = "MODERATE"

        # Check symptom cross-contraindications
        symptom_warnings = []
        if current_symptoms:
            sym_text = " ".join(current_symptoms).lower() if isinstance(current_symptoms, list) else str(current_symptoms).lower()
            for orig, norm in normalized_drugs:
                if norm in ["ibuprofen", "aspirin", "naproxen"] and any(w in sym_text for w in ["headache", "melena", "bleed", "stomach pain"]):
                    if any(d in [n for _, n in normalized_drugs] for d in ["warfarin", "apixaban", "rivaroxaban", "clopidogrel"]):
                        symptom_warnings.append(
                            f"WARNING: Taking {orig} (NSAID) while presenting with severe headache on active anticoagulants presents life-threatening intracranial hemorrhage risk."
                        )
                        overall_severity = "CONTRAINDICATED"

        result = {
            "status": "success",
            "medications_analyzed": [d for d, _ in normalized_drugs],
            "interactions_count": len(flagged_interactions),
            "highest_severity": overall_severity,
            "flagged_interactions": flagged_interactions,
            "symptom_warnings": symptom_warnings,
            "summary": (
                f"Flagged {len(flagged_interactions)} interaction(s). Highest severity: {overall_severity}."
                if flagged_interactions else "No contraindications detected across local DrugBank databases."
            )
        }
        return json.dumps(result, indent=2)
