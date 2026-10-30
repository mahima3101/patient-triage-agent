# Project Context: AURA Patient Triage & Interaction Checker

**Challenge Track**: Healthcare & Biotech  
**Event**: AgentX Challenge 2026 (SRMIST Tiruchirappalli)  
**Project Name**: AURA — Autonomous Patient Triage & Drug-Drug Interaction Checker  

---

## 1. Problem Statement & Clinical Relevance

In clinical intake, emergency departments, and telehealth platforms, patient self-reported symptoms are frequently expressed in colloquial, unstructured language (e.g., *"my chest feels super heavy and I took my grandpa's heart pills with my headache pills"*). Concurrently, over **1.3 million emergency department visits** occur annually due to Adverse Drug Events (ADEs) and unrecognized drug-drug contraindications.

Clinicians and triage nurses need an autonomous, evidence-grounded agent capable of:
1. Translating messy natural-language patient complaints into standardized medical taxonomy.
2. Cross-referencing patient medications against pharmacological contraindication databases (`interactions.json` and DrugBank CSV).
3. Searching verified, up-to-date clinical home-care protocols for non-emergency conditions.
4. Stratifying patient acuity into a validated 3-tier triage system:
   - 🟢 **GREEN**: Non-urgent / Self-care with home protocol.
   - 🟡 **YELLOW**: Urgent / Needs clinical evaluation within 12-24 hours.
   - 🔴 **RED**: Immediate Emergency / Call EMS or proceed to nearest Emergency Department.

---

## 2. The 4 Functional Pillars

### Pillar 1: Parse Symptoms into Medical Terms
- **Input**: Colloquial, rambling user narrative.
- **Process**: Extraction of clinical entities, mapping colloquial descriptions to standardized medical concepts (e.g., *"dizziness upon standing"* -> *Orthostatic Lightheadedness / Presyncope*; *"throbbing temple pain"* -> *Temporal Cephalea*).
- **Output**: Structured list of primary symptoms, duration, acuity, and anatomical system.

### Pillar 2: Flag Contraindications via Local Drug Tool
- **Input**: Active medications and candidate remedies.
- **Data Source**: Local `interactions.json` and tabular DrugBank CSVs (`data/drug_interactions_drugbank.csv`).
- **Process**: Exact & fuzzy entity matching of active drugs (generic & brand names). Identification of pairwise interactions, pharmacodynamic synergism, pharmacokinetic inhibition/induction, and severity ratings:
  - `CONTRAINDICATED`: Potentially life-threatening (e.g., Sildenafil + Nitroglycerin = profound hypotension).
  - `MAJOR`: Significant clinical risk requiring alternative therapy (e.g., Warfarin + Ibuprofen = upper GI hemorrhage).
  - `MODERATE`: Requires close monitoring or dosage adjustment.
  - `MINOR`: Minimal clinical risk.
- **Output**: Flagged contraindications, mechanisms of action, and clinical warnings.

### Pillar 3: Search Recent Home-Care Protocols
- **Input**: Normalized symptom profile + confirmed absence of critical red flags.
- **Data Source**: Local verified protocol database (`data/homecare_protocols.json`) and clinical web search fallback.
- **Process**: Retrieve evidence-backed supportive care (hydration, rest, non-pharmacological therapies, OTC medications not contraindicated by the drug checker).
- **Safety Boundary**: If red flags or severe contraindications are detected, home-care recommendations are automatically suppressed in favor of emergency medical instructions.

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
Stores high-frequency, high-acuity drug-drug interactions with explicit severity metadata:
```json
[
  {
    "drug_a": "Warfarin",
    "drug_b": "Ibuprofen",
    "severity": "MAJOR",
    "mechanism": "NSAIDs inhibit platelet aggregation and may cause gastrointestinal mucosal damage, exacerbating bleeding risks associated with anticoagulants.",
    "recommendation": "Avoid combination. Consider Acetaminophen for mild-to-moderate analgesia if not otherwise contraindicated."
  },
  {
    "drug_a": "Sildenafil",
    "drug_b": "Nitroglycerin",
    "severity": "CONTRAINDICATED",
    "mechanism": "Potentiation of nitric oxide-mediated vasodilation causing severe, potentially fatal hypotension.",
    "recommendation": "Absolute contraindication. Do not administer."
  }
]
```

### 3.2 `drug_interactions_drugbank.csv`
Tabular dataset sourced from DrugBank reference data, queried via SQL/DataFrame:
| Column | Type | Description |
|---|---|---|
| `drug_1` | string | Generic name of primary medication |
| `drug_2` | string | Generic name of secondary medication |
| `severity` | string | `CONTRAINDICATED` / `MAJOR` / `MODERATE` / `MINOR` |
| `description` | string | Clinical pharmacology interaction summary |
| `evidence_level` | string | FDA Black Box / Clinical Trial / Case Report |

### 3.3 `homecare_protocols.json`
Standardized clinical self-care guidelines indexed by condition:
```json
[
  {
    "condition": "Acute Viral Pharyngitis (Sore Throat)",
    "safe_home_care": [
      "Warm saline gargles (1/2 tsp salt in 8 oz warm water)",
      "Adequate oral hydration with warm broths or herbal teas",
      "Humidity inhalation via cool-mist humidifier"
    ],
    "medication_guidance": "Acetaminophen or Ibuprofen (only if drug checker confirms no contraindications)",
    "escalation_red_flags": [
      "Inability to swallow saliva or open mouth (trismus)",
      "High fever lasting > 3 days",
      "Stridor or difficulty breathing"
    ]
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

### 4.3 Server & Integration Architecture (`serve.py`)
- Built exclusively with Python standard library (`http.server`), requiring zero additional runtime frameworks.
- Exposes static HTML/CSS/JS at `http://localhost:8000`.
- Implements a RESTful `/api/triage` endpoint that directly invokes `run_agent(query)` from `main.py` while providing graceful client-side heuristic fallbacks if disconnected.

---

## 5. Judging Contract & CLI Specification

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
        "args": {"text": "I feel dizzy and took lisinopril and potassium"},
        "observation": "Extracted symptoms: Presyncope. Medications: Lisinopril, Potassium chloride."
      },
      {
        "thought": "Check for hyperkalemia risk between ACE inhibitor and Potassium",
        "tool": "check_drug_interactions",
        "args": {"drugs": ["Lisinopril", "Potassium chloride"]},
        "observation": "SEVERITY: MAJOR. Concomitant use increases risk of severe hyperkalemia."
      }
    ]
  }
  ```
- **Logging Rule**: All diagnostic logs, step traces, and thoughts during non-json mode or debugging go to `stderr`.

---

## 6. Scoring Matrix Mapping

| Score Category | Points | How This Project Wins Top Score |
|---|---|---|
| **Agentic Architecture & Autonomy** | **40 pts** | • Full ReAct cycle with dynamic planning.<br>• Chooses tools iteratively based on prior observations.<br>• Self-corrects when tool calls fail or inputs are ambiguous.<br>• Loop-prevention guard and step-budget enforcement. |
| **Domain Utility & Execution** | **30 pts** | • Real clinical data (`interactions.json`, DrugBank CSV).<br>• Accurate pharmacological mechanism reporting.<br>• Realistic 3-tier urgency classification (Green/Yellow/Red).<br>• Zero hardcoded answers. |
| **Code Hygiene & System Design** | **20 pts** | • Strict modular architecture: `agent/`, `tools/`, `config/`, `data/`, `frontend/`.<br>• Strict compliance with judges' `--json` contract.<br>• Offline unit tests covering parsing, interaction checks, and executor loops.<br>• Comprehensive documentation and immediate runnability from README. |
| **Presentation & Live Demo** | **10 pts** | • Tactile Claymorphism UI (Navy Blue & Warm Beige) with real-time pipeline visualizer.<br>• Monospace ReAct trace inspector for live verification.<br>• One-click clinical scenario switcher for presentation flow.<br>• Complete technical Q&A preparation for all team members. |

---

## 7. Team Q&A & Defense Cheatsheet

1. **Why did you build both a CLI and a Claymorphism frontend?**  
   *Answer*: The AgentX evaluation harness tests headless CLI execution (`python main.py --json "..."`) via automated scripts, so strict CLI compliance is non-negotiable. The Claymorphism frontend (Navy & Beige) was engineered specifically for the live judging presentation to visually prove the 4-stage ReAct pipeline, show real-time Thought-Action-Observation traces, and let judges interact with real clinical scenarios.

2. **Does the UI require Node.js, React, or heavy npm dependencies to run?**  
   *Answer*: No. The UI is built with zero runtime dependencies using clean modern HTML5, CSS3 claymorphism tokens, and vanilla JavaScript. It is served instantly by Python's built-in standard library (`python serve.py`), meaning any judge can run it immediately without `npm install` headaches.

3. **How does the frontend communicate with the agent backend?**  
   *Answer*: `serve.py` routes asynchronous `POST /api/triage` calls into `main.py`'s `run_agent()` executor. If the server is run offline or during network dropouts, the frontend includes client-side fallback heuristics so the demo never hangs or crashes during judging.
