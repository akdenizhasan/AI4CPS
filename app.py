import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
import json, re, math
from PIL import Image

# --- 1. AYARLAR VE GÜVENLİK ---
genai.configure(api_key=st.secrets)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="CPS & EI Araştırması", layout="centered")

# --- 2. AI PUANLAMA MOTORU (7 PROMPT SETİ) ---
def call_ai_scorer(prompt_text, image=None):
    """Gemini API'yi çağırır ve JSON çıktısını ayıklar."""
    inputs = [prompt_text]
    if image:
        inputs.append(image)
    
    try:
        response = model.generate_content(inputs)
        # JSON bloğunu ayıkla
        match = re.search(r'(\{.*\})', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return None
    except Exception as e:
        st.error(f"AI Puanlama Hatası: {e}")
        return None

# --- 3. ARAYÜZ TASARIMI ---
st.title("🧩 Yaratıcı Problem Çözme ve Duygusal Zeka")
st.write("Bu araştırma kapsamında verileriniz anonim olarak saklanacaktır.")

# BÖLÜM 1: DUYGUSAL ZEKA (WLEIS - 16 MADDE)
with st.expander("Bölüm 1: Duygusal Zeka Anketi", expanded=True):
    st.info("Lütfen maddelere katılma derecenizi seçin (1: Hiç, 5: Tamamen)")
    wleis_items =
    ei_responses =
    for i, item in enumerate(wleis_items):
        res = st.select_slider(f"{i+1}. {item}", options=[1, 2, 3, 4, 5], value=3)
        ei_responses.append(res)

# BÖLÜM 2: CPS SÜRECİ (8 ADIM - 3 FAZ)
st.divider()
st.header("Bölüm 2: Yaratıcı Problem Çözme")

# Görsel Yükleme Kontrolü
try:
    img = Image.open("resim.jpg") 
    st.image(img, caption="Lütfen bu resmi dikkatle inceleyerek soruları yanıtlayın.")
except:
    st.error("Lütfen GitHub deponuza 'resim.jpg' isimli bir görsel ekleyin.")
    st.stop()

# FAZ 1: PROBLEM FORMULASYONU (Steps 1-3)
st.subheader("🟦 Aşama 1: Problemi Anlama")
r1 = st.text_area("Adım 1: Resimle ilgili gördüğün en az 4-5 problemi yaz. En önemlisini belirt ve nedenini açıkla.")
r2 = st.text_area("Adım 2: Bu problem hakkında bildiğin tüm gerçekleri (sayılar, gözlemler, kısıtlar) yaz.")
r3 = st.text_area("Adım 3: Seçtiğin problemle ilgili 3 farklı 'Nasıl Yapabiliriz?' (HMW) cümlesi yaz.")

# FAZ 2: ÇÖZÜM BULMA (Steps 4-5)
st.subheader("🟧 Aşama 2: Fikir Üretme ve Seçme")
r4 = st.text_area("Adım 4: Bu problemi çözmek için aklına gelen en az 10 farklı fikir üret.")
r5 = st.text_area("Adım 5: Bu fikirlerden en iyi 2 tanesini seç ve neden iyi olduklarını açıkla.")

# FAZ 3: PLANLAMA VE UYGULAMA (Steps 6-8)
st.subheader("🟩 Aşama 3: Çözümü Uygulamaya Hazırla")
r6 = st.text_area("Adım 6: Çözümünü uygulamak için 3 adımlı bir eylem planı hazırla.")
r7 = st.text_area("Adım 7: Bu çözümü uygulamak için kimlerden yardım alabilirsin?")
r8 = st.text_area("Adım 8 (Mini Test): Bu çözümü işe yarayıp yaramadığını nasıl test edersin? (Deneme planı)")

# --- 4. VERİ KAYIT VE OTOMATİK PUANLAMA ---
if st.button("Çalışmayı Tamamla ve Puanla"):
    with st.spinner("Yapay Zeka cevaplarınızı bilimsel olarak puanlıyor..."):
        
        # prompt_set yapısı (hazırladığınız promptları buraya yerleştiriyoruz)
        # Sadece Adım 1 ve 4 örneği gösterilmiştir, diğerleri benzer şekilde eklenir.
        
        s1 = call_ai_scorer(f"Adım 1 Cevabı: {r1}. Diverjan(0-3) ve Konverjan(0-3) puanla. JSON döndür: {{'D1':int, 'C1':int}}", img)
        s4 = call_ai_scorer(f"Adım 4 Fikir Listesi: {r4}. Fluency, Flexibility, Originality, Elaboration (0-3) puanla. JSON döndür: {{'Fluency':int, 'Flex':int, 'Orig':int, 'Elab':int}}")
        
        # EI Hesaplama
        ei_total = sum(ei_responses)
        ei_sea = sum(ei_responses[0:4])
        ei_oea = sum(ei_responses[4:8])
        ei_uoe = sum(ei_responses[8:12])
        ei_roe = sum(ei_responses[12:16])

        # Google Sheets Kayıt
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        final_row = {
            "EI_Total": ei_total, "EI_SEA": ei_sea, "EI_OEA": ei_oea, "EI_UOE": ei_uoe, "EI_ROE": ei_roe,
            "S1_D": s1.get('D1',0) if s1 else 0, "S1_C": s1.get('C1',0) if s1 else 0,
            "S4_Fluency": s4.get('Fluency',0) if s4 else 0,
            "Overall_CPS": (s1.get('D1',0) + s4.get('Fluency',0)) # Örnek toplama
        }
        
        df = pd.DataFrame([final_row])
        conn.create(data=df)
        
        st.success("Tebrikler! Cevaplarınız ve AI puanlarınız Google Sheets'e kaydedildi.")
        st.balloons()
