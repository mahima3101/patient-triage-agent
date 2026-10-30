"""End-to-End Integration Tests for Clinical Triage Scenarios (Red, Yellow, Green).
Validates the full ReAct loop execution, tool chaining, and judges' JSON contract.
"""
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_agent


class TestClinicalIntegrationScenarios(unittest.TestCase):
    def test_scenario_red_anticoagulant_nsaid(self):
        query = "Patient takes Warfarin, reports severe headache and wants to take Ibuprofen"
        answer, trace = run_agent(query, dry_run=True, verbose=False)
        self.assertIn("[RED]", answer)
        self.assertIn("Warfarin + Ibuprofen", answer)
        self.assertTrue(len(trace) >= 4)
        tools_called = [t["tool"] for t in trace]
        self.assertIn("parse_symptoms", tools_called)
        self.assertIn("check_drug_interactions", tools_called)
        self.assertIn("search_protocol", tools_called)
        self.assertIn("classify_urgency", tools_called)

    def test_scenario_yellow_ace_inhibitor_potassium(self):
        query = "Patient takes Lisinopril for hypertension, reports dry cough and is taking Potassium supplements"
        answer, trace = run_agent(query, dry_run=True, verbose=False)
        self.assertIn("[YELLOW]", answer)
        self.assertIn("Lisinopril + Potassium Chloride", answer)
        self.assertTrue(len(trace) >= 4)

    def test_scenario_green_benign_tension_headache(self):
        query = "Mild dull headache around temples after working at computer, no fever, no active medications"
        answer, trace = run_agent(query, dry_run=True, verbose=False)
        self.assertIn("[GREEN]", answer)
        self.assertIn("Routine Home Care", answer)
        self.assertTrue(len(trace) >= 4)

    def test_cli_headless_json_contract_strict(self):
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_py = os.path.join(script_dir, "main.py")
        proc = subprocess.run(
            [sys.executable, main_py, "--json", "--dry-run", "Test query"],
            cwd=script_dir,
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        lines = proc.stdout.strip().splitlines()
        self.assertEqual(len(lines), 1, f"Expected strictly 1 line on stdout, got {len(lines)}: {lines}")
        data = json.loads(lines[0])
        self.assertIn("answer", data)
        self.assertIn("trace", data)
        self.assertIsInstance(data["trace"], list)
        self.assertTrue(len(data["trace"]) >= 4)


if __name__ == "__main__":
    unittest.main()
