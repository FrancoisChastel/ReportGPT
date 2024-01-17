from langchain_openai import OpenAI
from pages.files.reporters.reporter_manager import FileGroup
import openai

from pages.files.reporters.contentieux import (
    ContentieuxParEtat,
    ConformiteFiscale,
    ContentieuxParImpots,
    ContentieuxParStatut,
    DegrevementParEmissions,
)

from pages.files.reporters.incomes import (
    RecetteParImpots,
    ContentieuxParTypeImpots,
    PrincipauxContribuables,
    RecetteParTypeDeclaration,
    RecettesParDeclarations,
    DeclarationParDirection,
)

from pages.files.reporters.tax_population import (
    EvolutionContribuablesParDirection,
    DoitsSimplesPayes,
    PaiementsAttendus,
    PaimentParTypeParPeriode,
    RecettesParImpots,
)

reports = [
    # ContentieuxParEtat,
    # ConformiteFiscale,
    ContentieuxParImpots,
    # ContentieuxParStatut,
    # DegrevementParEmissions,
    RecetteParImpots,
    # ContentieuxParTypeImpots,
    PrincipauxContribuables,
    RecetteParTypeDeclaration,
    # RecettesParDeclarations,
    DeclarationParDirection,
    EvolutionContribuablesParDirection,
    DoitsSimplesPayes,
    # PaiementsAttendus,
    # PaimentParTypeParPeriode,
    # RecettesParImpots,
]


def InitializeReporter(
    declarations_path: str,
    contribuables_path: str,
    quittances_path: str,
    amr_path: str,
    recours_path: str,
    notifications_path: str,
    openai_api_key: str,
):
    reporters = []
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key, max_tokens=512)
    file_group = FileGroup(
        declarations_path,
        contribuables_path,
        quittances_path,
        amr_path,
        recours_path,
        notifications_path,
    )
    client = openai.OpenAI(api_key=openai_api_key)

    for report in reports:
        reporters.append(report(llm=llm, group=file_group, chat=client))
    return reporters
