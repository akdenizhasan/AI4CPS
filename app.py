import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
import json, re, math
from PIL import Image

# --- 1. SETTINGS & SECURITY ---
genai.configure(api_key=st.secrets)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="CPS & EI Assessment", layout="centered")

# --- 2. MASTER SCORING FUNCTION ---
def call_ai_scorer(prompt_text, image=None):
    inputs = [prompt_text]
    if image: inputs.append(image)
    try:
        response = model.generate_content(inputs)
        match = re.search(r'(\{.*\})', response.text, re.DOTALL)
        return json.loads(match.group(1)) if match else None
    except: return None

# --- 3. UI - STUDENT BOOKLET ---
st.title("🧩 Creative Problem Solving Booklet")
st.info("In this booklet, you will work on a real-life problem. There are no right or wrong answers.")

# BÖLÜM 1: EMOTIONAL INTELLIGENCE (WLEIS)
with st.expander("Bölüm 1: Emotional Intelligence Survey", expanded=True):
    # WLEIS 16 Items
    wleis_items = [
        "I have a good sense of why I have certain feelings most of the time.",
        "I have a good understanding of my own emotions.",
        "I really understand what I feel.",
        "I always know whether or not I am happy.",
        "I always know my friends' emotions from their behavior.",
        "I am a good observer of others' emotions.",
        "I am sensitive to the feelings and emotions of others.",
        "I have a good understanding of the emotions of people around me.",
        "I always set goals for myself and then try my best to achieve them.",
        "I always tell myself I am a competent person.",
        "I am a self-motivating person.",
        "I would always encourage myself to try my best.",
        "I am able to control my temper so that I can handle difficulties rationally.",
        "I am quite capable of controlling my own emotions.",
        "I can always calm down quickly when I am very angry.",
        "I have good control of my own emotions."
    ]
    ei_responses =
    for i, item in enumerate(wleis_items):
        res = st.select_slider(f"{i+1}. {item}", options=[3, 7, 8, 5, 1], value=3)
        ei_responses.append(res)

# BÖLÜM 2: SCENARIO & CPS
st.header("Bölüm 2: The School Corridor Scenario")
st.write("**Scenario:** The hallway is very crowded during break times. Pathways are blocked, causing delays and small accidents.")
try:
    img = Image.open("resim.jpg") 
    st.image(img, caption="School corridor during break time.")
except:
    st.warning("Please upload 'resim.jpg' to your GitHub repo.")
    st.stop()

# STAGE 1: PROBLEM FORMULATION (Tasks 1-3)
st.subheader("🟦 Stage 1: Understanding the Problem")
t1a = st.text_area("Task 1A: List at least 5 possible problems shown in the picture.")
t1b = st.text_area("Task 1B: Choose the ONE most important problem and explain why.")

t2a = st.text_area("Task 2A: List all information and facts (Observations, Numbers, Rules, etc.).")
t2b = st.text_area("Task 2B: Select the top 3 facts and explain why they matter.")

t3a = st.text_area("Task 3A: Write 2–3 'How Might We' (HMW) definitions.")
t3b = st.text_area("Task 3B: Choose the best definition and explain why.")

# STAGE 2: SOLUTION FINDING (Tasks 4-5)
st.subheader("🟧 Stage 2: Producing and Choosing Ideas")
t4 = st.text_area("Task 4: Generate as many solution ideas as you can (at least 10).")
t5 = st.text_area("Task 5: Choose the best solution and explain why.")

# STAGE 3: IMPLEMENTATION (Task 6)
st.subheader("🟩 Stage 3: Planning and Testing")
t6a = st.text_area("Task 6A: Describe your 4-step action plan.")
t6b = st.text_area("Task 6B (Mini Test): How will you test if your idea works? (Where, who, what observations?)")

# --- 4. DATA PROCESSING & SUBMISSION ---
if st.button("Complete and Submit"):
    with st.spinner("AI is calculating your CPS Proficiency..."):
        # Step-by-Step Scoring following your Prompt Set [Prompt 1-7]
        s1 = call_ai_scorer(f"Prompt 1 (Problem Finding): Input A: {t1a}, Input B: {t1b}. JSON: {{'D1':0-3,'C1':0-3}}", img)
        s2 = call_ai_scorer(f"Prompt 2 (Fact Finding): Input A: {t2a}, Input B: {t2b}. JSON: {{'D3':0-3,'C3':0-3}}")
        s3 = call_ai_scorer(f"Prompt 3 (Problem Definition): Input A: {t3a}, Input B: {t3b}. JSON: {{'D2':0-3,'C2':0-3}}")
        s4 = call_ai_scorer(f"Prompt 4 (Idea Generation): Ideas: {t4}. Calculate Fluency, Flex(0-3), Orig(0-3), Elab(0-3). JSON: {{'Fluency':int,'Flex':int,'Orig':int,'Elab':int}}")
        s5 = call_ai_scorer(f"Prompt 5 (Idea Selection): Choice: {t5}. JSON: {{'C_IdeaSelection':0-3}}")
        s6 = call_ai_scorer(f"Prompt 6 (Implementation): Plan: {t6a}, Test: {t6b}. JSON: {{'C_Implementation':0-3}}")

        # MASTER AGGREGATOR [Prompt 7 Logic]
        if s4:
            fluency_log = math.log(1 + s4['Fluency'])
            # (Note: Z-scores would require cohort comparison in backend; here we use raw weights for immediate storage)
            dw_score = (0.20 * fluency_log) + (0.30 * s4['Flex']) + (0.30 * s4['Orig']) + (0.20 * s4['Elab'])
        else: dw_score = 0

        # Save to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        final_row = pd.DataFrame(), "OEA": sum(ei_responses[4:8]), 
            "UOE": sum(ei_responses[8:12]), "ROE": sum(ei_responses[12:16]),
            "EI_Total": sum(ei_responses),
            "S1_D": s1.get('D1',0), "S1_C": s1.get('C1',0),
            "S4_DW": dw_score, "S6_C": s6.get('C_Implementation',0),
            "Status": "Evaluated"
        }])
        conn.create(data=final_row)
        st.success("Cevaplarınız başarıyla kaydedildi! Thank you for participating.")
        st.balloons()
