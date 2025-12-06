import streamlit as st

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


rules = [
    ("High","None","None","None","None","Rain"),
    ("High","None","None","Medium","None","Rain"),
    ("High","Medium","None","None","None","Rain"),
    ("High","Medium","Medium","None","None","Rain"),
    ("Medium","None","None","None","None","Rain"),
    ("Medium","None","High","None","None","Rain"),
    ("Medium","None","High","High","None","Rain"),
    ("High","None","None","None","Poor","Rain"),
    ("High","None","Poor","None","Poor","Rain"),
    ("High","High","None","None","Poor","No Rain"),
    ("Medium","None","None","None","Poor","Rain"),
    ("Medium","Poor","None","None","Poor","Rain"),
    ("Medium","None","Poor","None","Poor","Rain"),
    ("Poor","None","None","None","None","No Rain"),
    ("Poor","None","High","None","None","No Rain"),
    ("Poor","None","None","High","None","Rain"),
    ("Poor","None","Medium","High","None","Rain"),
    ("Poor","Low","None","None","None","Rain"),
    ("Poor","Low","None","Low","None","Rain"),
    ("Poor","Low","Medium","Low","None","No Rain"),
    ("Poor","None","None","None","Poor","No Rain"),
    ("Poor","None","Poor","None","Poor","No Rain"),
    ("Poor","Poor","None","None","Poor","Rain"),
    ("Poor","Poor","Poor","None","Poor","Rain"),
    ("Poor","High","None","None","Poor","No Rain"),
    ("Poor","High","Poor","None","Poor","No Rain"),
    ("Poor","High","Poor","Medium","Poor","No Rain"),
]



def match_rules(h, t, p, w, d):
    for rule in rules:
        r_h, r_t, r_p, r_w, r_d, output = rule

        def is_wildcard(r):
            return isinstance(r, str) and r.strip().lower() == "none"

        cond = (
            (is_wildcard(r_h) or r_h == h) and
            (is_wildcard(r_t) or r_t == t) and
            (is_wildcard(r_p) or r_p == p) and
            (is_wildcard(r_w) or r_w == w) and
            (is_wildcard(r_d) or r_d == d)
        )

        if cond:
            return output

    return "No Rule Matched"


st.set_page_config(page_title="Fuzzy Weather Prediction", page_icon="⛅", layout="centered")

st.title("⛅ Fuzzy Weather Prediction App")
st.write("Masukkan nilai cuaca, lalu sistem fuzzy akan memprediksi apakah akan **hujan** atau **tidak**.")

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

    result = match_rules(fh, ft, fp, fw, fd)

    st.subheader("Hasil Prediksi")
    if result == "Rain":
        st.success("🌧️ **Rain**")
    elif result == "No Rain":
        st.info("☀️ **No Rain**")
    else:
        st.warning("⚠️ Tidak ada rule yang cocok")
