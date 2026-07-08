import streamlit as st
import pandas as pd
import sqlite3

# Povezivanje sa bazom podataka (automatski se kreira fajl)
conn = sqlite3.connect('vip_podaci.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS beleške 
             (uid TEXT PRIMARY KEY, status_closure TEXT, zadovoljan TEXT, voli TEXT, napomena TEXT)''')
conn.commit()

st.title("VIP Asistent - Tvoj BO")

# Upload CSV-a
uploaded_file = st.file_uploader("Ubaci CSV izveštaj", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Podaci učitani:")
    st.dataframe(df)

    # Pretraga igrača
    uid_search = st.text_input("Ukucaj UID igrača da vidiš karton:")
    
    if uid_search:
        # Pretraga po koloni 'customer_id' (to je UID iz tvog izveštaja)
        igrac = df[df['customer_id'].astype(str) == uid_search]
        
        if not igrac.empty:
            st.subheader(f"Karton igrača: {uid_search}")
            st.write(igrac)
            
            # Unos beleški u formu
            with st.form("unos_beleški"):
                closure = st.text_input("Status (npr. Tražio closure?)")
                zadovoljan = st.text_input("Zadovoljan?")
                voli = st.text_input("Voli (npr. Bonus/FS/Cashback)?")
                napomena = st.text_area("Dodatna napomena")
                
                submitted = st.form_submit_button("Sačuvaj u karton")
                
                if submitted:
                    c.execute("REPLACE INTO beleške VALUES (?,?,?,?,?)", 
                              (uid_search, closure, zadovoljan, voli, napomena))
                    conn.commit()
                    st.success("Sačuvano!")
        else:
            st.error("Igrač nije nađen u ovom CSV-u.")

# Prikaz svih sačuvanih beleški (da ne zaboraviš šta si pisala)
if st.checkbox("Prikaži sve moje beleške"):
    st.write(pd.read_sql("SELECT * FROM beleške", conn))
