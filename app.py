import streamlit as st
import pandas as pd

def fuzzify4(value, 
             poor_min, poor_max,
             low_min, low_max,
             med_min, med_max,
             high_min, high_max):
    if value < poor_min:
        return "Poor"

    if value > high_max:
        return "High"

    if poor_min <= value <= poor_max:
        return "Poor"
    if low_min <= value <= low_max:
        return "Low"
    if med_min <= value <= med_max:
        return "Medium"
    if high_min <= value <= high_max:
        return "High"

    mids = {
        "Poor": (poor_min + poor_max) / 2,
        "Low": (low_min + low_max) / 2,
        "Medium": (med_min + med_max) / 2,
        "High": (high_min + high_max) / 2
    }
    
    distances = {k: abs(value - v) for k, v in mids.items()}
    return min(distances, key=distances.get)


def fuzzy_humidity(x):
    return fuzzify4(x, 70.1, 82.6, 78.6, 90.1, 86.3, 96.4, 91.7, 100.6)

def fuzzy_temperature(x):
    return fuzzify4(x, 22.4, 25.3, 24.0, 27.0, 25.7, 29.4, 27.9, 30.8)

def fuzzy_pressure(x):
    return fuzzify4(x, 1001, 1010, 1005, 1012, 1007, 1014, 1009, 1016)

def fuzzy_windspeed(x):
    return fuzzify4(x, 0.7, 4.9, 4.7, 12.3, 11.7, 21.4, 20.4, 44.1)

def fuzzy_dewpoint(x):
    return fuzzify4(x, 20.9, 24.0, 22.8, 25.0, 23.8, 26.3, 25.0, 26.8)


df_rules = pd.read_csv("rules.csv")


def parse_condition(cond):
    cond = str(cond).strip()

    if cond.upper() == "ANY":
        return {"type": "any"}

    if cond.startswith("!="):
        val = cond.replace("!=", "").strip()
        return {"type": "not", "value": val}

    if "AND" in cond:
        parts = [c.strip() for c in cond.split("AND")]
        parsed_parts = []
        for p in parts:
            if p.startswith("!="):
                parsed_parts.append({"type": "not", "value": p.replace("!=", "").strip()})
            else:
                parsed_parts.append({"type": "eq", "value": p})
        return {"type": "and", "values": parsed_parts}

    return {"type": "eq", "value": cond}


def check_condition(rule_cond, fuzzy_value):
    ctype = rule_cond["type"]

    if ctype == "any":
        return True

    if ctype == "eq":
        return fuzzy_value == rule_cond["value"]

    if ctype == "not":
        return fuzzy_value != rule_cond["value"]

    if ctype == "and":
        for sub in rule_cond["values"]:
            if sub["type"] == "eq" and fuzzy_value != sub["value"]:
                return False
            if sub["type"] == "not" and fuzzy_value == sub["value"]:
                return False
        return True

    return False


def match_rules_from_csv(h, t, p, w, d):
    for _, row in df_rules.iterrows():

        cond_h = parse_condition(row["Humidity"])
        cond_t = parse_condition(row["Temperature"])
        cond_p = parse_condition(row["Pressure"])
        cond_w = parse_condition(row["WindSpeed"])
        cond_d = parse_condition(row["DewPoint"])

        if (check_condition(cond_h, h) and
            check_condition(cond_t, t) and
            check_condition(cond_p, p) and
            check_condition(cond_w, w) and
            check_condition(cond_d, d)):
            return row["Output"]

    return "No Rule Matched"


st.set_page_config(page_title="Fuzzy Weather Prediction", page_icon="⛅", layout="centered")

st.title("⛅ Fuzzy Weather Prediction App")
st.write("Masukkan nilai cuaca, lalu sistem fuzzy akan memprediksi **Rain / No Rain**.")

st.subheader("Input Data")

humidity = st.number_input("Humidity", min_value=0.0, format="%.2f")
temp = st.number_input("Temperature", min_value=0.0, format="%.2f")
pressure = st.number_input("Pressure", min_value=0.0, format="%.2f")
wind = st.number_input("Wind Speed", min_value=0.0, format="%.2f")
dew = st.number_input("Dew Point", min_value=0.0, format="%.2f")

if st.button("Prediksi Cuaca"):
    fh = fuzzy_humidity(humidity)
    ft = fuzzy_temperature(temp)
    fp = fuzzy_pressure(pressure)
    fw = fuzzy_windspeed(wind)
    fd = fuzzy_dewpoint(dew)

    st.subheader("Hasil Fuzzy")
    st.write(f"**Humidity**: {fh}")
    st.write(f"**Temperature**: {ft}")
    st.write(f"**Pressure**: {fp}")
    st.write(f"**Wind Speed**: {fw}")
    st.write(f"**Dew Point**: {fd}")

    result = match_rules_from_csv(fh, ft, fp, fw, fd)

    st.subheader("Hasil Prediksi")
    if result == "Rain":
        st.success("🌧️ **Rain**")
    elif result == "No Rule Matched":
        st.warning("⚠️ Tidak ada rule yang cocok")
    else:
        st.info("☀️ **No Rain**")
