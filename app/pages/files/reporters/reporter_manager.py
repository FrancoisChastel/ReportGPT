from langchain_openai import OpenAI, ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.agents.agent_types import AgentType

import pandas as pd

TMP_DIR = "tmp/"


class FileGroup:
    __slots__ = [
        "declarations",
        "contribuables",
        "quittances",
        "amr",
        "notifications",
        "recours",
    ]

    def __init__(
        self,
        declarations_path: str,
        contribuables_path: str,
        quittances_path: str,
        amr_path: str,
        recours_path: str,
        notifications_path: str,
    ) -> None:
        print(f"Loading files")

        self.declarations = pd.read_excel(declarations_path)
        self.contribuables = pd.read_excel(contribuables_path)
        self.quittances = pd.read_excel(quittances_path)
        self.amr = pd.read_excel(amr_path)
        print(f"Files partially loaded")

        amr_col_types = {
            "DROIT_SIMPLE": "float",
            "PENALITE": "float",
            "FRAIS_POURSUITE": "float",
            "DROIT_SIMPLE_PAYE": "float",
            "PENALITE_PAYE": "float",
            "MAJORATION_PAYE": "float",
        }
        for column in list(amr_col_types):
            self.amr[column] = self.amr[column].str.replace(",", ".")
            self.amr[column] = self.amr[column].astype("float")

        self.recours = pd.read_excel(recours_path)
        recours_col_types = {
            "Droit Simple": "float",
            "Pénalité": "float",
            "Majoration": "float",
            "Frais": "float",
        }
        for column in list(recours_col_types):
            self.recours[column] = self.recours[column].str.replace(",", ".")
            self.recours[column] = self.recours[column].str.replace(" ", "")
            self.recours[column] = self.recours[column].astype("float")

        self.notifications = pd.read_excel(notifications_path)
        print(f"Files loaded")


class ReportableFile:
    __slots__ = ["llm", "agent", "title", "description", "chat", "title"]

    def __init__(
        self,
        llm: OpenAI,
        group: FileGroup,
        chat: ChatOpenAI,
    ):
        self.llm = llm
        self.chat = chat
        self.agent = create_csv_agent(
            llm,
            self.Transform(group),
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
        )

    def Transform(file_group: FileGroup) -> str:
        """
        Take a file_group which hold all the available files and make
        it a file from it which will be group truth for analysis
        """
        pass

    def generateInsight(self) -> str:
        insight = ""
        try:
            insight = self.agent.run(
                f"Give me a summary text that give me insight about the dataset in a non-technical way (which is about {self.title})"
            )
        except Exception:
            pass
        return insight

    def generateTrends(self) -> str:
        trends = ""
        try:
            trends = self.agent.run(
                f"Give me a summary text giving me insight of the trends of evolution (which is about {self.title})"
            )
        except Exception:
            pass
        return trends

    def generateAnalysis(self) -> str:
        analysis = ""
        try:
            analysis = self.agent.run(
                f"Give me a summary text information of what the values could means {self.title})"
            )
        except Exception:
            pass
        return analysis

    def generateReport(self) -> str:
        print(f"Generating report for {self.title}")
        return "\r\n".join(
            [self.generateTrends(), self.generateInsight(), self.generateAnalysis()]
        )

    def summarize(self, summarise) -> str:
        report = self.generateReport()
        if summarise:
            messages = [
                {
                    "role": "system",
                    "content": "Tu es un analyste des impôts Mauritanienne, tu fais des rapports d'analyses en francais à destination de la direction. Tes rapports exposes de manière efficaces le contexte et fournis une analyse avec des explications ainsi que des recommandations. Il permet à la direction d'avoir une vision fonctionnelle et non technique des choses. Tu ne fais pas reference a des tableaux externes. Une attention sur les tendances est attendue.",
                },
                {
                    "role": "user",
                    "content": report,
                },
            ]

            return (
                self.chat.chat.completions.create(
                    model="gpt-3.5-turbo-16k",
                    messages=messages,
                    temperature=0.15,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                .choices[0]
                .message.content
            )
        return report
