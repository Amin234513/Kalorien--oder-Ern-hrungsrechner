import streamlit as st
import pandas as pd
import numpy as np

# ===== KLARES, FUNKTIONALES DESIGN =====
st.set_page_config(
    layout="centered", 
    page_title="📊 Wissenschaftlicher Kalorienrechner",
    page_icon="⚖️"
)

# Minimalistisches CSS
st.markdown("""
<style>
:root {
    --primary: #3498db;
    --secondary: #2c3e50;
    --accent: #e74c3c;
}
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #333;
}
.stApp {
    max-width: 900px;
    margin: 0 auto;
}
.stButton button {
    background-color: var(--primary) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}
.stProgress > div > div {
    background-color: var(--primary) !important;
}
.stMetric {
    border-left: 4px solid var(--primary);
    padding-left: 1rem;
}
h1, h2, h3 {
    color: var(--secondary);
}
</style>
""", unsafe_allow_html=True)

# ===== DATENSTRUKTUREN =====
if 'lebensmittel_log' not in st.session_state:
    st.session_state.lebensmittel_log = pd.DataFrame(
        columns=['Zeit', 'Lebensmittel', 'Menge', 'Kalorien', 'Protein', 'Fett', 'Kohlenhydrate']
    )

# ===== BENUTZERPROFIL =====
st.title("📊 Wissenschaftlicher Kalorienrechner")
with st.expander("👤 Persönliches Profil", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        geschlecht = st.radio("Geschlecht", ["Männlich", "Weiblich"], index=0)
        alter = st.number_input("Alter", min_value=18, max_value=100, value=30)
        groesse = st.number_input("Größe (cm)", min_value=100, max_value=250, value=180)
    
    with col2:
        gewicht = st.number_input("Aktuelles Gewicht (kg)", min_value=40.0, value=80.0, step=0.5)
        zielgewicht = st.number_input("Zielgewicht (kg)", min_value=40.0, value=75.0, step=0.5)
        aktivitaet = st.selectbox("Aktivitätslevel", [
            "Sitzend (kaum Bewegung)",
            "Leicht aktiv (1-3 Tage/Woche)",
            "Mäßig aktiv (3-5 Tage/Woche)",
            "Sehr aktiv (6-7 Tage/Woche)",
            "Extrem aktiv (Sport + körperl. Arbeit)"
        ], index=2)
    
    ziel = st.radio("Ziel", ["Gewicht halten", "Abnehmen", "Muskelaufbau"], index=1)

# ===== KALORIENBEDARFSBERECHNUNG =====
def berechne_kalorienbedarf():
    # Grundumsatz (Harris-Benedict-Formel)
    if geschlecht == "Männlich":
        grundumsatz = 88.362 + (13.397 * gewicht) + (4.799 * groesse) - (5.677 * alter)
    else:
        grundumsatz = 447.593 + (9.247 * gewicht) + (3.098 * groesse) - (4.330 * alter)
    
    # Aktivitätsfaktor
    aktivitaetsfaktoren = [1.2, 1.375, 1.55, 1.725, 1.9]
    aktiv_index = ["Sitzend", "Leicht", "Mäßig", "Sehr", "Extrem"].index(aktivitaet.split()[0])
    gesamtumsatz = grundumsatz * aktivitaetsfaktoren[aktiv_index]
    
    # Zielanpassung
    if ziel == "Abnehmen":
        zielkalorien = gesamtumsatz - 500
    elif ziel == "Muskelaufbau":
        zielkalorien = gesamtumsatz + 300
    else:
        zielkalorien = gesamtumsatz
    
    return {
        "grundumsatz": grundumsatz,
        "gesamtumsatz": gesamtumsatz,
        "zielkalorien": zielkalorien
    }

# Berechnung durchführen
kalorien_daten = berechne_kalorienbedarf()

# ===== ERGEBNISSE ANZEIGEN =====
st.subheader("📈 Dein Energiebedarf")
col1, col2, col3 = st.columns(3)
col1.metric("🔥 Grundumsatz", f"{kalorien_daten['grundumsatz']:.0f} kcal")
col2.metric("⚡ Gesamtumsatz", f"{kalorien_daten['gesamtumsatz']:.0f} kcal")
col3.metric("🎯 Tagesziel", f"{kalorien_daten['zielkalorien']:.0f} kcal", 
            delta=f"{(kalorien_daten['zielkalorien'] - kalorien_daten['gesamtumsatz']):+.0f} kcal" if ziel != "Gewicht halten" else None)

st.progress(min(1.0, st.session_state.lebensmittel_log['Kalorien'].sum() / kalorien_daten['zielkalorien']))
st.caption(f"Kalorien verbraucht: {st.session_state.lebensmittel_log['Kalorien'].sum():.0f} / {kalorien_daten['zielkalorien']:.0f} kcal")

# =%% MAKRONÄHRSTOFFE %%===
st.subheader("🍽️ Makronährstoffverteilung")
protein_ziel = gewicht * 1.8 if ziel == "Muskelaufbau" else gewicht * 1.2
fett_ziel = kalorien_daten['zielkalorien'] * 0.25 / 9  # 25% der Kalorien aus Fett
kohlenhydrate_ziel = (kalorien_daten['zielkalorien'] - (protein_ziel * 4 + fett_ziel * 9)) / 4

col1, col2, col3 = st.columns(3)
col1.metric("🥩 Protein-Ziel", f"{protein_ziel:.1f}g")
col2.metric("🥑 Fett-Ziel", f"{fett_ziel:.1f}g")
col3.metric("🍞 KH-Ziel", f"{kohlenhydrate_ziel:.1f}g")

# ===== LEBENSMITTEL-DATENBANK =====
NÄHRWERT_DB = {
    "Hähnchenbrust (100g)": {"Kalorien": 165, "Protein": 31, "Fett": 3.6, "Kohlenhydrate": 0},
    "Vollkornreis (100g gekocht)": {"Kalorien": 130, "Protein": 2.7, "Fett": 1, "Kohlenhydrate": 28},
    "Lachs (100g)": {"Kalorien": 208, "Protein": 20, "Fett": 13, "Kohlenhydrate": 0},
    "Avocado (1 Stück)": {"Kalorien": 160, "Protein": 2, "Fett": 15, "Kohlenhydrate": 9},
    "Haferflocken (50g)": {"Kalorien": 185, "Protein": 6.5, "Fett": 3.5, "Kohlenhydrate": 30},
    "Protein-Shake (1 Portion)": {"Kalorien": 120, "Protein": 24, "Fett": 2, "Kohlenhydrate": 4},
    "Gemischter Salat (100g)": {"Kalorien": 15, "Protein": 1.3, "Fett": 0.2, "Kohlenhydrate": 2.3},
    "Apfel (mittel)": {"Kalorien": 95, "Protein": 0.5, "Fett": 0.3, "Kohlenhydrate": 25},
    "Vollkornbrot (1 Scheibe)": {"Kalorien": 80, "Protein": 4, "Fett": 1, "Kohlenhydrate": 15},
    "Eier (1 Stück)": {"Kalorien": 78, "Protein": 6, "Fett": 5, "Kohlenhydrate": 0.6},
}

# ===== LEBENSMITTEL-ERFASSUNG =====
st.subheader("➕ Nahrungsaufnahme erfassen")
with st.form("nahrungsform"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        lebensmittel = st.selectbox("Lebensmittel", list(NÄHRWERT_DB.keys()))
    
    with col2:
        menge = st.number_input("Menge", min_value=1, value=100, step=10)
    
    if st.form_submit_button("Hinzufügen"):
        nährwerte = NÄHRWERT_DB[lebensmittel]
        faktor = menge / 100 if "(100g)" in lebensmittel else 1
        
        neuer_eintrag = pd.DataFrame([{
            "Zeit": pd.Timestamp.now().strftime("%H:%M"),
            "Lebensmittel": lebensmittel,
            "Menge": menge,
            "Kalorien": nährwerte["Kalorien"] * faktor,
            "Protein": nährwerte["Protein"] * faktor,
            "Fett": nährwerte["Fett"] * faktor,
            "Kohlenhydrate": nährwerte["Kohlenhydrate"] * faktor
        }])
        
        st.session_state.lebensmittel_log = pd.concat(
            [st.session_state.lebensmittel_log, neuer_eintrag], 
            ignore_index=True
        )
        st.success("Eintrag hinzugefügt!")

# ===== NAHRUNGS-PROTOKOLL =====
if not st.session_state.lebensmittel_log.empty:
    st.subheader("📋 Dein Ernährungstagebuch")
    
    # Tageszusammenfassung
    tages_summe = st.session_state.lebensmittel_log[['Kalorien', 'Protein', 'Fett', 'Kohlenhydrate']].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔥 Kalorien", f"{tages_summe['Kalorien']:.0f} kcal")
    col2.metric("🥩 Protein", f"{tages_summe['Protein']:.1f}g")
    col3.metric("🥑 Fett", f"{tages_summe['Fett']:.1f}g")
    col4.metric("🍞 Kohlenhydrate", f"{tages_summe['Kohlenhydrate']:.1f}g")
    
    # Makronährstoff-Balken
    protein_proz = min(1.0, tages_summe['Protein'] / protein_ziel)
    fett_proz = min(1.0, tages_summe['Fett'] / fett_ziel)
    kh_proz = min(1.0, tages_summe['Kohlenhydrate'] / kohlenhydrate_ziel)
    
    st.progress(protein_proz, text=f"Protein: {tages_summe['Protein']:.1f}g / {protein_ziel:.1f}g")
    st.progress(fett_proz, text=f"Fett: {tages_summe['Fett']:.1f}g / {fett_ziel:.1f}g")
    st.progress(kh_proz, text=f"Kohlenhydrate: {tages_summe['Kohlenhydrate']:.1f}g / {kohlenhydrate_ziel:.1f}g")
    
    # Detailtabelle
    st.dataframe(
        st.session_state.lebensmittel_log,
        hide_index=True,
        use_container_width=True
    )
    
    # Diagramm - Kalorienverteilung
    st.subheader("📊 Kalorienverteilung über den Tag")
    zeit_df = st.session_state.lebensmittel_log.copy()
    zeit_df['Uhrzeit'] = pd.to_datetime(zeit_df['Zeit'], format='%H:%M').dt.hour
    
    if not zeit_df.empty:
        st.bar_chart(zeit_df.groupby('Uhrzeit')['Kalorien'].sum())
    
    # Reset-Button
    if st.button("🔄 Tagesprotokoll zurücksetzen"):
        st.session_state.lebensmittel_log = st.session_state.lebensmittel_log.iloc[0:0]
        st.experimental_rerun()
else:
    st.info("ℹ️ Füge deine erste Mahlzeit hinzu, um deine Ernährung zu protokollieren.")

# ===== WISSENSDATENBANK =====
with st.expander("📚 Ernährungs-Wissen", expanded=True):
    tab1, tab2, tab3 = st.tabs(["Grundlagen", "Proteinquellen", "Tipps"])
    
    with tab1:
        st.markdown("""
        **Kalorienbedarf setzt sich zusammen aus:**
        1. **Grundumsatz (BMR):** Energie für Körperfunktionen im Ruhezustand
        2. **Leistungsumsatz:** Energie für Aktivitäten und Verdauung
        
        **Formel (Harris-Benedict):**  
        - Männer: `88.362 + (13.397 × Gewicht) + (4.799 × Größe) - (5.677 × Alter)`  
        - Frauen: `447.593 + (9.247 × Gewicht) + (3.098 × Größe) - (4.330 × Alter)`
        """)
        
    with tab2:
        st.markdown("""
        **Hochwertige Proteinquellen:**
        - Tierisch: Hähnchen, Pute, Eier, Fisch, Magerquark
        - Pflanzlich: Linsen, Kichererbsen, Tofu, Tempeh, Quinoa
        - Supplemente: Whey-Protein, Casein, vegane Proteinpulver
        
        **Empfohlene Zufuhr:**
        - Normal: 0.8-1.2g pro kg Körpergewicht
        - Kraftsport: 1.6-2.2g pro kg Körpergewicht
        """)
        
    with tab3:
        st.markdown("""
        **Praktische Ernährungstipps:**
        - Trinke 500ml Wasser vor jeder Mahlzeit
        - Protein zuerst essen (sättigender)
        - Gemüse sollte 50% deines Tellers ausmachen
        - Tracke dein Essen 2-3 Tage/Woche zur Sensibilisierung
        - Vermeide flüssige Kalorien (Softdrinks, Säfte)
        """)

# ===== EXPORT =====
if not st.session_state.lebensmittel_log.empty:
    csv = st.session_state.lebensmittel_log.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Protokoll als CSV exportieren",
        data=csv,
        file_name="ernaehrungsprotokoll.csv",
        mime="text/csv"
    )
