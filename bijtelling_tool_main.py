
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Bijtelling & Btw Correctie Tool", layout="centered")
st.title("Auto-bijtelling & Btw-correctie Tool")

kenteken = st.text_input("Voer het kenteken in (zonder streepjes)", "").replace("-", "").upper()
auto_type = st.selectbox("Is het een marge- of btw-auto?", ["btw", "marge"])
gebruiker = st.selectbox("Type gebruiker", ["IB-ondernemer", "DGA"])
bruto_loon = st.number_input("Bruto jaarloon (voor netto bijtelling)", value=45000)
autokosten = st.number_input("Totale autokosten (voor max. bijtelling bij IB)", value=3000.0)

if kenteken:
    rdw_url = f"https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={kenteken}"
    response = requests.get(rdw_url)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        catalogusprijs = float(data.get("catalogusprijs", "0").replace(",", "."))
        toelating = data.get("datum_eerste_toelating_tenaamstelling", "")

        if toelating:
            jaar = int(toelating[:4])
            huidig_jaar = datetime.now().year
            leeftijd = huidig_jaar - jaar
        else:
            leeftijd = 0

        bijtelling_percentage = 0.22  # standaard
        bruto_bijtelling = catalogusprijs * bijtelling_percentage

        if gebruiker == "IB-ondernemer":
            bijtelling = min(bruto_bijtelling, autokosten)
        else:
            bijtelling = bruto_bijtelling

        netto_dag = (bijtelling / 365) * 0.37  # 37% tarief

        if auto_type == "btw":
            btw_perc = 0.015 if leeftijd > 5 else 0.027
            btw_correctie = catalogusprijs * btw_perc
        else:
            btw_correctie = 0

        st.success("Resultaten")
        st.write(f"**Catalogusprijs**: €{catalogusprijs:,.2f}")
        st.write(f"**Leeftijd auto**: {leeftijd} jaar")
        st.write(f"**Bruto bijtelling**: €{bijtelling:,.2f}")
        st.write(f"**Netto bijtelling per dag** (geschat): €{netto_dag:.2f}")
        st.write(f"**BTW-correctie** (privégebruik): €{btw_correctie:,.2f}")

    else:
        st.error("Geen voertuiggegevens gevonden. Controleer het kenteken.")
