"""Urgency Classifier Tool.
Stratifies patient clinical presentation into validated 3-tier triage levels:
GREEN (Routine/Home Care), YELLOW (Urgent/12-24h Clinic), or RED (Immediate Emergency/ER).
"""
import json
from tools import Tool


class UrgencyClassifier(Tool):
    name = "classify_urgency"
    description = (
        "Classifies patient triage acuity into a 3-tier rating (GREEN, YELLOW, RED) by synthesizing "
        "symptom acuity, drug interaction severity, and red-flag indicators."
    )
    args_doc = '{"symptom_acuity": "CRITICAL|MODERATE|ROUTINE", "interaction_severity": "CONTRAINDICATED|MAJOR|MODERATE|NONE", "has_red_flags": false}'

    def execute(self, symptom_acuity: str = "ROUTINE", interaction_severity: str = "NONE", has_red_flags: bool = False, **kwargs) -> str:
        s_acuity = str(symptom_acuity).upper()
        i_sev = str(interaction_severity).upper()

        # Decision Matrix
        if has_red_flags or i_sev == "CONTRAINDICATED" or s_acuity == "CRITICAL":
            level = "RED"
            badge = "🔴 RED (Immediate Emergency)"
            timeframe = "Immediate EMS / Emergency Department evaluation (0-1 hour)"
            rationale = (
                "Critical clinical risk identified. Potential for life-threatening hemodynamic instability, "
                "fatal drug toxicity, or severe hemorrhagic/cardiovascular complication."
            )
            action_plan = [
                "Instruct patient/caregiver to call local emergency medical services (EMS/911/112) immediately.",
                "Immediately discontinue any contraindicated medication identified.",
                "Do not attempt home supportive care or oral self-medication.",
                "Prepare active medication list and timing of last doses for emergency personnel."
            ]
        elif i_sev == "MAJOR" or (i_sev == "MODERATE" and s_acuity == "MODERATE"):
            level = "RED" if s_acuity == "MODERATE" and i_sev == "MAJOR" else "YELLOW"
            badge = "🔴 RED (Immediate Emergency)" if level == "RED" else "🟡 YELLOW (Urgent Clinical Review)"
            timeframe = "Immediate ER" if level == "RED" else "Clinical consultation within 12-24 hours"
            rationale = (
                f"Significant pharmacological risk ({i_sev}) combined with active symptoms ({s_acuity}). "
                "Requires prompt clinical assessment and medication regimen adjustment."
            )
            action_plan = [
                "Withhold offending medication combination pending physician review.",
                "Schedule priority same-day clinic or urgent care appointment.",
                "Monitor vitals (blood pressure, heart rate, temperature) every 4 hours.",
                "Escalate to Emergency Department immediately if red-flag symptoms develop."
            ]
        elif i_sev == "MODERATE" or s_acuity == "MODERATE":
            level = "YELLOW"
            badge = "🟡 YELLOW (Urgent Clinical Review)"
            timeframe = "Outpatient physician evaluation within 12-24 hours"
            rationale = (
                "Moderate clinical risk or persistent symptoms requiring medical consultation. "
                "Low risk of imminent decompensation, but unmonitored home care is insufficient."
            )
            action_plan = [
                "Contact primary care physician or telemedicine service for evaluation.",
                "Avoid starting new over-the-counter supplements or medications.",
                "Maintain hydration and observe symptom trajectory."
            ]
        else:
            level = "GREEN"
            badge = "🟢 GREEN (Routine / Home Care)"
            timeframe = "Self-care with follow-up if unmitigated after 48-72 hours"
            rationale = (
                "Self-limiting presentation with zero adverse drug-drug interactions or emergency red flags. "
                "Appropriate for conservative, supportive home-care protocols."
            )
            action_plan = [
                "Follow verified evidence-based home-care protocol (hydration, rest, non-pharmacological relief).",
                "Ensure OTC medications adhere strictly to interaction checker guidance.",
                "Re-evaluate and seek clinical review if symptoms worsen or persist beyond 72 hours."
            ]

        result = {
            "urgency_level": level,
            "badge": badge,
            "timeframe": timeframe,
            "triage_rationale": rationale,
            "action_plan": action_plan,
            "summary": f"Triage Stratification: {level} urgency. {timeframe}."
        }
        return json.dumps(result, indent=2)
