
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Bijtelling & Btw Correctie Tool", layout="centered")
st.markdown("<h1 style='color:#002e5d;'>iQOUNT - Auto-bijtelling & Btw-correctie Tool</h1>", unsafe_allow_html=True)

kenteken = st.text_input("Voer het kenteken in (zonder streepjes)", "").replace("-", "").upper()
auto_type = st.selectbox("Is het een marge- of btw-auto?", ["btw", "marge"])
gebruiker = st.selectbox("Type gebruiker", ["IB-ondernemer", "DGA"])
bruto_loon = st.number_input("Bruto jaarloon (voor netto bijtelling)", value=45000)

st.subheader("Autokosten")
lease_rente = st.number_input("Rentelasten leaseverplichting", value=0.0)
lease_operational = st.number_input("Operational leasekosten", value=0.0)
verzekering = st.number_input("Verzekeringskosten", value=0.0)
brandstof = st.number_input("Brandstofkosten", value=0.0)
onderhoud = st.number_input("Reparatie en onderhoudskosten", value=0.0)
wegenbelasting = st.number_input("Motorrijtuigenbelasting", value=0.0)
overige_kosten = st.number_input("Overige autokosten", value=0.0)
btw_correctie_input = st.number_input("Btw privé gebruik (voor controle, wordt ook berekend)", value=0.0)

autokosten = sum([lease_rente, lease_operational, verzekering, brandstof, onderhoud, wegenbelasting, overige_kosten, btw_correctie_input])

if kenteken:
    rdw_url = f"https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={kenteken}"
    response = requests.get(rdw_url)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        catalogusprijs = float(data.get("catalogusprijs", "0").replace(",", "."))
        toelating = data.get("datum_eerste_toelating", "")  # YYYYMMDD
        tenaamstelling = data.get("datum_tenaamstelling", "")  # YYYYMMDD

        gebruiksjaar = int(tenaamstelling[:4]) if tenaamstelling else datetime.now().year
        bouwjaar = int(toelating[:4]) if toelating else datetime.now().year
        huidig_jaar = datetime.now().year
        leeftijd = huidig_jaar - bouwjaar

        bijtelling_percentage = 0.22
        bruto_bijtelling = catalogusprijs * bijtelling_percentage

        if gebruiker == "IB-ondernemer":
            bijtelling = min(bruto_bijtelling, autokosten)
        else:
            bijtelling = bruto_bijtelling

        netto_maand = (bijtelling / 12) * 0.37  # 37% IB tarief gesimplificeerd

        if auto_type == "btw":
            btw_perc = 0.015 if leeftijd > 5 else 0.027
            btw_correctie = catalogusprijs * btw_perc
        else:
            btw_correctie = 0

        st.success("Resultaten")
        st.markdown(f"**Catalogusprijs**: €{catalogusprijs:,.2f}")
        st.markdown(f"**Leeftijd auto** (volgens eerste toelating): {leeftijd} jaar")
        st.markdown(f"**Gebruiksjaar** (volgens laatste tenaamstelling): {gebruiksjaar}")

        st.subheader("Berekening bijtelling")
        st.markdown(f"**Bruto bijtelling**: €{bruto_bijtelling:,.2f} (22% van catalogusprijs)")
        st.markdown(f"**Totale autokosten** (som ingevoerde kosten): €{autokosten:,.2f}")
        st.markdown(f"**Bijtelling toegepast**: €{bijtelling:,.2f}")
        st.markdown(f"**Netto bijtelling per maand** (geschat 37%): €{netto_maand:.2f}")

        st.subheader("Btw-correctie privégebruik")
        if auto_type == "btw":
            st.markdown(f"**Btw percentage**: {'1,5%' if leeftijd > 5 else '2,7%'}")
            st.markdown(f"**Btw-correctie**: €{btw_correctie:,.2f}")
        else:
            st.markdown("Geen btw-correctie voor marge-auto.")

    else:
        st.error("Geen voertuiggegevens gevonden. Controleer het kenteken.")
