st.divider()

# Pretraga (radiće uvek, čim ukucaš UID)
uid_search = st.text_input("Ukucaj UID igrača:")

if uid_search:
    # Uvek vadi podatke čim postoji UID
    istorija = pd.read_sql(f"SELECT * FROM baza_igraca WHERE uid='{uid_search}'", conn)
    
    if not istorija.empty:
        st.write("### Istorija igrača:")
        st.dataframe(istorija)
        
        # Forma za beleške
        with st.form("update_beleški"):
            c_status = st.text_input("Status closure?")
            zad = st.text_input("Zadovoljan?")
            vol = st.text_input("Voli (Bonus/FS)?")
            nap = st.text_area("Napomena")
            if st.form_submit_button("Sačuvaj beleške"):
                c.execute("UPDATE baza_igraca SET closure=?, zadovoljan=?, voli=?, napomena=? WHERE uid=?", 
                          (c_status, zad, vol, nap, uid_search))
                conn.commit()
                st.success("Beleške sačuvane! (Osveži stranicu da vidiš promene)")
    else:
        st.warning("Nema podataka za ovaj UID u bazi.")
