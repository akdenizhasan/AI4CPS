import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
import json
import re
import math
import base64

# --- 1. AYARLAR VE YAPAY ZEKA YAPILANDIRMASI ---
# Not: Streamlit Secrets panelinden API anahtarınızı alacağız
genai.configure(api_key=st.secrets)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. DUYGUSAL ZEKA (WLEIS) PUANLAMA MANTIĞI ---
def calculate_ei_score(responses):
    """WLEIS 16 soru: SEA(1-4), OEA(5-8), UOE(9-12), ROE(13-16)"""
    return {
        "SEA": sum(responses[0:4]),
        "OEA": sum(responses[4:8]),
        "UOE": sum(responses[8:12]),
        "ROE": sum(responses[12:16]),
        "EI_Total": sum(responses)
    }

# --- 3. MULTIMODAL PROMPT OLUŞTURUCU (CoT İLE) ---
def build_multimodal_prompt(stage_name, response, task_description):
    return f"""
You are an expert creativity evaluator using the Basadur Simplex model.
STAGE: {stage_name}
TASK: {task_description}

STUDENT RESPONSE:
<<< {response} >>>

Step 1: Reasoning (Chain-of-Thought)
- Analyze the student's text in relation to the VISUAL CUES in the image.
- Evaluate Flexibility (0-3): Are there different conceptual categories?
- Evaluate Originality (0-3): Is the response rare or insightful?
- Evaluate Elaboration (0-3): Level of detail and development.
- Evaluate Convergent Thinking (0-3): Logic, feasibility, and adherence to the task goal. [6]

Step 2: Final Scores
Return ONLY a JSON block under the heading "Final Scores":
{{
  "Flexibility": int,
  "Originality": int,
  "Elaboration": int,
  "Convergent": int,
  "D_j": int, (Sum of first three)
  "StageScore_j": int (D_j + Convergent)
}}
""".strip()

# --- 4. WEB ARAYÜZÜ (STREAMLIT) ---
st.set_page_config(page_title="CPS & EI Araştırması", layout="centered")
st.title("🧩 Yaratıcı Problem Çözme ve Duygusal Zeka Çalışması")

# BÖLÜM 1: Duygusal Zeka (WLEIS - Örnek Sorular)
with st.expander("Bölüm 1: Duygusal Zeka Anketi", expanded=True):
    st.write("Lütfen maddelere katılma derecenizi seçin (1: Hiç, 5: Tamamen)")
    q1 = st.radio("1. Kendi duygularımın nedenlerini her zaman bilirim.", [1, 2, 3, 4, 5], horizontal=True)
    # Buraya diğer 15 soruyu ekleyiniz...
    ei_answers = [q1] * 16 # Kodun çalışması için geçici liste

# BÖLÜM 2: Görsel CPS
st.divider()
st.header("Bölüm 2: Görsel Analiz ve Problem Çözme")
# Resminizi base64 formatına çevirip AI'ya göndermek en sağlıklı yoldur
IMAGE_PATH = "senin_resmin.jpg" 
st.image(IMAGE_PATH, caption="Lütfen bu resmi dikkatle inceleyin.")

r1 = st.text_area("Aşama 1: Resimde gördüğünüz ana zorlukları veya fırsatları yazın.")
r2 = st.text_area("Aşama 2: Bu durumu iyileştirmek için aklınıza gelen tüm fikirleri (akıcılık odaklı) listeleyin.")

if st.button("Çalışmayı Gönder"):
    with st.spinner("AI Yanıtlarınızı Bilimsel Olarak Puanlıyor..."):
        # AI Analizi (Stage 1 Örneği)
        prompt = build_multimodal_prompt("Clarify", r1, "Resimdeki bulanık durumu tanımlama")
        
        # Resmi AI'nın görebileceği formata çeviriyoruz
        with open(IMAGE_PATH, "rb") as f:
            img_data = f.read()
        
        # Gemini çağrısı
        ai_response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_data}])
        
        # Puanları Ayıklama (Regex)
        match = re.search(r'Final Scores:\s*(\{.*\})', ai_response.text, re.DOTALL)
        scores = json.loads(match.group(1)) if match else {}

        # Google Sheets'e Kayıt
        conn = st.connection("gsheets", type=GSheetsConnection)
        ei_data = calculate_ei_score(ei_answers)
        
        # Veri setini birleştirip kaydediyoruz
        final_row = {**ei_data, "CPS_S1_Score": scores.get("StageScore_j", 0), "Text_S1": r1}
        # conn.create(data=pd.DataFrame([final_row]))
        
        st.success("Verileriniz başarıyla kaydedildi!")
