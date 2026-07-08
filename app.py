import streamlit as st
import pandas as pd
import sqlite3

# Povezivanje sa bazom (sada čuvamo i uplate)
conn = sqlite3.connect('vip_podaci.db')
c = conn.cursor()
# Tabela sada čuva UID, mesec, iznos i beleške
c.execute('''CREATE TABLE IF NOT EXISTS baza_igraca 
             (uid TEXT, mesec TEXT, iznos REAL, closure TEXT, zadovoljan TEXT, voli TEXT, napomena TEXT)''')
conn.commit()

st.title("VIP Asistent - Tvoj BO")

uploaded_file = st.file_uploader("Ubaci CSV izveštaj za tekući mesec", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Podaci učitani.")
    
    # Automatsko dodavanje u bazu (ovo bi bilo još preciznije kad mi daš primer kolona)
    # Ovde ćemo kasnije dodati kod koji automatski "knjiži" uplate u bazu

# Pretraga
uid_search = st.text_input("Ukucaj UID za istoriju kartona:")
if uid_search:
    # Program prikazuje sve podatke iz baze za taj UID (bez obzira na fajlove)
    istorija = pd.read_sql(f"SELECT * FROM baza_igraca WHERE uid='{uid_search}'", conn)
    st.write(istorija)
