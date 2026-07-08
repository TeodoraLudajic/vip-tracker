import streamlit as st
import pandas as pd
import sqlite3

# Baza sada čuva i 'brand'
conn = sqlite3.connect('vip_podaci.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS baza_igraca 
             (uid TEXT, mesec TEXT, iznos REAL, brand TEXT, closure TEXT, zadovoljan TEXT, voli TEXT, napomena TEXT)''')
conn.commit()

st.title("VIP Asistent - Tvoj BO")

uploaded_file = st.file_uploader("Ubaci CSV izveštaj", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    mesec_input = st.text_input("Koji je ovo mesec/godina?")
    
    if st.button("Učitaj i ažuriraj bazu") and mesec_input:
        for index, row in df.iterrows():
            # Upisuje UID, mesec, iznos I BRAND
            c.execute("INSERT INTO baza_igraca (uid, mesec, iznos, brand) VALUES (?,?,?,?)", 
                      (str(row['customer_id']), mesec_input, row['bins'], row['brand']))
        conn.commit()
        st.success("Podaci su ubačeni u bazu!")

st.divider()

uid_search = st.text_input("Ukucaj UID igrača:")
if uid_search:
    istorija = pd.read_sql(f"SELECT * FROM baza_igraca WHERE uid='{uid_search}'", conn)
    st.write("Istorija igrača:")
    st.write(istorija)
    
    with st.form("update_beleški"):
        c_status = st.text_input("Status closure?")
        zad = st.text_input("Zadovoljan?")
        vol = st.text_input("Voli (Bonus/FS)?")
        nap = st.text_area("Napomena")
        if st.form_submit_button("Sačuvaj beleške"):
            c.execute("UPDATE baza_igraca SET closure=?, zadovoljan=?, voli=?, napomena=? WHERE uid=?", 
                      (c_status, zad, vol, nap, uid_search))
            conn.commit()
            st.success("Sačuvano!")
