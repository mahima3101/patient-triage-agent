"""Thin wrapper over the free LLM APIs. Picks Gemini or Groq from your environment.
Includes an intelligent DryRunLLM for offline evaluation and judge test harnesses.
"""
import json
import os
import re
import sys
import time

import config


class LLM:
    def __init__(self, provider=None):
        self.provider = provider or os.environ.get("AGENTX_PROVIDER") or (
            "gemini" if os.environ.get("GEMINI_API_KEY") else "groq" if os.environ.get("GROQ_API_KEY") else None)
        if self.provider is None:
            raise RuntimeError("No API key found. Set GEMINI_API_KEY or GROQ_API_KEY in .env (both are free).")
        if self.provider == "gemini":
            from google import genai
            self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        else:
            from groq import Groq
            self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

    def generate(self, system, messages):
        """messages: list of {"role": "user"|"assistant", "content": str}. Returns text. Retries on 429/503."""
        for attempt in range(4):
            try:
                return self._call(system, messages)
            except Exception as e:
                converted = self._native_tool_call_as_json(e)
                if converted:
                    return converted
                # rate limit or transient service spike: back off and retry
                err_str = str(e).lower()
                if attempt < 3 and any(w in err_str for w in ["429", "503", "rate", "quota", "demand", "unavailable", "timeout"]):
                    wait_time = 2 * (attempt + 1)
                    print(f"[LLM] Service busy/unavailable ({e}). Retrying in {wait_time}s...", file=sys.stderr, flush=True)
                    time.sleep(wait_time)
                    continue
                raise

    @staticmethod
    def _native_tool_call_as_json(e):
        """Groq's gpt-oss sometimes emits a native tool call, which the API rejects (400 tool_use_failed).
        Turn that into our JSON action so the agent loop keeps going (unknown tool names are reported back)."""
        try:
            body = e.response.json()["error"]
            if body.get("code") != "tool_use_failed":
                return None
            call = json.loads(body["failed_generation"])
            return json.dumps({"thought": "(native tool call)", "action": str(call["name"]).split(".")[-1],
                               "args": call.get("arguments") or {}})
        except Exception:
            return None

    def _call(self, system, messages):
        if self.provider == "gemini":
            from google.genai import types
            text = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
            r = self.client.models.generate_content(
                model=config.GEMINI_MODEL, contents=text,
                config=types.GenerateContentConfig(system_instruction=system, temperature=config.TEMPERATURE))
            return r.text or ""
        r = self.client.chat.completions.create(
            model=config.GROQ_MODEL, temperature=config.TEMPERATURE,
            messages=[{"role": "system", "content": system}] + messages)
        msg = r.choices[0].message
        return msg.content or getattr(msg, "reasoning", None) or ""


class DryRunLLM:
    """Scripted stand-in so you can test your setup with NO API key: python main.py --dry-run '...'
    Simulates a full 4-stage clinical ReAct trajectory tailored to the input query.
    """

    def __init__(self):
        self.step = 0
        self.scenario = "red"

    def _detect_scenario(self, user_query: str):
        q = user_query.lower()
        has_red = any(w in q for w in ["warfarin", "coumadin", "ibuprofen", "advil", "chest", "sildenafil", "nitroglycerin", "bleed"])
        has_yellow = any(w in q for w in ["lisinopril", "potassium", "cough"]) or ("fever" in q and "no fever" not in q)
        if has_red:
            return "red", ["Warfarin", "Ibuprofen"], "Severe throbbing headache, dizziness"
        elif has_yellow:
            return "yellow", ["Lisinopril", "Potassium Chloride"], "Dry tickling cough and mild fatigue"
        else:
            return "green", ["Multivitamin"], "Mild tension headache after computer work"

    def generate(self, system, messages):
        self.step += 1
        user_query = messages[0]["content"] if messages else ""
        scenario, meds, symptoms = self._detect_scenario(user_query)

        if self.step == 1:
            return json.dumps({
                "thought": "Extract and standardize patient complaints into formal clinical nomenclature.",
                "action": "parse_symptoms",
                "args": {"raw_text": symptoms}
            })

        if self.step == 2:
            return json.dumps({
                "thought": "Cross-reference active medications against interactions.json and DrugBank DDI records.",
                "action": "check_drug_interactions",
                "args": {"drugs": meds, "current_symptoms": [symptoms]}
            })

        if self.step == 3:
            sev = "MAJOR" if scenario == "red" else "MODERATE" if scenario == "yellow" else "NONE"
            return json.dumps({
                "thought": "Search clinical protocols to evaluate whether supportive home-care is permissible.",
                "action": "search_protocol",
                "args": {"condition": symptoms, "interaction_severity": sev}
            })

        if self.step == 4:
            s_acuity = "CRITICAL" if scenario == "red" else "MODERATE" if scenario == "yellow" else "ROUTINE"
            i_sev = "MAJOR" if scenario == "red" else "MODERATE" if scenario == "yellow" else "NONE"
            return json.dumps({
                "thought": "Synthesize all clinical findings into a verified 3-tier triage acuity rating.",
                "action": "classify_urgency",
                "args": {"symptom_acuity": s_acuity, "interaction_severity": i_sev, "has_red_flags": scenario == "red"}
            })

        # Step 5: Final synthesis
        if scenario == "red":
            final_text = (
                "[AURA CLINICAL TRIAGE SUMMARY]\n\n"
                "* Standardized Medical Terms: Cephalea (Acutely severe), Presyncope.\n"
                "* Contraindication Alert: Warfarin + Ibuprofen (MAJOR CONTRAINDICATION). "
                "NSAIDs inhibit platelet aggregation and promote gastric mucosal injury, creating severe hemorrhage risk in patients on oral anticoagulants.\n"
                "* Care Directives: Home self-care is STRICTLY SUSPENDED. Acute headache during active anticoagulation requires immediate clinical evaluation to rule out intracranial hemorrhage.\n"
                "* Triage Classification: [RED] LEVEL: RED (Immediate Emergency). Immediate EMS/Emergency Department evaluation required."
            )
        elif scenario == "yellow":
            final_text = (
                "[AURA CLINICAL TRIAGE SUMMARY]\n\n"
                "* Standardized Medical Terms: Non-productive Tussis, Malaise.\n"
                "* Contraindication Alert: Lisinopril + Potassium Chloride (MODERATE-MAJOR INTERACTION). Risk of hyperkalemia and conduction abnormalities.\n"
                "* Care Directives: Withhold unmonitored potassium supplements. Schedule clinical consult within 12-24 hours for basic metabolic panel check.\n"
                "* Triage Classification: [YELLOW] LEVEL: YELLOW (Urgent Clinical Review). Clinic or telemedicine review within 12-24 hours."
            )
        else:
            final_text = (
                "[AURA CLINICAL TRIAGE SUMMARY]\n\n"
                "* Standardized Medical Terms: Tension Cephalea (Mild), Asthenopia.\n"
                "* Contraindication Alert: None. No adverse drug-drug interactions detected.\n"
                "* Care Directives: Oral hydration (500ml), dark quiet room rest, screen break, cold forehead compress.\n"
                "* Triage Classification: [GREEN] LEVEL: GREEN (Routine Home Care). Safe for supportive home-care protocol."
            )

        return json.dumps({
            "thought": "All 4 clinical stages completed with evidence. Formulating structured triage report.",
            "final_answer": final_text
        })
