import streamlit as st
import pandas as pd
import sqlite3

# Povezivanje na bazu
conn = sqlite3.connect('vip_podaci.db', check_same_thread=False, timeout=10)
c = conn.cursor()

# Kreiranje tabele sa svim potrebnim kolonama
c.execute('''CREATE TABLE IF NOT EXISTS baza_igraca 
             (uid TEXT, mesec TEXT, iznos REAL, brand TEXT, segment TEXT, 
              promo_status TEXT, promo_iznos REAL, closure TEXT, zadovoljan TEXT, voli TEXT, napomena TEXT)''')
conn.commit()

st.title("VIP Asistent - Tvoj BO")

# --- SEKCIJA ZA UPLOAD ---
uploaded_file = st.file_uploader("Ubaci CSV izveštaj", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    mesec_input = st.text_input("Mesec/godina (npr. Jul 2026):")
    is_promo = st.checkbox("Da li je ovo PROMO period?")
    
    if st.button("Učitaj i ažuriraj bazu") and mesec_input:
        for _, row in df.iterrows():
            p_iznos = row['bins'] if is_promo else 0.0
            p_status = "DA" if is_promo else "NE"
            
            c.execute("""INSERT INTO baza_igraca 
                         (uid, mesec, iznos, brand, segment, promo_status, promo_iznos) 
                         VALUES (?,?,?,?,?,?,?)""", 
                      (str(row['customer_id']), mesec_input, row['bins'], row['brand'], row['vips'], p_status, p_iznos))
        conn.commit()
        st.success("Podaci uspešno dodati!")

st.divider()

# --- SEKCIJA ZA PRETRAGU I EDITOVANJE ---
uid_search = st.text_input("Ukucaj UID igrača za pretragu:")

if uid_search:
    # Čitamo podatke sa rowid (potreban za editovanje)
    df_search = pd.read_sql(f"SELECT rowid, * FROM baza_igraca WHERE uid='{uid_search}'", conn)
    
    if not df_search.empty:
        st.write(f"### Istorija za UID: {uid_search}")
        
        # Interaktivna tabela
        edited_df = st.data_editor(
            df_search, 
            column_config={"rowid": None}, # Sakrivamo sistemski ID
            num_rows="fixed"
        )
        
        if st.button("Sačuvaj izmene iz tabele"):
            for index, row in edited_df.iterrows():
                try:
                    c.execute("""UPDATE baza_igraca 
                                 SET closure=?, zadovoljan=?, voli=?, napomena=?, promo_status=?, promo_iznos=? 
                                 WHERE rowid=?""", 
                              (row['closure'], row['zadovoljan'], row['voli'], row['napomena'], 
                               row['promo_status'], row['promo_iznos'], row['rowid']))
                    conn.commit()
                except Exception as e:
                    st.error(f"Greška kod reda {row['rowid']}: {e}")
            
            st.success("Sve izmene su sačuvane!")
            st.rerun()
    else:
        st.warning("Nema podataka za taj UID.")
