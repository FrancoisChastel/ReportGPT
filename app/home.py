from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st
import pandas as pd
import os
import openai


from pages.files.main import InitializeReporter


file_formats = {
    "xlsx": pd.read_excel,
}


def clear_submit():
    """
    Clear the Submit Button State
    Returns:

    """
    st.session_state["submit"] = False


@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    except Exception:
        ext = uploaded_file.split(".")[-1]
    if ext in file_formats:
        return file_formats[ext](uploaded_file)
    else:
        st.error(f"Unsupported file format: {ext}")
        return None


st.set_page_config(
    page_title="ReportGPT - Generez des rapports avec vos données", page_icon="🤖"
)
st.title("🤖 ReportGPT - Generez des rapports avec vos données")

openai_api_key = st.sidebar.text_input(
    "Clé d'API OpenAI",
    type="password",
)

intermediate_reports = st.sidebar.checkbox("Activer les rapports intermédiaires")


uploaded_declarations = st.sidebar.file_uploader(
    "Téléversez le fichier des déclarations",
    type=list(file_formats.keys()),
    help="Les formats : xlsx sont supportés",
    on_change=clear_submit,
)

uploaded_contribuables = st.sidebar.file_uploader(
    "Téléversez le fichier des contribuables",
    type=list(file_formats.keys()),
    help="Les formats : xlsx sont supportés",
    on_change=clear_submit,
)

uploaded_quittances = st.sidebar.file_uploader(
    "Téléversez le fichier des quittances",
    type=list(file_formats.keys()),
    help="Les formats : xlsx sont supportés",
    on_change=clear_submit,
)

uploaded_amr = st.sidebar.file_uploader(
    "Téléversez le fichier des AMR",
    type=list(file_formats.keys()),
    help="Les formats : xlsx sont supportés",
    on_change=clear_submit,
)

uploaded_recours = st.sidebar.file_uploader(
    "Téléversez le fichier des recours",
    type=list(file_formats.keys()),
    help="Les formats : xlsx sont supportés",
    on_change=clear_submit,
)

uploaded_notifications = st.sidebar.file_uploader(
    "Téléversez le fichier des notifications",
    type=list(file_formats.keys()),
    help="Les formats : xlsx sont supportés",
    on_change=clear_submit,
)

if "messages" not in st.session_state or st.sidebar.button(
    "Nettoyer l'historique de conversation"
):
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Bonjour je suis FileGPT ! Je génére des rapports pour l'administration Mauritanienne!",
        }
    ]

if not openai_api_key:
    st.info("Ajoutez une clé d'API OpenAI pour continuer.")
    st.stop()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if st.button(label="Générer le rapport"):
    st.session_state.messages.append(
        {"role": "user", "content": "Génère les rapports des fichiers ajoutés"}
    )

    with st.spinner("Analyse des fichiers, cela peut prendre plusieurs minutes"):
        reporters = InitializeReporter(
            uploaded_declarations,
            uploaded_contribuables,
            uploaded_quittances,
            uploaded_amr,
            uploaded_recours,
            uploaded_notifications,
            openai_api_key,
        )
        st.success("Fichiers analysés !", icon="🔥")

    notes = []
    for report in reporters:
        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            with st.spinner("Je réflechis"):
                response = report.summarize(summarise=intermediate_reports)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            with st.expander(
                label=f"Rapport de {report.title}",
            ):
                st.markdown(response)
                notes.append(response)
    client = openai.OpenAI(api_key=openai_api_key)
    with st.spinner("Je conclus"):
        messages = [
            {
                "role": "system",
                "content": "Tu es un attaché au directeur des impôts Mauritanienne, tu fais des rapports d'analyses en francais à destination de la direction. Tes rapports doivent être court et synthétiques, exposant l'état des lieux et les tendances, tu fournis une analyse avec des explications ainsi que des recommandations. Une attention sur les tendances est attendue.",
            },
            {
                "role": "user",
                "content": "\r\n".join(notes),
            },
        ]

        response = (
            client.chat.completions.create(
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

        st.markdown(response)
    st.success("Le rapport a été généré avec succés", icon="🔥")
