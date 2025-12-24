import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
import json, re, math

# --- 1. AYARLAR VE GÜVENLİK ---
genai.configure(api_key=st.secrets)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="CPS & EI Araştırması", layout="centered")

# --- 2. MULTIMODAL CoT PROMPT FONKSİYONU ---
def get_ai_score(stage, student_text, image=None):
    prompt = f"""
    You are an expert creativity evaluator using the Basadur model and CEF rubric.
    STAGE: {stage}
    STUDENT RESPONSE: "{student_text}"

    Step 1: Reasoning (Chain-of-Thought)
    - Analyze the response based on visual cues if provided.
    - Evaluate Flexibility (0-3), Originality (0-3), Elaboration (0-3), and Convergent (0-3).
    - Calculate D_j = Flexibility + Originality + Elaboration.
    - Calculate StageScore_j = D_j + Convergent.

    Step 2: Final Scores
    Return ONLY this JSON under "Final Scores":
    {{
      "flex": int, "orig": int, "elab": int, "conv": int, "D_j": int, "total": int
    }}
    """
    inputs = [prompt]
    if image: inputs.append(image)
    
    response = model.generate_content(inputs)
    match = re.search(r'Final Scores:\s*(\{.*\})', response.text, re.DOTALL)
    return json.loads(match.group(1)) if match else None

# --- 3. ARAYÜZ (UX) ---
st.title("🧩 Yaratıcı Problem Çözme Araştırması")

# BÖLÜM 1: WLEIS DUYGUSAL ZEKA (16 Madde)
with st.expander("Bölüm 1: Duygusal Zeka Ölçeği", expanded=True):
    st.write("Lütfen maddelere katılma derecenizi seçin (1: Hiç, 5: Tamamen)")
    questions =
    ei_responses =
    for i, q in enumerate(questions):
        res = st.select_slider(f"{i+1}. {q}", options=[1, 2, 3, 4, 5], value=3)
        ei_responses.append(res)

# BÖLÜM 2: CPS SÜRECİ
st.divider()
st.header("Bölüm 2: Görsel Analiz")
# Görsel dosyanızın adı GitHub'da resim.jpg olmalı
try:
    from PIL import Image
    img = Image.open("resim.jpg") 
    st.image(img, caption="Bu resmi dikkatle inceleyin.")
except:
    st.error("Görsel yüklenemedi. Lütfen GitHub'a 'resim.jpg' ekleyin.")

r1 = st.text_area("Aşama 1 (Clarify): Resimdeki sorunlar nelerdir?")
r2 = st.text_area("Aşama 2 (Ideate): Tüm çözüm fikirlerinizi yazın.")
r3 = st.text_area("Aşama 3 (Develop): En iyi çözümünüzü detaylandırın.")
r4 = st.text_area("Aşama 4 (Implement): Uygulama için ilk adımınız nedir?")

# --- 4. VERİ KAYIT VE PUANLAMA ---
if st.button("Çalışmayı Gönder"):
    with st.spinner("AI Yanıtlarınızı Bilimsel Olarak Puanlıyor..."):
        # AI Puanlama
        s1 = get_ai_score("Clarify", r1, img)
        s2 = get_ai_score("Ideate", r2)
        s3 = get_ai_score("Develop", r3)
        s4 = get_ai_score("Implement", r4)

        # EI Puanlama (WLEIS 1-16 ortalaması)
        ei_total = sum(ei_responses)

        # Google Sheets Kayıt
        conn = st.connection("gsheets", type=GSheetsConnection)
        final_data = {
            "EI_Score": ei_total,
            "CPS_S1": s1['total'], "CPS_S2": s2['total'],
            "CPS_S3": s3['total'], "CPS_S4": s4['total'],
            "Overall_CPS": s1['total'] + s2['total'] + s3['total'] + s4['total']
        }
        df = pd.DataFrame([final_data])
        # Veriyi mevcut sayfanın sonuna ekler
        conn.create(data=df)
        st.success("Tebrikler! Verileriniz başarıyla kaydedildi.")
