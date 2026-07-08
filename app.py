import streamlit as st
import pandas as pd
import sqlite3

# Povezivanje na bazu
conn = sqlite3.connect('vip_podaci.db')
c = conn.cursor()

# Kreiramo tabelu
c.execute('''CREATE TABLE IF NOT EXISTS baza_igraca 
             (uid TEXT, mesec TEXT, iznos REAL, brand TEXT, segment TEXT, closure TEXT, zadovoljan TEXT, voli TEXT, napomena TEXT)''')
conn.commit()

st.title("VIP Asistent - Tvoj BO")

uploaded_file = st.file_uploader("Ubaci CSV izveštaj", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Podaci učitani. Unesi mesec za ove podatke:")
    mesec_input = st.text_input("Mesec/godina (npr. Jul 2026)")
    
    if st.button("Učitaj i ažuriraj bazu") and mesec_input:
        for index, row in df.iterrows():
            # Ovde smo promenili 'segment' u 'vips' da odgovara tvom fajlu
            uid = str(row['customer_id'])
            iznos = row['bins']
            brand = row['brand']
            segment = row['vips'] 
            
            c.execute("INSERT INTO baza_igraca (uid, mesec, iznos, brand, segment) VALUES (?,?,?,?,?)", 
                      (uid, mesec_input, iznos, brand, segment))
        conn.commit()
        st.success("Svi podaci su uspešno raspoređeni u bazu!")

st.divider()

# Pretraga
uid_search = st.text_input("Ukucaj UID igrača:")
if uid_search:
    istorija = pd.read_sql(f"SELECT * FROM baza_igraca WHERE uid='{uid_search}'", conn)
    st.write("Istorija igrača:")
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
            st.success("Beleške sačuvane!")
