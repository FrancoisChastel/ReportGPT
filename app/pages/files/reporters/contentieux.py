from pages.files.reporters.reporter_manager import ReportableFile, FileGroup
from langchain_openai import OpenAI, ChatOpenAI

import pandas as pd
import numpy as np


class ContentieuxParStatut(ReportableFile):
    file_path = "vol_contentieux_par_statut.csv"
    title = "Volume de contentieux par statut"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        vol_contentieux_par_statut = (
            file_group.amr.groupby(["ETAT_DECLARATION", "EXERCICE_COMPTABLE"])
            .size()
            .reset_index(name="count")
        )
        vol_contentieux_par_statut.to_csv(self.file_path)
        return self.file_path


class ContentieuxParEtat(ReportableFile):
    file_path = "montant_contentieux_par_etat.csv"
    title = "Montant des contentieux selon leur état"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        montant_contentieux_par_etat = (
            file_group.recours.groupby("Etat")["Droit Simple"]
            .sum()
            .reset_index(name="Montant couvert")
        )
        montant_contentieux_par_etat.to_csv(self.file_path)
        return self.file_path


class ContentieuxParImpots(ReportableFile):
    file_path = "montant_contentieux_par_type_impot.csv"
    title = "Montant des contentieux par type d'impôt par année"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        montant_contentieux_par_type_impot = file_group.recours[
            [
                "Impôt",
                "Exercice",
                "Etat",
                "Droit Simple",
                "Pénalité",
                "Majoration",
                "Frais",
            ]
        ]
        montant_contentieux_par_type_impot = (
            montant_contentieux_par_type_impot.groupby(["Exercice", "Impôt", "Etat"])
            .sum(["Droit Simple", "Pénalité", "Majoration", "Frais"])
            .reset_index()
        )
        montant_contentieux_par_type_impot.to_csv(self.file_path)
        return self.file_path


class DegrevementParEmissions(ReportableFile):
    file_path = "degrevements_recourvements.csv"
    title = "Dégrèvements et recouvrements par rapport aux émissions."

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        deg_rec_par_rapport_emissions = (
            file_group.amr.groupby(pd.Grouper(key="EXERCICE_COMPTABLE"))
            .agg(
                {
                    "DROIT_SIMPLE_DEGREVE": "sum",
                    "PENALITE_DEGREVE": "sum",
                    "MAJORATION_DEGREVE": "sum",
                    "FRAIS_DEGREVE": "sum",
                    "DROIT_SIMPLE_PAYE": "sum",
                    "PENALITE_PAYE": "sum",
                    "MAJORATION_PAYE": "sum",
                    "FRAIS_PAYE": "sum",
                    "DROIT_SIMPLE": "sum",
                    "PENALITE": "sum",
                    "MAJORATION": "sum",
                    "FRAIS_POURSUITE": "sum",
                }
            )
            .reset_index()
        )

        deg_rec_par_rapport_emissions["RECOUVREMENT"] = (
            deg_rec_par_rapport_emissions["DROIT_SIMPLE_PAYE"]
            + deg_rec_par_rapport_emissions["PENALITE_PAYE"]
            + deg_rec_par_rapport_emissions["MAJORATION_PAYE"]
            + deg_rec_par_rapport_emissions["FRAIS_PAYE"]
        )
        deg_rec_par_rapport_emissions["DEGREVEMENT"] = (
            deg_rec_par_rapport_emissions["DROIT_SIMPLE_DEGREVE"]
            + deg_rec_par_rapport_emissions["PENALITE_DEGREVE"]
            + deg_rec_par_rapport_emissions["MAJORATION_DEGREVE"]
            + deg_rec_par_rapport_emissions["FRAIS_DEGREVE"]
        )
        deg_rec_par_rapport_emissions["EMISSIONS"] = (
            deg_rec_par_rapport_emissions["DROIT_SIMPLE"]
            + deg_rec_par_rapport_emissions["PENALITE"]
            + deg_rec_par_rapport_emissions["MAJORATION"]
            + deg_rec_par_rapport_emissions["FRAIS_POURSUITE"]
        )

        deg_rec_par_rapport_emissions

        deg_rec_par_rapport_emissions.to_csv(self.file_path)
        return self.file_path


class ConformiteFiscale(ReportableFile):
    file_path = "conformite_fiscale_declarations.csv"
    title = "Conformité fiscale des déclarations en %. Nnombre de déclarations effectuées avant la date d'échéance."

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        conformite_fiscale_declarations = (
            (
                file_group.declarations["DATE_DECLARATION"]
                < file_group.declarations["ECHEANCE_DECLARATION"]
            ).sum()
            / len(file_group.declarations)
            * 100
        )
        pd.DataFrame(np.array([conformite_fiscale_declarations])).to_csv(self.file_path)
        return self.file_path
