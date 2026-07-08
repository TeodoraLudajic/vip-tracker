import streamlit as st
import pandas as pd
import sqlite3

# Povezivanje na bazu
conn = sqlite3.connect('vip_podaci.db', check_same_thread=False)
c = conn.cursor()

# Funkcija za pametno učitavanje podataka
@st.cache_data
def get_data(uid):
    return pd.read_sql(f"SELECT * FROM baza_igraca WHERE uid='{uid}'", conn)

st.title("VIP Asistent - Tvoj BO")

uploaded_file = st.file_uploader("Ubaci CSV izveštaj", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    mesec_input = st.text_input("Mesec/godina (npr. Jul 2026)")
    
    if st.button("Učitaj i ažuriraj bazu") and mesec_input:
        for index, row in df.iterrows():
            uid = str(row['customer_id'])
            iznos = row['bins']
            brand = row['brand']
            segment = row['vips'] 
            c.execute("INSERT INTO baza_igraca (uid, mesec, iznos, brand, segment) VALUES (?,?,?,?,?)", 
                      (uid, mesec_input, iznos, brand, segment))
        conn.commit()
        st.success("Svi podaci su ubačeni!")

st.divider()

uid_search = st.text_input("Ukucaj UID igrača:")

if uid_search:
    istorija = get_data(uid_search) # Koristimo keširanu funkciju
    
    if not istorija.empty:
        st.write("### Istorija igrača:")
        st.dataframe(istorija)
        
        with st.form("update_beleški"):
            c_status = st.text_input("Status closure?")
            zad = st.text_input("Zadovoljan?")
            vol = st.text_input("Voli (Bonus/FS)?")
            nap = st.text_area("Napomena")
            if st.form_submit_button("Sačuvaj beleške"):
                c.execute("UPDATE baza_igraca SET closure=?, zadovoljan=?, voli=?, napomena=? WHERE uid=?", 
                          (c_status, zad, vol, nap, uid_search))
                conn.commit()
                st.success("Sačuvano! Osveži stranicu da vidiš promene.")
    else:
        st.warning("Nema podataka za ovaj UID.")
