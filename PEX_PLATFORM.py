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

# Retrieve API keys from environment variables
os.environ["OPENAI_API_KEY"] = str(os.getenv("OPENAI_API_KEY"))
os.environ["LANGCHAIN_API_KEY"] = str(os.getenv("LANGCHAIN_API_KEY"))
os.environ["LANGCHAIN_TRACING_V2"] = "True"
os.environ["LANGCHAIN_PROJECT"] = str(os.getenv("LANGCHAIN_PROJECT"))
os.environ["CLOADE_API_KEY"] = str(os.getenv("CLOADE_API_KEY"))
CLOADE_API_KEY = str(os.getenv("CLOADE_API_KEY"))
grok_api_key = str(os.getenv("GROQ_API_KEY"))



# Set Streamlit configuration
st.set_page_config(
    page_title="EXP - PLATFORM FOR PATHOLOGY",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Connect to or create the SQLite database
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
                    Microscopic_Examination TEXT,
                    gross_images BLOB,
                    microscopic_images BLOB,
                    diagnosis TEXT,
                    recommendations TEXT
                )''')
conn.commit()

##############################################
# Function to transcribe audio using Whisper
def wesper_voice2text(voice_data):
    transcription = openai.Audio.transcribe(
        model="whisper-1",  # Specify the Whisper model
        file=voice_data,    # Pass the binary data directly
        response_format="json"
    )
    return transcription["text"]

# Streamlit UI
st.header("PEX - PLATFORM FOR PATHOLOGY")

# Columns for text and audio input
col1, col2 = st.columns(2)

# Text Input Column
with col1:
    st.markdown("### INPUT TEXT REPORT")
    input_text_p_name = st.text_input("PATIENT NAME", "", key="text_p_name")
    input_text_p_age = st.text_input("PATIENT AGE", "", key="text_p_age")
    input_text_p_PD = st.text_input("Referring Doctor", "", key="text_p_PD")
    input_text_p_date = st.date_input("DATE", key="text_p_date")
    input_text_p_clinical = st.text_area(label="Clinical Data", placeholder="WRITE THE CLINICAL DATA PLEASE", height=150)
    input_text_p_micro_find = st.text_area(label="Microscopic Examination", placeholder="WRITE THE Microscopic Examination PLEASE", height=150)
    input_text_p_gross = st.file_uploader("UPLOAD GROSS IMAGES", type=["jpg", "jpeg", "png"], key="text-gross")
    input_text_p_microscop = st.file_uploader("UPLOAD MICROSCOPIC IMAGES", type=["jpg", "jpeg", "png"], key="text-microscopic")
    input_text_p_diagnosis = st.text_area(label="Diagnosis", placeholder="WRITE DIAGNOSIS PLEASE", height=150, key="text_diagnosis")
    input_text_p_recommend = st.text_area(label="Recommendations", placeholder="WRITE RECOMMENDATIONS PLEASE", height=150, key="text_Recommendations")
    save_text_btn = st.button("SAVE DATA", key="text-save")

# Audio Input Column
with col2:
    st.markdown("### INPUT SOUND REPORT")
    audio_text_p_name = st.text_input("PATIENT NAME", "", key="audio_p_name")
    audio_text_p_age = st.text_input("PATIENT AGE", "", key="audio_p_age")
    audio_text_p_PD = st.text_input("Referring Doctor", "", key="audio_p_PD")
    audio_text_p_date = st.date_input("DATE", key="audio_p_date")
# Replace experimental_audio lines with file uploaders for each audio field.
    audio_clinical = st.file_uploader("UPLOAD YOUR CLINICAL DATA AUDIO FILE", type=["wav", "mp3"], key="audio-clinical")
    audio_micro_find = st.file_uploader("UPLOAD YOUR MICROSCOPIC EXAMINATION AUDIO FILE", type=["wav", "mp3"], key="audio-micro_find")
    audio_diagnosis = st.file_uploader("UPLOAD YOUR DIAGNOSIS AUDIO FILE", type=["wav", "mp3"], key="audio-diagnosis")
    audio_recommend = st.file_uploader("UPLOAD YOUR RECOMMENDATIONS AUDIO FILE", type=["wav", "mp3"], key="audio-recommend")

    save_audio_btn = st.button("SAVE DATA", key="audio-save")

########################################################
# Store data in the database
def add_report(patient_name, patient_age, referring_doctor, date, clinical_data, gross_images, microscopic_images, diagnosis, recommendations):
    cursor.execute('''INSERT INTO pathology_reports (
                        patient_name, patient_age, referring_doctor, date, clinical_data, gross_images, microscopic_images, diagnosis, recommendations
                      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (patient_name, patient_age, referring_doctor, date, clinical_data, gross_images, microscopic_images, diagnosis, recommendations))
    conn.commit()

# Save data from text input
if save_text_btn:
    if input_text_p_name:
        gross_image = input_text_p_gross.read() if input_text_p_gross else None
        microscopic_image = input_text_p_microscop.read() if input_text_p_microscop else None

        add_report(
            patient_name=input_text_p_name,
            patient_age=input_text_p_age,
            referring_doctor=input_text_p_PD,
            date=input_text_p_date,
            clinical_data=input_text_p_clinical,
            gross_images=gross_image,
            microscopic_images=microscopic_image,
            diagnosis=input_text_p_diagnosis,
            recommendations=input_text_p_recommend
        )
        st.success("Report saved successfully!")
    else:
        st.error("Please fill in all required fields: Patient Name, Referring Doctor, and Diagnosis.")

# Save data from audio input
if save_audio_btn:
    if audio_text_p_name:
        gross_audio_image = input_audio_p_gross.read() if input_audio_p_gross else None
        microscopic_audio_image = input_audio_p_microscop.read() if input_audio_p_microscop else None

        audioclinical = wesper_voice2text(audio_clinical)
        audiodiagnosis = wesper_voice2text(audio_diagnosis)
        audiorecommend = wesper_voice2text(audio_recommend)

        add_report(
            patient_name=audio_text_p_name,
            patient_age=audio_text_p_age,
            referring_doctor=audio_text_p_PD,
            date=audio_text_p_date,
            clinical_data=audioclinical,
            gross_images=gross_audio_image,
            microscopic_images=microscopic_audio_image,
            diagnosis=audiodiagnosis,
            recommendations=audiorecommend
        )
        st.success("Report saved successfully!")
    else:
        st.error("Please fill in all required fields: Patient Name, Referring Doctor, and Diagnosis.")

###############################################################
# Generate professional report with OpenAI model
def writing_report(model, patient_name, patient_age, referring_doctor, date, clinical_data, microscopic, diagnosis, recommendations):
    parser = StrOutputParser()
    llm = ChatOpenAI(model=model)
    prompet = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a professional pathology doctor, write a report"),
        ("user", "{input}")
    ])
    chain = prompet | llm | parser
    result = chain.invoke({"input": f"I have some features for a pathology report: Patient Name: {patient_name}, Age: {patient_age}, Referring Doctor: {referring_doctor}, Date: {date}, Clinical Data: {clinical_data}, Microscopic Findings: {microscopic}, Diagnosis: {diagnosis}, Recommendations: {recommendations}"})
    return result

if st.button("GENERATE REPORT WITH OPENAI"):
    result = writing_report("gpt-4", input_text_p_name, input_text_p_age, input_text_p_PD, input_text_p_date, input_text_p_clinical, input_text_p_micro_find, input_text_p_diagnosis, input_text_p_recommend)
    st.write(result)

###############################################################
# Generate professional report with Claude model
def writing_claude_report(model, patient_name, patient_age, referring_doctor, date, clinical_data, microscopic, diagnosis, recommendations):
    client = anthropic.Anthropic(api_key=CLOADE_API_KEY)
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system="You are a professional pathology doctor writing a report in a professional and explanatory way.",
        messages=[
            {"role": "user", "content": f"Please write a pathology report with the following information: Patient Name: {patient_name}, Age: {patient_age}, Referring Doctor: {referring_doctor}, Date: {date}, Clinical Data: {clinical_data}, Microscopic Findings: {microscopic}, Diagnosis: {diagnosis}, Recommendations: {recommendations}"}
        ]
    )
    return message.content

if st.button("GENERATE REPORT WITH CLAUDE"):
    result = writing_claude_report(
        "claude-3-5-sonnet-20241022",
        input_text_p_name,
        input_text_p_age,
        input_text_p_PD,
        input_text_p_date,
        input_text_p_clinical,
        input_text_p_micro_find,
        input_text_p_diagnosis,
        input_text_p_recommend
    )
    st.write(result)
