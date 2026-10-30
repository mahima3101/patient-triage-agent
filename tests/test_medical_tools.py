"""Unit tests for specialized clinical medical tools."""
import json
import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.drug_interaction import DrugInteractionChecker
from tools.protocol_search import HomeCareProtocolSearch
from tools.symptom_parser import SymptomMedicalParser
from tools.urgency_classifier import UrgencyClassifier


class TestMedicalTools(unittest.TestCase):
    def setUp(self):
        self.parser = SymptomMedicalParser()
        self.drug_checker = DrugInteractionChecker()
        self.protocol_search = HomeCareProtocolSearch()
        self.classifier = UrgencyClassifier()

    def test_symptom_parser_routine(self):
        res = json.loads(self.parser.execute("I have a mild tension headache and dry cough"))
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["is_emergency_red_flag"])
        terms = [t["clinical_term"] for t in res["extracted_terms"]]
        self.assertTrue(any("Cephalea" in t for t in terms))
        self.assertTrue(any("Tussis" in t for t in terms))

    def test_symptom_parser_critical_red_flag(self):
        res = json.loads(self.parser.execute("Patient reports sudden crushing chest pain and shortness of breath"))
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_emergency_red_flag"])
        self.assertEqual(res["overall_symptom_acuity"], "CRITICAL")
        self.assertTrue(len(res["red_flags"]) >= 1)

    def test_drug_interaction_major_warfarin_ibuprofen(self):
        res = json.loads(self.drug_checker.execute(drugs=["Warfarin", "Ibuprofen"]))
        self.assertEqual(res["status"], "success")
        self.assertIn(res["highest_severity"], ["MAJOR", "CONTRAINDICATED"])
        self.assertTrue(len(res["flagged_interactions"]) >= 1)
        pair_match = any("Warfarin" in f["pair"] and "Ibuprofen" in f["pair"] for f in res["flagged_interactions"])
        self.assertTrue(pair_match)

    def test_drug_interaction_contraindicated_sildenafil_nitrate(self):
        res = json.loads(self.drug_checker.execute(drugs=["Viagra", "Nitrostat"]))
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["highest_severity"], "CONTRAINDICATED")

    def test_drug_interaction_none(self):
        res = json.loads(self.drug_checker.execute(drugs=["Multivitamin"]))
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["highest_severity"], "NONE")

    def test_protocol_search_homecare_allowed(self):
        res = json.loads(self.protocol_search.execute(condition="tension headache", interaction_severity="NONE"))
        self.assertTrue(res.get("home_care_allowed"))
        self.assertTrue(len(res.get("supportive_measures", [])) > 0)

    def test_protocol_search_safety_guard_blocks_home_care(self):
        res = json.loads(self.protocol_search.execute(condition="headache", interaction_severity="MAJOR"))
        self.assertFalse(res.get("home_care_allowed"))
        self.assertEqual(res.get("status"), "home_care_suspended")
        self.assertIn("strictly contraindicated", res.get("reason"))

    def test_urgency_classifier_red(self):
        res = json.loads(self.classifier.execute(symptom_acuity="CRITICAL", interaction_severity="MAJOR"))
        self.assertEqual(res["urgency_level"], "RED")
        self.assertIn("Immediate", res["timeframe"])

    def test_urgency_classifier_green(self):
        res = json.loads(self.classifier.execute(symptom_acuity="ROUTINE", interaction_severity="NONE"))
        self.assertEqual(res["urgency_level"], "GREEN")


if __name__ == "__main__":
    unittest.main()
