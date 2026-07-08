import streamlit as st
import pandas as pd
import sqlite3

# Povezivanje sa bazom
conn = sqlite3.connect('vip_podaci.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS beleške 
             (uid TEXT PRIMARY KEY, status_closure TEXT, zadovoljan TEXT, voli TEXT, napomena TEXT)''')
conn.commit()

st.title("VIP Asistent - Tvoj BO")

uploaded_file = st.file_uploader("Ubaci CSV izveštaj", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Filter po brendu
    if 'brand' in df.columns:
        kazina = ["Svi"] + df['brand'].unique().tolist()
        izabrani_kazino = st.selectbox("Izaberi kazino/brend:", kazina)
        if izabrani_kazino != "Svi":
            df = df[df['brand'] == izabrani_kazino]
    
    st.write(f"Pregled podataka:")
    st.dataframe(df)

    # Pretraga
    uid_search = st.text_input("Ukucaj UID:")
    if uid_search:
        igrac = df[df['customer_id'].astype(str) == uid_search]
        if not igrac.empty:
            st.write(igrac)
            with st.form("unos_beleški"):
                closure = st.text_input("Status (npr. Tražio closure?)")
                zadovoljan = st.text_input("Zadovoljan?")
                voli = st.text_input("Voli (Bonus/FS/Cashback)?")
                napomena = st.text_area("Dodatna napomena")
                submitted = st.form_submit_button("Sačuvaj u karton")
                if submitted:
                    c.execute("REPLACE INTO beleške VALUES (?,?,?,?,?)", (uid_search, closure, zadovoljan, voli, napomena))
                    conn.commit()
                    st.success("Sačuvano!")
        else:
            st.error("Igrač nije nađen u ovom izveštaju.")
