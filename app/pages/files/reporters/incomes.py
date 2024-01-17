from pages.files.reporters.reporter_manager import ReportableFile, FileGroup
from langchain_openai import OpenAI, ChatOpenAI

import pandas as pd


nomenclature_impots = {
    "TAXE SUR LA VALEUR AJOUTEE": "TVA",
    "TAXE D’APPRENTISSAGE": "TA",
    "IMPOT SUR LES TRAITEMENTS ET SALAIRES": "ITS",
    "IMPOT MINIMUM FORFAITAIRE ": "IMF",
    "IMPOT SUR LES SOCIETES": "IS",
    "RETENUES A LA SOURCE": "RETENUES",
    "IMPOT SUR LE REVENU DES CAPITAUX MOBILIERS ": "IRCM",
    "(RETENU 15%) REGIME SIMPLIFIE D''IMPOSITION": "RSI",
    "BENEFICES INDUSTRIELS ET COMMERCIAUX FORFAIT": "BIC FORFAIT",
    "TAXE SUR LES OPERATIONS FINANCIERES": "TOF",
    "TAXE D AEROPORT A DESTINATION DE L ETRANGER": "TADE",
    "BENEFICES INDUSTRIELS ET COMMERCIAUX ": "BIC",
    "IMF PRECOMPTEE": "IMF PR",
    "IMPOT SUR LE REVENU FONCIER": "IRF",
    "DECLARATION PATENTE": "PATENTE",
    "IRF PRECOMPTEE": "IRF PR",
    "TAXE UNIQUE": "TU",
    "IMPOT SUR LES TRAITEMENTS ET SALAIRES REGIME EXCEPTIONNEL": "ITS EX",
    "IMPOT SUR LES BENEFICES RETENU A LA SOURCE REGIME GTA": "BIC GTA",
    "ITS RETENU A LA SOURCE REGIME GTA": "ITS GTA",
    "RETENUE BIC": "RETENUE BIC",
    "RETENUE ITS": "RETENUE ITS",
    "TVA/CI": "TVA/CI",
    "FFP": "FFP",
    "IBAPP": "IBAPP",
    "TAXE ASSURANCES": "TASS",
    "C.C.R.V.H.D": "C.C.R.V.H.D",
    "TVA PRECOMPTEE": "TVA PRECOMPTEE",
    "IMPOT GENERAL SUR LES REVENUS": "IMPOT GENERAL SUR LES REVENUS",
    "IBAPP FORFAIT": "IBAPP FORFAIT",
    "IBAPP": "IBAPP",
    "RETENUE SMCP": "RETENUE SMCP",
}
nomenclature_impots = pd.DataFrame(
    {
        "IMPOT_LONG": list(nomenclature_impots.keys()),
        "IMPOT_COURT": list(nomenclature_impots.values()),
    }
)


class PrincipauxContribuables(ReportableFile):
    file_path = "principaux_contribuables.csv"
    title = "Répartition des principaux contribuables (MONTANT_DROIT = droits déclarés ; MONTANT = droits payés)"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        merged_df = pd.merge(
            file_group.declarations,
            nomenclature_impots,
            left_on="IMPOT",
            right_on="IMPOT_COURT",
            how="inner",
        )
        merged_df = pd.merge(
            merged_df,
            file_group.quittances,
            left_on=["ANNEE_EFFET", "IDENTIFIANT", "IMPOT_LONG"],
            right_on=["ANNEE", "IDENTIFIANT", "IMPOT"],
            how="inner",
        )

        # Tri par "droits déclarés" les plus élevés
        principaux_contribuables = (
            merged_df.groupby(
                [
                    "IDENTIFIANT",
                    "ANNEE_EFFET",
                    "IMPOT_COURT",
                    "IMPOT_LONG",
                    "ANNEE",
                    "DIRECTION_y",
                ]
            )
            .agg({"MONTANT_DROIT": "sum", "MONTANT": "sum"})
            .reset_index()
            .groupby("IDENTIFIANT")
            .agg({"MONTANT": "sum", "MONTANT_DROIT": "sum"})
            .reset_index()
            .sort_values("MONTANT_DROIT", ascending=False)
        )

        # Tri par "montants payésé" les plus élevés
        principaux_contribuables.sort_values("MONTANT", ascending=False).to_csv(
            self.file_path
        )
        return self.file_path


class RecetteParImpots(ReportableFile):
    file_path = "recette_par_impots.csv"
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


class RecetteParTypeDeclaration(ReportableFile):
    file_path = "recettes_par_type_declaration.csv"
    title = "Montant des recettes forcées et spontanées par jour"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        montant_recettes_par_type_declaration = file_group.quittances[
            ["DATE_PAIEMENT", "TYPE_DECLARATION", "MONTANT"]
        ]
        montant_recettes_par_type_declaration[
            "TYPE_DECLARATION"
        ] = montant_recettes_par_type_declaration["TYPE_DECLARATION"].apply(
            lambda x: "Déclaration spontanée"
            if x == "DECLARATION SPONTANEE"
            else "Recette forcée"
        )
        montant_recettes_par_type_declaration = (
            montant_recettes_par_type_declaration.groupby(
                ["DATE_PAIEMENT", "TYPE_DECLARATION"]
            )
            .sum()
            .reset_index()
        )
        montant_recettes_par_type_declaration.to_csv(self.file_path)

        return self.file_path


class DeclarationParDirection(ReportableFile):
    file_path = "declarations_par_direction.csv"
    title = "Montant des déclarations par direction (droits et crédits) par mois"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        montant_declarations_par_direction = file_group.declarations[
            ["ANNEE_EFFET", "DIRECTION", "MONTANT_CREDIT", "MONTANT_DROIT"]
        ]
        montant_declarations_par_direction = (
            montant_declarations_par_direction.groupby(["ANNEE_EFFET", "DIRECTION"])
            .sum(["MONTANT_CREDIT", "MONTANT_DROIT"])
            .reset_index()
        )

        montant_declarations_par_direction.to_csv(self.file_path)
        return self.file_path


class RecettesParDeclarations(ReportableFile):
    file_path = "montant_declarations_par_direction.csv"
    title = "Part des recettes collectées sur les déclarations"

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        super().__init__(llm, group, chat)

    def Transform(self, file_group: FileGroup) -> str:
        montant_declarations_par_direction = file_group.declarations[
            ["ANNEE_EFFET", "DIRECTION", "MONTANT_CREDIT", "MONTANT_DROIT"]
        ]
        montant_declarations_par_direction = (
            montant_declarations_par_direction.groupby(["ANNEE_EFFET", "DIRECTION"])
            .sum(["MONTANT_CREDIT", "MONTANT_DROIT"])
            .reset_index()
        )

        montant_declarations_par_direction.to_csv(self.file_path)
        return self.file_path


class ContentieuxParTypeImpots(ReportableFile):
    file_path = "contentieux_par_type_impots.csv"
    title = "Répartition des plus gros paiements par contribuable"

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
