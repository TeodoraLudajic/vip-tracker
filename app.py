import streamlit as st
import pandas as pd
import sqlite3

# Povezivanje na bazu sa dozvolom za više korisnika (timeout čeka 10s da se baza otključa)
conn = sqlite3.connect('vip_podaci.db', check_same_thread=False, timeout=10)
c = conn.cursor()

# Kreiranje tabele ako ne postoji
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
    # Čitanje podataka
    df_search = pd.read_sql(f"SELECT * FROM baza_igraca WHERE uid='{uid_search}'", conn)
    
    if not df_search.empty:
        st.dataframe(df_search)
        
        # Forma za editovanje - pamti staro
        with st.form("edit_forma"):
            c_status = st.text_input("Status closure?")
            zad = st.text_input("Zadovoljan?")
            vol = st.text_input("Voli (Bonus/FS)?")
            nap = st.text_area("Napomena")
            
            if st.form_submit_button("Sačuvaj beleške"):
                # 1. Uzmemo šta već piše u bazi (poslednji unos za taj UID)
                stari_podaci = c.execute("SELECT closure, zadovoljan, voli, napomena FROM baza_igraca WHERE uid=? ORDER BY rowid DESC LIMIT 1", (uid_search,)).fetchone()
                
                # 2. Ako polje u formi ostane prazno, zadrži staro
                novi_closure = c_status if c_status else (stari_podaci[0] if stari_podaci else "")
                novi_zad = zad if zad else (stari_podaci[1] if stari_podaci else "")
                novi_vol = vol if vol else (stari_podaci[2] if stari_podaci else "")
                nova_nap = nap if nap else (stari_podaci[3] if stari_podaci else "")
                
                # 3. Update u bazi
                try:
                    c.execute("""UPDATE baza_igraca 
                                 SET closure=?, zadovoljan=?, voli=?, napomena=? 
                                 WHERE uid=?""", 
                              (novi_closure, novi_zad, novi_vol, nova_nap, uid_search))
                    conn.commit()
                    st.success("Sačuvano! Osveži stranicu.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Greška: {e}")
    else:
        st.warning("Nema podataka za ovaj UID.")
