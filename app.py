import streamlit as st
import pandas as pd
import sqlite3

# Baza koja pamti sve
conn = sqlite3.connect('vip_podaci.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS baza_igraca 
             (uid TEXT, mesec TEXT, iznos REAL, closure TEXT, zadovoljan TEXT, voli TEXT, napomena TEXT)''')
conn.commit()

st.title("VIP Asistent - Tvoj BO")

uploaded_file = st.file_uploader("Ubaci CSV izveštaj (npr. Jul 2026)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    mesec_input = st.text_input("Koji je ovo mesec/godina? (npr. Jul 2026)")
    
    if st.button("Učitaj i ažuriraj bazu") and mesec_input:
        for index, row in df.iterrows():
            # Ovde upisuje automatski iz CSV-a
            c.execute("INSERT INTO baza_igraca (uid, mesec, iznos) VALUES (?,?,?)", 
                      (str(row['customer_id']), mesec_input, row['bins']))
        conn.commit()
        st.success("Podaci iz fajla su ubačeni u bazu!")

st.divider()

# Pretraga
uid_search = st.text_input("Ukucaj UID igrača:")
if uid_search:
    # Vadi sve iz baze
    istorija = pd.read_sql(f"SELECT * FROM baza_igraca WHERE uid='{uid_search}'", conn)
    st.write(istorija)
    
    # Forma za beleške (closure, voli, itd)
    with st.form("update_beleški"):
        c_status = st.text_input("Status closure?")
        zad = st.text_input("Zadovoljan?")
        vol = st.text_input("Voli (Bonus/FS)?")
        nap = st.text_area("Napomena")
        if st.form_submit_button("Sačuvaj beleške za ovog igrača"):
            c.execute("UPDATE baza_igraca SET closure=?, zadovoljan=?, voli=?, napomena=? WHERE uid=?", 
                      (c_status, zad, vol, nap, uid_search))
            conn.commit()
            st.success("Beleške sačuvane!")
