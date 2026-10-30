# Implementation Plan: AURA Patient Triage & Interaction Checker

**Target Challenge**: AgentX Challenge 2026 - Healthcare & Biotech Track  
**Objective**: Transform the starter repo into a production-grade, 100-point scoring Patient Triage & Drug Interaction Checker agent complying with all judging rules, backed by an interactive Navy Blue & Warm Beige Claymorphism UI.

---

## 1. Overview & Architecture Strategy

The implementation strictly decouples:
1. **Clinical Data Tier (`data/`)**: Verified datasets (`interactions.json`, `drug_interactions_drugbank.csv`, `homecare_protocols.json`).
2. **Deterministic Tool Registry (`tools/`)**: Modular clinical tools implementing symptom extraction, drug interaction lookups, home-care protocol search, and urgency triage.
3. **Agent Brain (`agent/`)**: ReAct autonomous reasoning engine (`AgentExecutor`), clinical triage system prompt builder, and resilient LLM wrapper (Gemini / Groq with retry logic).
4. **Driver & Harness (`main.py`)**: Strict compliance with `--json` single-line stdout contract and rich stderr debugging traces.
5. **Claymorphism Frontend & Server (`frontend/`, `serve.py`)**: Tactile Navy Blue & Warm Beige single-page application with zero-dependency Python server bridging to `run_agent()`.

---

## 2. Phase-by-Phase Roadmap

### Phase 1: Data Assets Setup (`data/`) — [COMPLETED]
- [x] **Task 1.1: Integrated `data/DDI_data.csv`**
  - Ingested 222,697 real DrugBank interaction records (`drug1_name`, `drug2_name`, `interaction_type`, `drug1_id`, `drug2_id`).
- [x] **Task 1.2: Created `data/interactions.json`**
  - High-acuity pairwise contraindications with severity ratings (`CONTRAINDICATED`, `MAJOR`, `MODERATE`), pharmacodynamic/pharmacokinetic mechanisms, brand aliases, and clinical recommendations.
- [x] **Task 1.3: Created `data/homecare_protocols.json`**
  - Evidence-based clinical home-care protocols with ICD-10 and SNOMED concept codes, non-pharmacological directives, OTC guidance, and critical red-flag escalation triggers.

### Phase 2: Clinical Tool Suite Development (`tools/`) — [COMPLETED]
- [x] **Task 2.1: `tools/symptom_parser.py` (`SymptomMedicalParser`)**
  - Standardizes colloquial patient complaints into formal clinical nomenclature (SNOMED-CT / ICD-10).
  - Flags critical red-flag emergency symptoms (crushing chest pain, focal weakness, thunderclap cephalea, melena).
- [x] **Task 2.2: `tools/drug_interaction.py` (`DrugInteractionChecker`)**
  - Cross-references input medications against `interactions.json` and 222,697 DrugBank interaction pairs in `DDI_data.csv`.
  - Supports brand name aliases and symptom contraindications; sub-second lookup performance.
- [x] **Task 2.3: `tools/protocol_search.py` (`HomeCareProtocolSearch`)**
  - Searches verified supportive home-care protocols from `homecare_protocols.json`.
  - Enforces clinical safety boundaries: withholds home-care if major contraindications or red flags are present.
- [x] **Task 2.4: `tools/urgency_classifier.py` (`UrgencyClassifier`)**
  - Stratifies acuity into validated 3-tier clinical rating: GREEN, YELLOW, or RED with clinical rationale and action plan.
- [x] **Task 2.5: Registered in `tools/__init__.py` & Verified with Unit Tests (`tests/test_medical_tools.py`)**
  - 9 automated unit tests verifying parsing, contraindication flagging, safety blocking, and urgency classification.

### Phase 3: Agent Brain & Prompt Engineering (`agent/`) — [COMPLETED]
- [x] **Task 3.1: Specialize `agent/prompt_builder.py`**
  - Updated `ROLE` to board-certified Clinical Triage & Pharmacovigilance specialist.
  - Injected structured 4-step diagnostic protocol: `parse_symptoms` ➔ `check_drug_interactions` ➔ `search_protocol` ➔ `classify_urgency`.
  - Enforced JSON-only turn format and strict ground-truth tool reliance.
- [x] **Task 3.2: Enhance `agent/core.py`**
  - Clinical nudge prompt on ungrounded answers.
  - Repeat-guard and tool error recovery converting exceptions into actionable observations.
  - Hard reasoning iteration cap (`MAX_ITERATIONS = 8`).
- [x] **Task 3.3: Intelligent Dry-Run Simulator in `agent/llm.py`**
  - Scripted `DryRunLLM` simulating complete 4-stage ReAct trajectories for RED, YELLOW, and GREEN benchmark scenarios.
  - Verified with `--json` judges' contract to output valid JSON single-line answer + full execution trace.

### Phase 4: Driver & Harness Verification (`main.py`) — [COMPLETED]
- [x] **Task 4.1: Validate Judges' Contract**
  - Confirmed `python main.py --json "<query>"` emits strictly one JSON line to `stdout`: `{"answer": "...", "trace": [...]}`.
  - Ensured all human logs and trace displays are routed exclusively to `stderr` in headless mode.
- [x] **Task 4.2: Robust Exception Shielding**
  - Shielded against unhandled runtime errors with UTF-8 stream reconfiguration and safe fallback responses.

### Phase 5: Comprehensive Testing & Validation — [COMPLETED]
- [x] **Task 5.1: Unit Tests (`tests/test_medical_tools.py`)**
  - 9/9 tests passed for `parse_symptoms`, `check_drug_interactions`, `search_protocol`, and `classify_urgency`.
- [x] **Task 5.2: End-to-End ReAct Test (`tests/test_agent.py`)**
  - 6/6 tests passed for JSON parsing, iteration caps, tool error recovery, and CLI contract.

### Phase 6: Claymorphism Frontend & Live Demo Suite (`frontend/`, `serve.py`)
- [x] **Task 6.1: Tactile Claymorphism SPA (`frontend/index.html`)**
  - Navy Blue (`#152238`) & Warm Beige (`#F8F5EE`) palette with dual-layer soft outer and inner inset shadows.
  - Patient Intake Console: Narrative input box with symptom quick-select chips + medication tag manager.
  - 4-Stage Pipeline Progress Engine (`Parse Terms` -> `Drug Checker` -> `Protocols` -> `Triage Urgency`).
  - Clinical Output Cards: Urgency hero banner (Red/Yellow/Green), standardized medical terms, contraindication alerts, and care directives.
  - Monospace ReAct Trace Inspector for real-time judge log review.
- [x] **Task 6.2: Lightweight Python Server & API Bridge (`serve.py`)**
  - Python standard library HTTP server (`http.server`) running at `http://localhost:8000`.
  - Exposes `/api/triage` endpoint calling `run_agent(query)` from `main.py`.
  - Zero external pip dependencies required.
- [x] **Task 6.3: Presentation Demo Presets & Scenarios Script**
  - Scenario 1 (RED): Warfarin patient taking Ibuprofen (Severe hemorrhage hazard).
  - Scenario 2 (YELLOW): Lisinopril patient on Potassium Chloride (Hyperkalemia hazard).
  - Scenario 3 (GREEN): Mild tension headache (Digital strain / hydration protocol).

---

## 3. Verification Checklist Against Rubric

| Rubric Requirement | Verification Mechanism | Status |
|---|---|---|
| **Agentic Autonomy (40 pts)** | Multi-step ReAct loop with dynamic planning, tool retries, and step cap | Ready for impl |
| **Domain Utility (30 pts)** | Real `interactions.json` & DrugBank CSV queries; realistic pharmacology | Ready for impl |
| **Code Hygiene (20 pts)** | Decoupled modular design (`agent/`, `tools/`, `frontend/`), judges' `--json` contract | Ready for impl |
| **Presentation (10 pts)** | Navy & Beige Claymorphism UI, real-time pipeline visualizer, live trace inspector | **Complete** |
