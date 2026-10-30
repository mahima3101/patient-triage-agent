"""Tool registry. To add a tool: subclass Tool in a new file, then add it to build_tools()."""


class Tool:
    name = "tool"
    description = ""
    args_doc = "{}"

    def execute(self, **kwargs):
        raise NotImplementedError


def build_tools():
    from tools.calculator import Calculator
    from tools.data_query import ListFiles, ReadFile, SqlQuery
    from tools.drug_interaction import DrugInteractionChecker
    from tools.protocol_search import HomeCareProtocolSearch
    from tools.symptom_parser import SymptomMedicalParser
    from tools.urgency_classifier import UrgencyClassifier
    from tools.web_search import WebSearch

    tools = [
        SymptomMedicalParser(),
        DrugInteractionChecker(),
        HomeCareProtocolSearch(),
        UrgencyClassifier(),
        ListFiles(),
        ReadFile(),
        SqlQuery(),
        Calculator(),
        WebSearch(),
    ]
    return {t.name: t for t in tools}
