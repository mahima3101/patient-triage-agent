"""Home-Care Protocol Search Tool.
Retrieves verified evidence-based supportive home-care protocols from homecare_protocols.json
with web search fallback, and enforces clinical safety boundaries when red flags exist.
"""
import json
import os
import re
from typing import Dict, List, Optional
import config
from tools import Tool
from tools.web_search import WebSearch


class HomeCareProtocolSearch(Tool):
    name = "search_protocol"
    description = (
        "Retrieves verified clinical home-care protocols from homecare_protocols.json (or web search fallback). "
        "Enforces safety guards: if major drug contraindications or red flags are present, home-care is withheld."
    )
    args_doc = '{"condition": "condition or symptom name", "interaction_severity": "NONE|MODERATE|MAJOR|CONTRAINDICATED", "has_red_flags": false}'

    _protocols_cache: Optional[List[Dict]] = None

    def __init__(self):
        super().__init__()
        self.data_dir = config.DATA_DIR
        self.web_search = WebSearch()

    def _load_protocols(self) -> List[Dict]:
        if self._protocols_cache is not None:
            return self._protocols_cache

        proto_path = os.path.join(self.data_dir, "homecare_protocols.json")
        if not os.path.exists(proto_path):
            proto_path = os.path.join("data", "homecare_protocols.json")

        if os.path.exists(proto_path):
            try:
                with open(proto_path, "r", encoding="utf-8") as f:
                    self._protocols_cache = json.load(f)
            except Exception:
                self._protocols_cache = []
        else:
            self._protocols_cache = []
        return self._protocols_cache

    def execute(self, condition: str = "", interaction_severity: str = "NONE", has_red_flags: bool = False, **kwargs) -> str:
        # Enforce clinical safety boundary
        sev_upper = str(interaction_severity).upper()
        if sev_upper in ["CONTRAINDICATED", "MAJOR"] or has_red_flags:
            return json.dumps({
                "status": "home_care_suspended",
                "condition": condition,
                "home_care_allowed": False,
                "reason": (
                    f"Home-care protocols are strictly contraindicated due to presence of "
                    f"{'critical red-flag symptoms' if has_red_flags else f'{sev_upper} drug interaction risk'}."
                ),
                "clinical_directive": (
                    "Do NOT attempt home supportive self-care. Patient requires immediate medical evaluation "
                    "(Emergency Department or urgent clinical visit) to prevent serious adverse events."
                ),
                "recommended_urgency": "RED" if sev_upper == "CONTRAINDICATED" or has_red_flags else "YELLOW"
            }, indent=2)

        protocols = self._load_protocols()
        condition_lower = condition.lower() if condition else ""

        # Search local homecare protocols
        matched_protocol = None
        for proto in protocols:
            cname = proto.get("condition", "").lower()
            keywords = [k.lower() for k in proto.get("symptom_keywords", [])]
            if condition_lower and (condition_lower in cname or any(k in condition_lower for k in keywords)):
                matched_protocol = proto
                break
            elif not condition_lower and keywords:
                matched_protocol = proto
                break

        if matched_protocol:
            return json.dumps({
                "status": "success",
                "source": "homecare_protocols.json",
                "condition": matched_protocol.get("condition"),
                "icd10": matched_protocol.get("icd10"),
                "snomed": matched_protocol.get("snomed"),
                "home_care_allowed": True,
                "supportive_measures": matched_protocol.get("home_care_measures", []),
                "otc_guidance": matched_protocol.get("medication_guidance"),
                "escalation_triggers": matched_protocol.get("escalation_red_flags", []),
                "summary": f"Retrieved verified home-care protocol for {matched_protocol.get('condition')}."
            }, indent=2)

        # Fallback to web search if local database has no exact match
        try:
            search_query = f"evidence based home care guidelines protocol {condition}"
            web_res = self.web_search.execute(query=search_query)
            return json.dumps({
                "status": "success",
                "source": "web_search",
                "condition": condition,
                "home_care_allowed": True,
                "web_guidance": web_res,
                "summary": f"Searched recent clinical web protocols for {condition}."
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "partial",
                "condition": condition,
                "home_care_allowed": True,
                "supportive_measures": [
                    "Ensure adequate hydration and oral fluid intake.",
                    "Rest in a quiet, temperature-controlled environment.",
                    "Monitor symptoms every 4 to 6 hours."
                ],
                "escalation_triggers": [
                    "Fever exceeding 38.5°C",
                    "Difficulty breathing or chest tightness",
                    "Symptoms worsening after 24-48 hours"
                ],
                "summary": f"Applied standard clinical supportive care protocol for {condition}."
            }, indent=2)
