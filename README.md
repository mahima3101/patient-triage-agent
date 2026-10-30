# 🏥 AURA: Autonomous Patient Triage & Pharmacovigilance Interaction Checker

<p align="center">
  <img src="https://img.shields.io/badge/AgentX%20Challenge-2026%20SRMIST-152238?style=for-the-badge&logo=target" alt="AgentX 2026" />
  <img src="https://img.shields.io/badge/Track-Healthcare%20%26%20Biotech-10B981?style=for-the-badge&logo=heartbeat" alt="Track" />
  <img src="https://img.shields.io/badge/Model-Gemini%203.5%20Flash-4285F4?style=for-the-badge&logo=google" alt="Gemini" />
  <img src="https://img.shields.io/badge/Tests-19%2F19%20Passing-2E7D32?style=for-the-badge&logo=checkmarx" alt="Tests" />
  <img src="https://img.shields.io/badge/UI-Claymorphism%20(Navy%20%26%20Beige)-1E2E4A?style=for-the-badge" alt="UI" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="License" />
</p>

> **"Symptoms and current medications in, a clinical triage summary with urgency out."**  
> An autonomous ReAct clinical decision-support agent designed to prevent adverse drug events, normalize unstructured patient complaints, and classify triage urgency using verified medical databases.

---

## 📑 Table of Contents

- [Executive Summary](#-executive-summary)
- [The 4-Pillar Clinical Pipeline](#-the-4-pillar-clinical-pipeline)
- [System Architecture](#-system-architecture)
- [Interactive Claymorphism Frontend](#-interactive-claymorphism-frontend)
- [Quickstart Guide](#-quickstart-guide)
- [Judging Evaluation Contract (`--json`)](#-the-judges-evaluation-contract---json)
- [Real-World Benchmark Scenarios](#-real-world-benchmark-scenarios)
- [Repository Structure](#-repository-structure)
- [Automated Verification & Test Suite](#-automated-verification--test-suite)
- [100-Point Scoring Rubric Mapping](#-100-point-scoring-rubric-mapping)
- [Medical Disclaimer](#-medical-disclaimer)

---

## 📌 Executive Summary

Over **1.3 million emergency department visits** occur annually in the United States alone due to preventable Adverse Drug Events (ADEs) and unrecognized drug-drug interactions. In outpatient, telehealth, and emergency intake settings, patient complaints are frequently delivered in ambiguous, non-technical language (e.g., *"my head is pounding and I took my blood thinner with an Advil"*).

**AURA** solves this challenge through an autonomous **ReAct (Reasoning + Acting)** multi-step agent that:
1. Translates conversational patient complaints into standardized clinical concepts (**SNOMED-CT / ICD-10**) and flags immediate life threats.
2. Cross-references active medications against **222,697 DrugBank interaction records** ([`DDI_data.csv`](file:///c:/Users/sanja/Desktop/Sanjay/Neth2/data/DDI_data.csv)) and verified clinical contraindications ([`interactions.json`](file:///c:/Users/sanja/Desktop/Sanjay/Neth2/data/interactions.json)).
3. Evaluates evidence-based supportive care protocols ([`homecare_protocols.json`](file:///c:/Users/sanja/Desktop/Sanjay/Neth2/data/homecare_protocols.json)), automatically withholding home-care if contraindications exist.
4. Stratifies clinical acuity into a validated 3-tier urgency rating:
   - 🟢 **GREEN**: Routine / Supportive self-care with verified home protocol.
   - 🟡 **YELLOW**: Urgent / Primary care or telemedicine review within 12–24 hours.
   - 🔴 **RED**: Immediate Emergency / EMS dispatch or emergency room evaluation (0–1 hour).

---

## ⚡ The 4-Pillar Clinical Pipeline

```mermaid
flowchart LR
    A["1. Symptom Normalization\n(Colloquial -> SNOMED/ICD-10)"] --> B["2. Pharmacovigilance Engine\n(interactions.json + 222k DrugBank)"]
    B --> C["3. Protocol Search & Guard\n(homecare_protocols.json)"]
    C --> D["4. Triage Stratification\n(Green / Yellow / Red)"]
```

### Pillar 1: Parse Symptoms into Medical Terms
- Standardizes patient vernacular (*"pounding head and room spinning"*) into formal clinical entities (*Cephalea [ICD-10: R51.9]*, *Presyncope/Vertigo [ICD-10: R42]*).
- Automatically screens for immediate emergency red flags (e.g., crushing chest pressure, unilateral facial droop, dyspnea, melena, thunderclap headache).

### Pillar 2: Flag Contraindications via Local Drug Tools
- Scans `interactions.json` and 222,697 DrugBank interaction pairs in `DDI_data.csv`.
- Normalizes brand names to generic entities (`Coumadin` ➔ `Warfarin`, `Advil/Motrin` ➔ `Ibuprofen`, `Viagra` ➔ `Sildenafil`, `Nitrostat` ➔ `Nitroglycerin`).
- Identifies pharmacodynamic and pharmacokinetic mechanisms (e.g., synergistic cGMP elevation, COX-1 platelet inhibition, CYP2C19 competitive inhibition).
- Flags pairwise severity: `CONTRAINDICATED`, `MAJOR`, `MODERATE`, or `MINOR`.

### Pillar 3: Search Recent Home-Care Protocols
- Retrieves condition-specific clinical protocols from `homecare_protocols.json` (with DuckDuckGo web search fallback for rare presentations).
- **Safety Boundary Enforcement**: If major contraindications or critical red-flag symptoms are present, supportive home-care is **strictly suspended**, preventing dangerous self-treatment.

### Pillar 4: Classify Urgency (Green / Yellow / Red)
- Synthesizes symptom acuity, contraindication risk, and patient factors into an actionable clinical triage rating complete with timeframe directives and emergency instructions.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph UI ["1. Presentation Layer (frontend/ + serve.py)"]
        ClayUI["Claymorphism Dashboard (Navy Blue & Warm Beige)\n- Interactive Intake & Symptom Chips\n- Dynamic Medication Tagger\n- 4-Stage Live Progress Engine\n- Monospace ReAct Trace Drawer"]
        Server["serve.py (Python stdlib http.server)\n- Zero runtime pip/npm dependencies\n- /api/triage REST Bridge"]
    end

    subgraph CLI ["2. Automated Headless Driver (main.py)"]
        Harness["Judges' Headless Contract\n--json (single-line stdout JSON, isolated stderr)"]
    end

    subgraph AgentBrain ["3. Agent Brain (agent/)"]
        PromptBuilder["Prompt Builder (prompt_builder.py)\nClinical Triage Specialist Persona + JSON Protocol"]
        Executor["ReAct Engine (core.py)\nThought -> Action -> Observation -> Decision\nLoop Guards (MAX_ITERATIONS = 8)"]
        LLMLayer["LLM Wrapper (llm.py)\nGoogle Gemini 3.5 Flash + Exponential Backoff\nScripted Intelligent DryRunLLM Fallback"]
    end

    subgraph ToolRegistry ["4. Specialized Clinical Tools (tools/)"]
        T1["SymptomMedicalParser (parse_symptoms)"]
        T2["DrugInteractionChecker (check_drug_interactions)"]
        T3["HomeCareProtocolSearch (search_protocol)"]
        T4["UrgencyClassifier (classify_urgency)"]
    end

    subgraph DataStore ["5. Clinical Data Tier (data/)"]
        D1[("interactions.json\nHigh-acuity pairwise contraindications")]
        D2[("DDI_data.csv\n222,697 DrugBank interaction records")]
        D3[("homecare_protocols.json\nVerified self-care guidelines")]
    end

    ClayUI <--> Server
    Server --> Executor
    Harness --> Executor

    Executor <--> PromptBuilder
    Executor <--> LLMLayer
    Executor -- Executes --> ToolRegistry

    T1 --> DataStore
    T2 <--> D1
    T2 <--> D2
    T3 <--> D3
    T4 --> Executor
```

---

## 🎨 Interactive Claymorphism Frontend

A custom-designed, tactile **Claymorphism** interface designed with a clinical **Navy Blue (`#152238`) & Warm Beige (`#F8F5EE`)** palette:

* **Dual-Layer Clay Elevation**: Soft diffused drop shadows combined with interior inset highlight reflections (`inset 2px 2px 4px rgba(255,255,255,0.9)`, `inset -3px -3px 6px rgba(180,160,140,0.25)`).
* **Patient Intake Console**: Natural-language narrative text box with quick-select symptom chips and interactive medication tag pills.
* **4-Step Pipeline Visualizer**: Live step-by-step indicator showing term parsing, drug interaction verification, protocol retrieval, and acuity classification.
* **Clinical Triage Decision Output**: Color-coded urgency hero banner (Red/Yellow/Green), standardized medical nomenclature badges, and pharmacological risk warnings.
* **Quick Clinical Presets**: One-click scenario switcher for live demo presentations:
  - 🔴 *Warfarin + NSAID Bleed Risk (Red)*
  - 🟡 *Lisinopril + Hyperkalemia (Yellow)*
  - 🟢 *Mild Tension Cephalea (Green)*
* **Live ReAct Execution Trace Inspector**: Dedicated terminal log drawer directly displaying the Thought -> Action -> Observation reasoning loop for judges and evaluators.

```bash
# Launch the built-in HTTP server (zero extra pip/npm dependencies required):
python serve.py
# Opens at http://localhost:8000
```

---

## 🚀 Quickstart Guide

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/himanshuraiml/agentx-starter.git
cd agentx-starter
python -m venv venv

# Activate Virtual Environment:
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and configure your API key:
```bash
cp .env.example .env
```
Inside `.env`:
```ini
GEMINI_API_KEY="your-google-ai-studio-api-key"
AGENTX_PROVIDER="gemini"
GEMINI_MODEL="gemini-3.5-flash"
```
*(Free Gemini API keys can be generated at [Google AI Studio](https://aistudio.google.com/apikey)).*

> [!NOTE]
> If you do not have an API key, the agent runs in full **`--dry-run` mode** simulating complete clinical reasoning loops across all benchmark scenarios.

---

## ⚖️ The Judges' Evaluation Contract (`--json`)

This repository strictly complies with the automated evaluation harness contract:

```bash
python main.py --json "Patient on Sildenafil reports chest tightness and took Nitroglycerin"
```

### Contract Guarantees:
1. **Single-Line Standard Output**: Emits **EXACTLY ONE JSON line** to `stdout`:
   ```json
   {"answer": "<Clinical Triage Synthesis>", "trace": [{"thought": "...", "tool": "...", "args": {...}, "observation": "..."}]}
   ```
2. **Strict Telemetry Isolation**: All debug logs, reasoning thoughts, and timing metrics are routed exclusively to `stderr`, guaranteeing clean stdout piping for automated evaluation tools like `jq`.
3. **Environment Agnostic**: Reads data dynamically from `AGENTX_DATA_DIR` (defaults to `./data`). No hardcoded paths or values.
4. **Crash Immunity**: Unhandled exceptions are caught and formatted as structured error JSON responses rather than throwing unhandled tracebacks.

---

## 🔬 Real-World Benchmark Scenarios

### Scenario 1: Fatal Hypotension Risk (🔴 RED Triage)
- **Input Query**: `"Patient taking Sildenafil reports chest tightness and took Nitroglycerin"`
- **Tool Trajectory**:
  1. `parse_symptoms`: Detects *Angina Pectoris / Acute Coronary Syndrome* (`CRITICAL` red flag).
  2. `check_drug_interactions`: Queries `interactions.json` for `Sildenafil + Nitroglycerin` ➔ Returns `CONTRAINDICATED` (synergistic cGMP accumulation causing profound hypotension).
  3. `search_protocol`: Identifies critical red flag ➔ Suspends home-care protocols.
  4. `classify_urgency`: Returns **🔴 RED (Immediate Emergency — 0 to 1 Hour)**.

### Scenario 2: Severe Hemorrhage Hazard (🔴 RED Triage)
- **Input Query**: `"Patient takes Warfarin, has severe headache and took Ibuprofen"`
- **Outcome**: Flagged as `MAJOR / CONTRAINDICATED`. NSAID-induced platelet inhibition on active anticoagulation creates acute risk of intracranial hemorrhage. Urgent ER referral required.

### Scenario 3: Hyperkalemia Conduction Risk (🟡 YELLOW Triage)
- **Input Query**: `"Patient on Lisinopril for hypertension has dry cough and is taking Potassium supplements"`
- **Outcome**: Flagged as `MODERATE-MAJOR INTERACTION`. Aldosterone suppression by ACE inhibitors reduces renal potassium excretion. Potassium supplements withheld; clinic visit within 12–24h recommended.

### Scenario 4: Benign Tension Cephalalgia (🟢 GREEN Triage)
- **Input Query**: `"Mild dull headache around temples after working at computer, no fever, taking Multivitamin"`
- **Outcome**: Zero drug contraindications detected. Verified home-care protocol returned: hydration (500mL), screen rest (20-20-20 rule), and cold compress. Classified as **🟢 GREEN**.

---

## 📂 Repository Structure

```
.
├── main.py                       # Headless CLI entry point complying with judges' contract
├── serve.py                      # Claymorphism UI web server & /api/triage REST bridge
├── README.md                     # Project overview, quickstart, and evaluation guide
├── architecture.md               # Detailed system architecture, Mermaid diagrams, and failover logic
├── project_context.md            # Clinical background, data schemas, and judge defense cheatsheet
├── implementation_plan.md        # 6-phase engineering plan and rubric verification checklist
├── frontend/
│   └── index.html                # Claymorphism SPA (Navy Blue & Warm Beige palette)
├── agent/
│   ├── __init__.py
│   ├── core.py                   # ReAct loop engine, loop guards, error recovery
│   ├── llm.py                    # Multi-provider LLM interface (Gemini/Groq) with exponential retry
│   └── prompt_builder.py         # Clinical Triage & Pharmacovigilance system prompt
├── config/
│   └── __init__.py               # Runtime settings (MAX_ITERATIONS = 8, DATA_DIR)
├── data/
│   ├── DDI_data.csv              # 222,697 DrugBank pairwise interaction records (14.9 MB)
│   ├── interactions.json         # High-acuity contraindications, mechanisms, and brand aliases
│   └── homecare_protocols.json   # Verified clinical self-care protocols (ICD-10 / SNOMED)
├── tools/
│   ├── __init__.py               # Tool registry (build_tools)
│   ├── symptom_parser.py         # Standardizes complaints to SNOMED-CT / ICD-10 & red flags
│   ├── drug_interaction.py       # Indexed lookups over DDI_data.csv & interactions.json
│   ├── protocol_search.py        # Protocol retrieval with safety boundary overrides
│   ├── urgency_classifier.py     # 3-tier clinical acuity triage engine
│   ├── data_query.py             # File and SQL query primitives
│   └── web_search.py             # DuckDuckGo clinical web search fallback
└── tests/
    ├── test_medical_tools.py     # 9 unit tests for medical tools and safety boundaries
    ├── test_agent.py             # 6 tests for ReAct loop, iteration caps, and JSON handling
    └── test_integration_scenarios.py # 4 end-to-end integration tests & strict CLI contract test
```

---

## 🧪 Automated Verification & Test Suite

The repository includes **19 automated unit and integration tests** executable offline without API keys:

```bash
# Run all tests via unittest discovery:
python -m unittest discover tests
```

### Test Suite Summary

| Test Module | Tests | Execution | Description |
|---|:---:|:---:|---|
| [`tests/test_medical_tools.py`](file:///c:/Users/sanja/Desktop/Sanjay/Neth2/tests/test_medical_tools.py) | **9** | **PASSED** | Normalization of symptoms, emergency red flags, DrugBank CSV & JSON queries, brand matching, safety boundary overrides, and urgency classification. |
| [`tests/test_agent.py`](file:///c:/Users/sanja/Desktop/Sanjay/Neth2/tests/test_agent.py) | **6** | **PASSED** | ReAct executor loop, JSON fence stripping, error-to-observation recovery, repeat-action guards, and max iteration limits. |
| [`tests/test_integration_scenarios.py`](file:///c:/Users/sanja/Desktop/Sanjay/Neth2/tests/test_integration_scenarios.py) | **4** | **PASSED** | Full end-to-end execution of Red, Yellow, and Green benchmark queries, and strict single-line JSON stdout verification. |
| **Total** | **19** | **100% OK** | **Zero failures, zero errors.** |

---

## 📊 100-Point Scoring Rubric Mapping

| Rubric Dimension | Pts | Technical Implementation in This Repository |
|---|:---:|---|
| **Agentic Architecture & Autonomy** | **40** | • Multi-step autonomous ReAct loop (`Thought -> Action -> Observation -> Decision`).<br>• Dynamic tool selection adapting to intermediate observations.<br>• Automatic error recovery (exceptions converted to observations for model self-correction).<br>• Loop prevention guards (`MAX_SAME_TOOL_CALLS = 2`) and iteration bounds (`MAX_ITERATIONS = 8`). |
| **Domain Utility & Execution** | **30** | • Real clinical data: **222,697 DrugBank interaction records** (`DDI_data.csv`) and `interactions.json`.<br>• Accurate pharmacological mechanisms (COX-1 inhibition, cGMP vasodilation, CYP2C19 inhibition).<br>• Standardized clinical terminologies (ICD-10, SNOMED-CT).<br>• Zero hardcoded answers. |
| **Code Hygiene & System Design** | **20** | • Strict decoupling between Agent Brain (`agent/`), Tool Registry (`tools/`), Data Tier (`data/`), and CLI Driver (`main.py`).<br>• Verified judges' contract (`--json`) with isolated `stderr` logging.<br>• 19 passing unit & integration tests.<br>• Self-contained, zero-dependency local execution directly from README. |
| **Presentation & Live Demo** | **10** | • Tactile Claymorphism UI (Navy Blue & Warm Beige) with real-time 4-step pipeline visualizer.<br>• Embedded monospace ReAct execution trace drawer for live judge inspection.<br>• One-click benchmark clinical presets for seamless presentation flow. |

---

## 🛡️ Medical Disclaimer

*AURA is an autonomous engineering demonstration and clinical decision-support research prototype built for the AgentX Challenge 2026. It is designed to assist healthcare personnel and researchers and does not constitute a substitute for professional clinical judgment, diagnosis, or treatment. In a medical emergency, always call local emergency medical services (911/112) immediately.*
