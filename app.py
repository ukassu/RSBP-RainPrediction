import streamlit as st
import pandas as pd
import os
import numpy as np

def trapezoid(x, a, b, c, d):
    if x <= a or x >= d:
        return 0
    elif b <= x <= c:
        return 1
    elif a < x < b:
        return (x - a) / (b - a)
    else:
        return (d - x) / (d - c)

def fuzzify4(value, 
             poor_min, poor_max,
             low_min, low_max,
             med_min, med_max,
             high_min, high_max):

    memberships = {
        "Poor": trapezoid(value, poor_min-5, poor_min, poor_max, poor_max+5),
        "Low": trapezoid(value, low_min-5, low_min, low_max, low_max+5),
        "Medium": trapezoid(value, med_min-5, med_min, med_max, med_max+5),
        "High": trapezoid(value, high_min-5, high_min, high_max, high_max+5)
    }

    label = max(memberships, key=memberships.get)
    return label, memberships

def fuzzy_humidity(x): return fuzzify4(x, 70.1, 82.6, 78.6, 90.1, 86.3, 96.4, 91.7, 100.6)
def fuzzy_temperature(x): return fuzzify4(x, 22.4, 25.3, 24.0, 27.0, 25.7, 29.4, 27.9, 30.8)
def fuzzy_pressure(x): return fuzzify4(x, 1001, 1010, 1005, 1012, 1007, 1014, 1009, 1016)
def fuzzy_windspeed(x): return fuzzify4(x, 0.7, 4.9, 4.7, 12.3, 11.7, 21.4, 20.4, 44.1)
def fuzzy_dewpoint(x): return fuzzify4(x, 20.9, 24.0, 22.8, 25.0, 23.8, 26.3, 25.0, 26.8)

if os.path.exists("rules.csv"):
    df_rules = pd.read_csv("rules.csv")
else:
    df_rules = pd.DataFrame(columns=["Humidity", "Temperature", "Pressure", "WindSpeed", "DewPoint", "Output"])

def parse_condition(cond):
    cond = str(cond).strip()
    if cond.upper() == "ANY": return {"type": "any"}
    if cond.startswith("!="):
        return {"type": "not", "value": cond.replace("!=", "").strip()}
    if "AND" in cond:
        parts = [p.strip() for p in cond.split("AND")]
        parsed = []
        for p in parts:
            if p.startswith("!="):
                parsed.append({"type": "not", "value": p.replace("!=", "").strip()})
            else:
                parsed.append({"type": "eq", "value": p})
        return {"type": "and", "values": parsed}
    return {"type": "eq", "value": cond}

def check_condition(rule_cond, fuzzy_value):
    ctype = rule_cond["type"]
    if ctype == "any": return True
    if ctype == "eq": return fuzzy_value == rule_cond["value"]
    if ctype == "not": return fuzzy_value != rule_cond["value"]
    if ctype == "and":
        for sub in rule_cond["values"]:
            if sub["type"] == "eq" and fuzzy_value != sub["value"]: return False
            if sub["type"] == "not" and fuzzy_value == sub["value"]: return False
        return True
    return False

def match_rules_from_csv(fh, ft, fp, fw, fd):
    for idx, row in df_rules.iterrows():
        cond_h = parse_condition(row["Humidity"])
        cond_t = parse_condition(row["Temperature"])
        cond_p = parse_condition(row["Pressure"])
        cond_w = parse_condition(row["WindSpeed"])
        cond_d = parse_condition(row["DewPoint"])

        if (check_condition(cond_h, fh) and
            check_condition(cond_t, ft) and
            check_condition(cond_p, fp) and
            check_condition(cond_w, fw) and
            check_condition(cond_d, fd)):
            
            return idx+1, row

    return None, None

st.set_page_config(page_title="Expert System for Rain Forecasting Using Fuzzy Rule-Based", page_icon="🌦️", layout="centered")

st.title("🌦️ Expert System for Rain Forecasting Using Fuzzy Rule-Based")
st.markdown(
    "Masukkan nilai cuaca, lalu sistem akan memberikan hasil prediksi "
    "**Rain / No Rain** disertai penjelasan singkat bagaimana keputusan dibuat."
)

with st.expander("ℹ️ Apa itu Fuzzy Logic? (Penjelasan untuk Pengguna)"):
    st.markdown("""
### 🧩 1. Apa Itu Fuzzy Logic?
Fuzzy logic adalah metode pengambilan keputusan yang **meniru cara manusia berpikir**. 
Tidak semua hal di dunia ini tegas (0 atau 1, benar atau salah).  
Dalam cuaca misalnya, tidak ada batas *tepat* kapan suhu dianggap panas atau dingin — semua bersifat **kabur (fuzzy)**.

Fuzzy logic mengubah nilai numerik (misalnya suhu 27°C) menjadi kategori seperti:
- **Poor**
- **Low**
- **Medium**
- **High**

Kategori ini memiliki tingkat keanggotaan (*membership degree*) antara **0 sampai 1**, bukan hanya 0 atau 1 saja.

---

### 🧠 2. Bagaimana Fuzzy Logic Bekerja di Sistem Ini?

Prosesnya terdiri dari **4 langkah:**

---

#### **🔹 A. Fuzzification**
Input seperti *humidity, temperature, pressure, wind speed,* dan *dew point* diubah menjadi kategori fuzzy  
misalnya:
- Humidity → **High**
- Temperature → **Medium**

Ini dilakukan dengan fungsi bentuk **trapezoid** yang menentukan seberapa besar nilai masuk ke setiap kategori.

---

#### **🔹 B. Rule Matching**
Sistem memiliki **Basis Pengetahuan** yang berisi aturan untuk pengambilan keputusan. Aturan - aturan ini diperolah dari pengolahan data pola historis cuaca.

Contoh rule:


Hasil fuzzification tadi dibandingkan dengan semua rule untuk mencari rule yang paling cocok.

---

#### **🔹 C. Inference (Penalaran)**
Jika sebuah rule sesuai, maka rule tersebut dianggap menggambarkan pola cuaca yang mirip dengan kondisi Anda.

---

#### **🔹 D. Decision Making (Prediksi Akhir)**
Output dari rule yang cocok menentukan hasil final:
- **Rain**, atau
- **No Rain**

Dengan ini, keputusan menjadi:
- **transparan**
- **dapat dijelaskan**
- **berbasis pengetahuan historis cuaca**

---

### 🔍 Kesimpulan
Fuzzy logic membantu sistem memahami kondisi cuaca **secara lebih manusiawi**, tidak kaku, dan memberikan keputusan yang dapat dijelaskan berdasarkan rule yang jelas.
    """)

if df_rules.empty:
    st.error("⚠️ File 'rules.csv' tidak ditemukan.")
    st.stop()

st.subheader("Masukkan Data Cuaca")

col1, col2 = st.columns(2)
with col1:
    humidity = st.number_input("Humidity (%)", 0.0, 100.0)
    temp = st.number_input("Temperature (°C)", -10.0, 50.0)
    pressure = st.number_input("Pressure (hPa)", 800.0, 1200.0)

with col2:
    wind = st.number_input("Wind Speed (km/h)", 0.0, 100.0)
    dew = st.number_input("Dew Point (°C)", -10.0, 50.0)

if st.button("🔍 Analisis Cuaca", type="primary"):

    fh, mh = fuzzy_humidity(humidity)
    ft, mt = fuzzy_temperature(temp)
    fp, mp = fuzzy_pressure(pressure)
    fw, mw = fuzzy_windspeed(wind)
    fd, md = fuzzy_dewpoint(dew)

    st.divider()
    st.subheader("🧠 Interpretasi Fuzzy")

    st.markdown(
        f"Dari nilai cuaca yang Anda masukkan, sistem menerjemahkannya ke dalam "
        f"kategori fuzzy sebagai berikut:\n\n"
        f"- **Humidity (Kelembapan):** {fh}\n"
        f"- **Temperature (Suhu):** {ft}\n"
        f"- **Pressure (Tekanan Udara):** {fp}\n"
        f"- **Wind Speed (Kecepatan Angin):** {fw}\n"
        f"- **Dew Point:** {fd}\n\n"
        "Interpretasi fuzzy ini digunakan sebagai pola untuk mencocokkan rule berbasis pengetahuan "
        "yang tersimpan di dalam **Basis Pengetahuan Sistem**."
    )

    idx, matched_rule = match_rules_from_csv(fh, ft, fp, fw, fd)

    st.divider()
    st.subheader("Penjelasan Keputusan – Naratif")

    if matched_rule is None:
        st.warning(
            "❗ Tidak ditemukan rule yang cocok dengan pola kondisi cuaca Anda. "
            "Ini berarti kombinasi fuzzy yang terbentuk belum pernah muncul atau belum memiliki "
            "pola dalam data historis hujan."
        )
        st.stop()

    output = matched_rule["Output"]

    if output.strip().lower() == "rain":
        st.success(f"Rule #{idx} cocok → Prediksi: **{output}**")
    else:
        st.error(f"Rule #{idx} cocok → Prediksi: **{output}**")

    st.markdown(
        f"Model fuzzy menemukan bahwa kondisi cuaca yang Anda masukkan paling cocok "
        f"dengan **Rule #{idx}** dalam basis pengetahuan sistem.\n\n"
        
        f"Rule ini terbentuk dari pola historis kondisi cuaca yang pernah terjadi sebelumnya "
        f"pada dataset hujan, sehingga rule yang cocok menandakan bahwa **kombinasi kategori fuzzy "
        f"Anda sangat mirip dengan pola cuaca nyata yang pernah menghasilkan kejadian `{output}`**.\n\n"

        "Berikut penjelasan naratif bagaimana rule tersebut cocok:\n"
        "1. **Kelembapan** Anda termasuk kategori *" + fh + "* yang biasanya menjadi faktor penting dalam pembentukan awan.\n"
        "2. **Suhu udara** berada pada kategori *" + ft + "*, yang memengaruhi proses penguapan dan kondensasi.\n"
        "3. **Tekanan atmosfer** berada pada kondisi *" + fp + "*, dan tekanan rendah sering kali terkait dengan cuaca tidak stabil.\n"
        "4. **Kecepatan angin** terklasifikasi sebagai *" + fw + "*, yang dapat mengindikasikan pergerakan massa udara tertentu.\n"
        "5. **Dew Point** atau titik embun masuk kategori *" + fd + "*, yang berhubungan langsung dengan potensi terbentuknya uap air di udara.\n\n"

        f"Ketika kelima variabel ini dibandingkan dengan rule di dalam **Basis Pengetahuan**, seluruh syarat "
        f"dalam Rule #{idx} terpenuhi. Karena itu, sistem menyimpulkan bahwa kondisi cuaca Anda "
        f"paling mendekati pola yang menghasilkan: **{output}**.\n\n"

        # "---\n"
        # "📝 **Catatan**: Rule di dalam sistem berasal dari analisis dataset cuaca, di mana pola-pola "
        # "tertentu membentuk aturan berbasis hubungan fuzzy. Dengan demikian, keputusan sistem "
        # "bersifat *explainable*, bukan sekadar hasil hitungan matematis."
    )

    # with st.expander("Lihat Isi Rule yang Cocok"):
    #     st.json(matched_rule.to_dict())