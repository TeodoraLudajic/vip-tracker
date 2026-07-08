import streamlit as st
import pandas as pd
import sqlite3

# Povezivanje na bazu sa 'timeout' parametrom (čekaće 10 sekundi ako je baza zauzeta)
conn = sqlite3.connect('vip_podaci.db', check_same_thread=False, timeout=10)
c = conn.cursor()

# Kreiranje tabele (ako ne postoji)
c.execute('''CREATE TABLE IF NOT EXISTS baza_igraca 
             (uid TEXT, mesec TEXT, iznos REAL, brand TEXT, segment TEXT, closure TEXT, zadovoljan TEXT, voli TEXT, napomena TEXT)''')
conn.commit()

st.title("VIP Asistent - Tvoj BO")

uploaded_file = st.file_uploader("Ubaci CSV izveštaj", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    mesec_input = st.text_input("Mesec/godina:")
    if st.button("Učitaj u bazu") and mesec_input:
        for _, row in df.iterrows():
            c.execute("INSERT INTO baza_igraca (uid, mesec, iznos, brand, segment) VALUES (?,?,?,?,?)", 
                      (str(row['customer_id']), mesec_input, row['bins'], row['brand'], row['vips']))
        conn.commit()
        st.success("Podaci ubačeni!")

st.divider()

uid_search = st.text_input("Ukucaj UID igrača:")

if uid_search:
    # Učitaj podatke
    df_search = pd.read_sql(f"SELECT * FROM baza_igraca WHERE uid='{uid_search}'", conn)
    
    if not df_search.empty:
        st.dataframe(df_search)
        
        # Forma za editovanje
        with st.form("edit_forma", clear_on_submit=True):
            c_status = st.text_input("Status closure?")
            zad = st.text_input("Zadovoljan?")
            vol = st.text_input("Voli (Bonus/FS)?")
            nap = st.text_area("Napomena")
            
            if st.form_submit_button("Sačuvaj"):
                try:
                    # SQL komanda za update
                    c.execute("""UPDATE baza_igraca 
                                 SET closure=?, zadovoljan=?, voli=?, napomena=? 
                                 WHERE uid=?""", 
                              (c_status, zad, vol, nap, uid_search))
                    conn.commit()
                    st.success("Sačuvano! Osveži stranicu da vidiš promene.")
                except Exception as e:
                    st.error(f"Došlo je do greške: {e}")
    else:
        st.warning("Nema podataka za ovaj UID.")
