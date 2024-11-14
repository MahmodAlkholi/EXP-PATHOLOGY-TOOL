from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import anthropic
import streamlit as st
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Safely retrieve environment variables and raise errors if they are missing
def get_env_var(var_name):
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Environment variable '{var_name}' is not set.")
    return value

# Setting environment variables
os.environ["OPENAI_API_KEY"] = get_env_var("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = get_env_var("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "True"
os.environ["LANGCHAIN_PROJECT"] = get_env_var("LANGCHAIN_PROJECT")
CLOADE_API_KEY = get_env_var("CLOADE_API_KEY")
grok_api_key = get_env_var("GROQ_API_KEY")

st.set_page_config(
    page_title="EXP - PLATFORM FOR PATHOLOGY",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Connect to or create the database
conn = sqlite3.connect("pathology_reports.db")
cursor = conn.cursor()

# Create table if it doesn't already exist
cursor.execute('''CREATE TABLE IF NOT EXISTS pathology_reports (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT,
                    patient_age INTEGER,
                    referring_doctor TEXT,
                    date DATE,
                    clinical_data TEXT,
                    microscopic_examination TEXT,
                    gross_images BLOB,
                    microscopic_images BLOB,
                    diagnosis TEXT,
                    recommendations TEXT
                )''')
conn.commit()

# Function to transcribe audio using Whisper
def whisper_voice2text(voice_data):
    transcription = openai.Audio.transcribe(
        model="whisper-1",
        file=voice_data,
        response_format="json"
    )
    return transcription["text"]

st.header("PEX - PLATFORM FOR PATHOLOGY")

# Input form layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("### INPUT TEXT REPORT")
    input_text_p_name = st.text_input("PATIENT NAME", "", key="text_p_name")
    input_text_p_age = st.text_input("PATIENT AGE", "", key="text_p_age")
    input_text_p_PD = st.text_input("Referring Doctor", "", key="text_p_PD")
    input_text_p_date = st.date_input("DATE", key="text_p_date")
    input_text_p_clinical = st.text_area("Clinical Data", placeholder="WRITE THE CLINICAL DATA PLEASE", height=150)
    input_text_p_micro_find = st.text_area("Microscopic Examination", placeholder="WRITE THE Microscopic Examination PLEASE", height=150)
    input_text_p_gross = st.file_uploader("UPLOAD GROSS IMAGES", type=["jpg", "jpeg", "png"], key="text-gross")
    input_text_p_microscopic = st.file_uploader("UPLOAD MICROSCOPIC IMAGES", type=["jpg", "jpeg", "png"], key="text-microscopic")
    input_text_p_diagnosis = st.text_area("Diagnosis", placeholder="WRITE DIAGNOSIS PLEASE", height=150)
    input_text_p_recommend = st.text_area("Recommendations", placeholder="WRITE RECOMMENDATIONS PLEASE", height=150)
    save_text_btn = st.button("SAVE DATA", key="text-save")

with col2:
    st.markdown("### INPUT SOUND REPORT")
    audio_text_p_name = st.text_input("PATIENT NAME", "", key="audio_p_name")
    audio_text_p_age = st.text_input("PATIENT AGE", "", key="audio_p_age")
    audio_text_p_PD = st.text_input("Referring Doctor", "", key="audio_p_PD")
    audio_text_p_date = st.date_input("DATE", key="audio_p_date")
    audio_clinical = st.file_uploader("UPLOAD CLINICAL AUDIO", type=["wav", "mp3"], key="audio-clinical")
    audio_micro_find = st.file_uploader("UPLOAD MICROSCOPIC AUDIO", type=["wav", "mp3"], key="audio-micro_find")
    input_audio_p_gross = st.file_uploader("UPLOAD GROSS IMAGES", type=["jpg", "jpeg", "png"], key="audio-gross")
    input_audio_p_microscopic = st.file_uploader("UPLOAD MICROSCOPIC IMAGES", type=["jpg", "jpeg", "png"], key="audio-microscopic")
    audio_diagnosis = st.file_uploader("UPLOAD DIAGNOSIS AUDIO", type=["wav", "mp3"], key="audio-diagnosis")
    audio_recommend = st.file_uploader("UPLOAD RECOMMENDATIONS AUDIO", type=["wav", "mp3"], key="audio-recommend")
    save_audio_btn = st.button("SAVE DATA", key="audio-save")

# Function to insert data into the database
def add_report(patient_name, patient_age, referring_doctor, date, clinical_data, microscopic_examination, gross_images, microscopic_images, diagnosis, recommendations):
    cursor.execute('''INSERT INTO pathology_reports (
                        patient_name, patient_age, referring_doctor, date, clinical_data, microscopic_examination, gross_images, microscopic_images, diagnosis, recommendations
                      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (patient_name, patient_age, referring_doctor, date, clinical_data, microscopic_examination, gross_images, microscopic_images, diagnosis, recommendations))
    conn.commit()

if save_text_btn:
    if input_text_p_name:
        gross_image = input_text_p_gross.read() if input_text_p_gross else None
        microscopic_image = input_text_p_microscopic.read() if input_text_p_microscopic else None
        add_report(input_text_p_name, input_text_p_age, input_text_p_PD, input_text_p_date, input_text_p_clinical, input_text_p_micro_find, gross_image, microscopic_image, input_text_p_diagnosis, input_text_p_recommend)
        st.success("Report saved successfully!")
    else:
        st.error("Please fill in all required fields: Patient Name, Referring Doctor, and Diagnosis.")

if save_audio_btn:
    if audio_text_p_name:
        gross_audio_image = input_audio_p_gross.read() if input_audio_p_gross else None
        microscopic_audio_image = input_audio_p_microscopic.read() if input_audio_p_microscopic else None

        audioclinical = whisper_voice2text(audio_clinical) if audio_clinical else ""
        audiomicro_find = whisper_voice2text(audio_micro_find) if audio_micro_find else ""
        audiodiagnosis = whisper_voice2text(audio_diagnosis) if audio_diagnosis else ""
        audiorecommend = whisper_voice2text(audio_recommend) if audio_recommend else ""

        add_report(audio_text_p_name, audio_text_p_age, audio_text_p_PD, audio_text_p_date, audioclinical, audiomicro_find, gross_audio_image, microscopic_audio_image, audiodiagnosis, audiorecommend)
        st.success("Report saved successfully!")
    else:
        st.error("Please fill in all required fields: Patient Name, Referring Doctor, and Diagnosis.")

# Generating professional report using OpenAI
def writing_report(model, patient_name, patient_age, referring_doctor, date, clinical_data, microscopic, diagnosis, recommendations):
    parser = StrOutputParser()
    llm = ChatOpenAI(model=model)
    prompt = ChatPromptTemplate.from_messages(
        [("system", "you are a professional pathology doctor write a report"), ("user", "{input}")]
    )
    chain = prompt | llm | parser
    result = chain.invoke({"input": f"I have features for a pathology report such as patient name {patient_name}, patient age {patient_age}, referring doctor {referring_doctor}, today's date {date}, clinical data {clinical_data}, microscopic findings {microscopic}, diagnosis {diagnosis} and recommendations {recommendations}"})
    return result

if st.button("GENERATE REPORT WITH OPENAI"):
    result1 = writing_report("gpt-4", input_text_p_name, input_text_p_age, input_text_p_PD, input_text_p_date, input_text_p_clinical, input_text_p_micro_find, input_text_p_diagnosis, input_text_p_recommend)
    st.write(result1)

# Generating professional report using Claude model
def writing_claude_report(model, patient_name, patient_age, referring_doctor, date, clinical_data, microscopic, diagnosis, recommendations):
    client = anthropic.Anthropic(api_key=CLOADE_API_KEY)
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system="You are a professional pathology doctor write this report in a more professional way explaining the report.",
        messages=[{"role": "user", "content": f"Please write a pathology report with the following information: Patient Name: {patient_name}, Patient Age: {patient_age}, Referring Doctor: {referring_doctor}, Date: {date}, Clinical Data: {clinical_data}, Microscopic Findings: {microscopic}, Diagnosis: {diagnosis}, Recommendations: {recommendations}"}]
    )
    return message.content

if st.button("GENERATE REPORT WITH CLAUDE"):
   
