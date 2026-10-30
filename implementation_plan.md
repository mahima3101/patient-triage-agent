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

### Phase 2: Clinical Tool Suite Development (`tools/`)
- [ ] **Task 2.1: `tools/symptom_parser.py` (`SymptomMedicalParser`)**
  - Maps natural language complaints to standardized clinical terms.
  - Flags vital signs or red-flag symptom markers (e.g., crushing chest pain, dyspnea, focal weakness).
- [ ] **Task 2.2: `tools/drug_interaction.py` (`DrugInteractionChecker`)**
  - Reads `interactions.json` and `drug_interactions_drugbank.csv` from `AGENTX_DATA_DIR` (fallback to `./data`).
  - Supports fuzzy matching for generic and brand names (e.g., Advil -> Ibuprofen, Coumadin -> Warfarin).
  - Returns highest interaction severity, clinical rationale, and alternative medications.
- [ ] **Task 2.3: `tools/protocol_search.py` (`HomeCareProtocolSearch`)**
  - Searches local `homecare_protocols.json` by condition keyword.
  - Incorporates web search tool fallback if local protocol is unavailable.
  - Safety check: Disallows home-care if major drug contraindications or red-flag symptoms are present.
- [ ] **Task 2.4: `tools/urgency_classifier.py` (`UrgencyClassifier`)**
  - Algorithmic urgency scoring mapping combined factors into **Green**, **Yellow**, or **Red**.
- [ ] **Task 2.5: Register Tools in `tools/__init__.py`**
  - Integrate new tools into `build_tools()`, exposing clean documentation and argument schemas to the agent.

### Phase 3: Agent Brain & Prompt Engineering (`agent/`)
- [ ] **Task 3.1: Specialize `agent/prompt_builder.py`**
  - Update `ROLE` to a board-certified Clinical Triage & Pharmacovigilance specialist.
  - Add explicit multi-step planning instructions:
    1. Parse symptoms into medical terms.
    2. Check active drug contraindications.
    3. Query appropriate care protocols.
    4. Stratify urgency into Green / Yellow / Red.
  - Enforce JSON-only formatting and ground-truth data usage.
- [ ] **Task 3.2: Enhance `agent/core.py`**
  - Verify loop-prevention guards and retry handling.
  - Ensure error trace capturing for judge inspection.
- [ ] **Task 3.3: Dry-Run Support in `agent/llm.py`**
  - Update `DryRunLLM` to simulate a complete clinical triage trajectory with realistic thoughts, tool calls, and observations for offline demonstrations.

### Phase 4: Driver & Harness Verification (`main.py`)
- [ ] **Task 4.1: Validate Judges' Contract**
  - Ensure `python main.py --json "<query>"` emits strictly one JSON line to `stdout`:
    `{"answer": "...", "trace": [...]}`.
  - Ensure all human logs and trace displays are routed exclusively to `stderr`.
- [ ] **Task 4.2: Robust Exception Shielding**
  - Ensure unhandled exceptions return a clean fallback JSON answer rather than crashing with an exit code != 0.

### Phase 5: Comprehensive Testing & Validation
- [ ] **Task 5.1: Unit Tests (`tests/test_medical_tools.py`)**
  - Test `DrugInteractionChecker` with known contraindication pairs (Warfarin + Ibuprofen -> MAJOR).
  - Test `SymptomMedicalParser` normalization.
  - Test `UrgencyClassifier` boundary cases (Red vs Yellow vs Green).
- [ ] **Task 5.2: End-to-End ReAct Test (`tests/test_agent.py`)**
  - Run offline dry-run tests verifying that at least one data tool is called before emitting the final answer.
  - Verify JSON structure and trace integrity.

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
