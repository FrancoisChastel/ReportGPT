from pages.files.reporters.reporter_manager import ReportableFile, FileGroup
from langchain_openai import OpenAI, ChatOpenAI

import pandas as pd


class PaiementsAttendus(ReportableFile):
    file_path = "paiements_attendus.csv"
    title = "Somme des paiements attendus sur la période"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        somme_paiements_attendus = (
            file_group.declarations.groupby(
                pd.Grouper(key="DATE_DECLARATION", freq="W-Mon")
            )["MONTANT_DROIT"]
            .sum()
            .reset_index()
        )
        somme_paiements_attendus.sort_values(
            by="DATE_DECLARATION", ascending=True, inplace=True
        )
        somme_paiements_attendus.to_csv(self.file_path)
        return self.file_path


class RecettesParImpots(ReportableFile):
    file_path = "recettes_par_impots.csv"
    title = "Montant des recettes par impôt par année"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        montant_recettes_par_impot = (
            file_group.quittances.groupby(["IMPOT", "ANNEE"])
            .sum("MONTANT")
            .reset_index()[["ANNEE", "IMPOT", "MONTANT"]]
            .sort_values(["ANNEE", "MONTANT"], ascending=[True, False])
            .reset_index()
            .drop(columns="index")
        )
        montant_recettes_par_impot.to_csv(self.file_path)
        return self.file_path


class EvolutionContribuablesParDirection(ReportableFile):
    file_path = "evo_enregistrements_contribuables_par_direction.csv"
    title = "Evolution du nombre de contribuables non-gelés enregistrés auprès des directions"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        evo_enregistrements_contribuables_par_direction = (
            file_group.contribuables.loc[file_group.contribuables["GEL2"] != "Gelé"][
                ["DATE_IMMATRICULATION", "DIRECTION", "NIF"]
            ]
            .groupby([pd.Grouper(key="DATE_IMMATRICULATION", freq="M"), "DIRECTION"])
            .count()
        )
        evo_enregistrements_contribuables_par_direction.to_csv(self.file_path)
        return self.file_path


class DoitsSimplesPayes(ReportableFile):
    file_path = "droits_simples_vs_droits_simples_payes.csv"
    title = "Montants des droits simples par rapport aux droits simples payes"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        droits_simples_vs_droits_simples_payes = (
            file_group.amr[["EXERCICE_COMPTABLE", "DROIT_SIMPLE", "DROIT_SIMPLE_PAYE"]]
            .groupby("EXERCICE_COMPTABLE")
            .sum()
        )
        droits_simples_vs_droits_simples_payes.to_csv(self.file_path)
        return self.file_path


class PaimentParTypeParPeriode(ReportableFile):
    file_path = "montant_paiements_par_type_par_periode.csv"
    title = "Montant et taux des paiements par type"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        montant_paiements_par_type_par_periode = (
            file_group.quittances[["TYPE_DECLARATION", "MONTANT", "DATE_PAIEMENT"]]
            .groupby([pd.Grouper(key="DATE_PAIEMENT", freq="M"), "TYPE_DECLARATION"])
            .sum()
        )
        montant_paiements_par_type_par_periode.to_csv(self.file_path)
        return self.file_path
