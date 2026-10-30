# 🩺 Project Context: AURA Patient Triage & Interaction Checker

**Target Challenge**: AgentX Challenge 2026 (SRMIST Tiruchirappalli)  
**Track**: Healthcare & Biotech  
**Project Name**: AURA (Autonomous Triage & Pharmacovigilance Reasoning Agent)  
**Status**: Production Complete & Verified (19/19 Tests Passing)  

---

## 1. Clinical Background & Problem Statement

### 1.1 The Clinical Challenge
In emergency departments, urgent care centers, and telemedicine triage platforms, intake personnel are confronted with two compounding challenges:
1. **Unstructured & Ambiguous Patient Language**: Patients routinely express life-threatening emergencies in colloquial vernacular (e.g., *"my head is pounding, my chest feels squeezed, and I took my blood thinner with an Advil"*).
2. **Adverse Drug Events (ADEs) & Severe Contraindications**: Over **1.3 million emergency department visits** occur annually in the United States due to preventable Adverse Drug Events. Co-administration of contraindicated medications (e.g., oral anticoagulants + NSAIDs, nitrates + PDE5 inhibitors, ACE inhibitors + potassium supplements) frequently leads to fatal cardiovascular collapse, intractable hemorrhage, or hyperkalemic cardiac arrest.

### 1.2 The Solution: AURA
AURA is an autonomous, evidence-grounded ReAct decision-support agent engineered to evaluate patient complaints, translate informal terms into standardized clinical taxonomy, cross-reference pharmacological databases, query evidence-based care protocols, and stratify triage urgency into a validated 3-tier rating:
- 🟢 **GREEN**: Routine / Supportive self-care with verified home protocol.
- 🟡 **YELLOW**: Urgent / Primary care or telemedicine review within 12–24 hours.
- 🔴 **RED**: Immediate Emergency / EMS dispatch or emergency room evaluation (0–1 hour).

---

## 2. The 4 Functional Pillars

### Pillar 1: Parse Symptoms into Medical Terms
- **Input**: Raw, conversational patient intake narrative.
- **Processing**: Standardizes patient vernacular into standardized clinical nomenclature (**SNOMED-CT / ICD-10**) and flags immediate emergency red flags (e.g., crushing chest pressure, unilateral facial droop, dyspnea, melena, thunderclap headache).
- **Output**: Structured list of primary symptoms, ICD-10 codes, SNOMED concept IDs, and baseline symptom acuity (`CRITICAL`, `MODERATE`, `ROUTINE`).

### Pillar 2: Flag Contraindications via Local Drug Tools
- **Input**: Active medications list and candidate treatments.
- **Data Source**: Local `interactions.json` and 222,697 DrugBank interaction pairs in `DDI_data.csv`.
- **Processing**: Exact and brand-alias entity matching (`Coumadin` ➔ `Warfarin`, `Advil` ➔ `Ibuprofen`, `Viagra` ➔ `Sildenafil`, `Nitrostat` ➔ `Nitroglycerin`). Evaluates pairwise interactions, pharmacodynamic synergism, pharmacokinetic inhibition/induction, and severity ratings:
  - `CONTRAINDICATED`: Absolute contraindication; severe life-threatening risk.
  - `MAJOR`: Significant clinical risk requiring alternative therapy.
  - `MODERATE`: Requires clinical monitoring or dosage adjustment.
  - `MINOR`: Minimal clinical risk.
- **Output**: Flagged contraindications, pharmacological mechanisms, clinical risks, and alternative therapy recommendations.

### Pillar 3: Search Recent Home-Care Protocols
- **Input**: Normalized symptom profile + confirmed absence of critical red flags.
- **Data Source**: Local verified protocol database (`data/homecare_protocols.json`) and clinical web search fallback.
- **Processing**: Retrieves condition-specific clinical protocols from `homecare_protocols.json`.
- **Safety Boundary Enforcement**: If major contraindications or critical red-flag symptoms are present, supportive home-care is **strictly suspended**, preventing dangerous self-treatment.

### Pillar 4: Classify Urgency (Green / Yellow / Red)
- **Triage Decision Engine**:
  - 🔴 **RED (Emergency)**:
    - Any severe drug contraindication (e.g., serotonin syndrome risk, fatal arrhythmia risk).
    - Vital red flag symptoms: crushing chest pain, dyspnea, focal neurological deficits, acute anaphylaxis, severe uncontrolled hemorrhage.
  - 🟡 **YELLOW (Urgent)**:
    - Moderate drug interaction requiring doctor evaluation.
    - Persistent high fever (>39°C / 102.2°F), worsening pain, localized symptoms requiring prescription treatment.
  - 🟢 **GREEN (Routine / Low)**:
    - Mild, self-limiting symptoms with zero drug contraindications.
    - Clear home-care pathway; recommendation to monitor for 48 hours.

---

## 3. Data Tier Specifications

### 3.1 `interactions.json`
Stores curated, high-acuity pairwise contraindications with clinical pharmacology metadata:
```json
[
  {
    "drug_a": "Warfarin",
    "drug_b": "Ibuprofen",
    "aliases_a": ["Coumadin", "Jantoven"],
    "aliases_b": ["Advil", "Motrin", "Nurofen"],
    "severity": "MAJOR",
    "urgency": "RED",
    "mechanism": "NSAIDs competitively inhibit platelet cyclooxygenase-1 (COX-1), blocking thromboxane A2 synthesis and causing gastric mucosal erosions. When combined with oral vitamin K antagonists (Warfarin), it dramatically elevates the risk of severe gastrointestinal hemorrhage, systemic bleeding, and occult hematoma.",
    "clinical_risk": "Acute upper gastrointestinal hemorrhage, intracranial hemorrhage, uncontrolled systemic bleeding.",
    "recommendation": "Avoid combination. Withhold Ibuprofen immediately. Consider Acetaminophen (maximum 2g/day) under strict medical supervision if analgesia is required and INR is stable.",
    "symptom_warnings": ["Severe headache", "Dizziness", "Black/tarry stools (Melena)", "Easy bruising", "Epistaxis"]
  }
]
```

### 3.2 `DDI_data.csv` (14.9 MB)
Tabular dataset sourced from DrugBank reference data, containing **222,697 interaction records**:
| Column | Type | Description |
|---|---|---|
| `drug1_id` | string | DrugBank accession identifier for primary agent (e.g., `DB00006`) |
| `drug2_id` | string | DrugBank accession identifier for secondary agent (e.g., `DB13783`) |
| `drug1_name` | string | Generic name of primary medication |
| `drug2_name` | string | Generic name of secondary medication |
| `interaction_type` | string | Specific pharmacological interaction consequence (e.g., `anticoagulant activities`, `risk or severity of bleeding`, `QTc-prolonging activities`, `serum concentration`) |

### 3.3 `homecare_protocols.json`
Verified clinical self-care guidelines indexed by condition:
```json
[
  {
    "condition": "Tension-Type Headache / Screen Asthenopia",
    "icd10": "G44.2",
    "snomed": "398057008",
    "symptom_keywords": ["headache", "temple pain", "band-like pain", "dull ache", "eye strain", "screen fatigue"],
    "home_care_measures": [
      "Immediate oral hydration: Consume 500-750 mL of water.",
      "Rest in a quiet, dark, well-ventilated room with eyes closed for 30-45 minutes.",
      "Apply a cold damp washcloth or ice pack over forehead or warm compress to posterior neck muscles.",
      "Practice the 20-20-20 visual rest rule (look at an object 20 feet away for 20 seconds every 20 minutes of screen use)."
    ],
    "medication_guidance": "Acetaminophen (500-1000 mg oral every 6 hours as needed, max 3000 mg/day) ONLY IF no contraindication exists and liver function is normal. Verify with drug interaction checker before taking NSAIDs if patient takes anticoagulants or ACE inhibitors.",
    "escalation_red_flags": [
      "Sudden 'thunderclap' onset of worst headache of life (subarachnoid hemorrhage risk)",
      "Accompanied by neck stiffness, high fever, or photophobia (meningitis triad)",
      "Headache on anticoagulant therapy (Warfarin, NOACs) - Mandatory Emergency Department referral"
    ],
    "urgency_classification": "GREEN"
  }
]
```

---

## 4. Frontend Design: Claymorphism (Navy Blue & Warm Beige)

To ensure the clinical triage process is both aesthetically engaging and easy for evaluators and judges to understand during live presentations, AURA incorporates a tactile **Claymorphism** interface:

### 4.1 Aesthetic Concept & Palette
- **Deep Midnight Navy (`#152238`, `#1E2E4A`)**: Represents clinical precision, seriousness, and high authority. Applied to primary CTAs, active states, pill tags, and the terminal trace viewer.
- **Warm Beige & Cream (`#F8F5EE`, `#F1E9DC`, `#E5DAC9`)**: Evokes a calming, hospitable medical environment, reducing the cold sterile feeling of medical software.
- **Claymorphism Depth**: Created with rounded geometries (`border-radius: 22px` to `30px`) and composite dual-shadow styling (soft drop shadows combined with light inset highlight reflections and dark inset bevel shadows).

### 4.2 Interactive Components
1. **Patient Intake Console**:
   - Multi-line narrative textarea with one-tap symptom chip injectors (`+ Severe headache`, `+ Dizziness`, `+ Cough`).
   - Dynamic medication tagger allowing seamless addition and deletion of active pharmaceutical regimens.
2. **4-Stage Pipeline Progress Engine**:
   - Visually indicates the exact step currently executing in the ReAct loop:
     `Parse Terms` ➔ `Drug Checker` ➔ `Protocols` ➔ `Triage Urgency`.
3. **Clinical Output Cards**:
   - Acuity Hero Banner with animated urgency level badges (🔴 Red, 🟡 Yellow, 🟢 Green).
   - Standardized medical nomenclature chips.
   - Pharmacological contraindication risk cards with clinical mechanisms and DrugBank references.
   - Evidence-based home-care protocols with explicit red-flag escalation triggers.
4. **Live Scenario Quick-Switchers**:
   - One-click buttons to instantly load representative benchmark cases for live presentations without manual typing:
     - 🔴 **Red Preset**: Warfarin + NSAID (Severe Hemorrhage Risk).
     - 🟡 **Yellow Preset**: Lisinopril + Potassium Chloride (Hyperkalemia Hazard).
     - 🟢 **Green Preset**: Mild Tension Headache (Digital Strain / Hydration Protocol).
5. **ReAct Trace Inspector**:
   - Embedded dark terminal log drawer displaying the model's exact thoughts, tool actions, and raw observations, validating that the frontend is driven by real agentic reasoning rather than hardcoded mockups.

---

## 5. Judging Contract & Headless Specification

Judges automatically inspect execution traces and terminal outputs before looking at any UI.

### 5.1 Headless CLI Contract
- **Command**: `python main.py --json "<patient query>"`
- **Requirement**: Must output **EXACTLY ONE JSON line** to `stdout`:
  ```json
  {
    "answer": "<Structured triage report with medical terms, drug warnings, protocol, and urgency>",
    "trace": [
      {
        "thought": "Extract symptoms and medications from the narrative",
        "tool": "parse_symptoms",
        "args": {"raw_text": "..."},
        "observation": "..."
      },
      {
        "thought": "Check for contraindications",
        "tool": "check_drug_interactions",
        "args": {"drugs": ["..."]},
        "observation": "..."
      }
    ]
  }
  ```
- **Logging Rule**: All diagnostic logs, step traces, and thoughts during non-json mode or debugging go to `stderr`.

---

## 6. Scoring Matrix Mapping

| Score Category | Points | How This Project Wins Top Score |
|---|:---:|---|
| **Agentic Architecture & Autonomy** | **40 pts** | • Full ReAct cycle with dynamic planning.<br>• Chooses tools iteratively based on prior observations.<br>• Self-corrects when tool calls fail or inputs are ambiguous.<br>• Loop-prevention guard and step-budget enforcement. |
| **Domain Utility & Execution** | **30 pts** | • Real clinical data (`interactions.json`, DrugBank CSV).<br>• Accurate pharmacological mechanism reporting.<br>• Realistic 3-tier urgency classification (Green/Yellow/Red).<br>• Zero hardcoded answers. |
| **Code Hygiene & System Design** | **20 pts** | • Strict modular architecture: `agent/`, `tools/`, `config/`, `data/`, `frontend/`.<br>• Strict compliance with judges' `--json` contract.<br>• Offline unit tests covering parsing, interaction checks, and executor loops.<br>• Comprehensive documentation and immediate runnability from README. |
| **Presentation & Live Demo** | **10 pts** | • Tactile Claymorphism UI (Navy Blue & Warm Beige) with real-time pipeline visualizer.<br>• Monospace ReAct trace inspector for live verification.<br>• One-click clinical scenario switcher for presentation flow.<br>• Complete technical Q&A preparation for all team members. |

---

## 7. Team Defense & Technical Q&A Cheatsheet

1. **Why not just prompt the LLM directly with the symptoms and medications?**  
   *Answer*: Large language models suffer from severe pharmacological hallucinations and out-of-date parametric memory. By using an agentic ReAct loop that queries local DrugBank records and `interactions.json`, every contraindication and severity rating is grounded in authoritative clinical data, satisfying strict medical safety standards.

2. **How does the agent handle ambiguous or misspelt drug names?**  
   *Answer*: The `check_drug_interactions` tool implements fuzzy name matching and alias resolution against known brand-to-generic mappings before executing SQL/JSON queries, preventing missed contraindications due to colloquial names.

3. **What happens if a tool crashes or data is unavailable?**  
   *Answer*: The tool returns a structured error string into the agent's observation stream. The ReAct engine reads the error, self-corrects the query parameters, or falls back to secondary sources (e.g. web protocol search), ensuring the process never crashes.

4. **Why did you build both a CLI and a Claymorphism frontend?**  
   *Answer*: The AgentX evaluation harness tests headless CLI execution (`python main.py --json "..."`) via automated scripts, so strict CLI compliance is non-negotiable. The Claymorphism frontend (Navy & Beige) was engineered specifically for the live judging presentation to visually prove the 4-stage ReAct pipeline, show real-time Thought-Action-Observation traces, and let judges interact with real clinical scenarios.

5. **Does the UI require Node.js, React, or heavy npm dependencies to run?**  
   *Answer*: No. The UI is built with zero runtime dependencies using clean modern HTML5, CSS3 claymorphism tokens, and vanilla JavaScript. It is served instantly by Python's built-in standard library (`python serve.py`), meaning any judge can run it immediately without `npm install` headaches.
