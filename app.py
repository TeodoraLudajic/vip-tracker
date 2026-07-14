import streamlit as st
import pandas as pd
import sqlite3
import streamlit.components.v1 as components
import os

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="VIP BO",
    page_icon="👑",
    layout="wide"
)

# ==========================
# DATABASE
# ==========================

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vip_podaci.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

def setup_db():
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS players (uid TEXT PRIMARY KEY, brand TEXT, closure TEXT DEFAULT '', reward TEXT DEFAULT '', tags TEXT DEFAULT '', notes TEXT DEFAULT '')")
        cur.execute("CREATE TABLE IF NOT EXISTS monthly (id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT, month TEXT, deposit TEXT, segment TEXT, status TEXT, notes TEXT DEFAULT '')")
        cur.execute("CREATE TABLE IF NOT EXISTS promo (id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT, month TEXT, promo_type TEXT, amount TEXT, notes TEXT DEFAULT '')")
        conn.commit()
    except Exception as e:
        st.error(f"Problem sa bazom: {e}")

setup_db()

# ==========================
# STYLE
# ==========================
st.markdown("""
<style>
/* 1. Mermerna pozadina */
.stApp {
    background-color: #050505 !important;
    background-image: radial-gradient(circle at 70% 30%, #1a1a1a 0%, #050505 100%) !important;
}

/* 2. Glavni kontejner - "VIP Kartica" izgled */
.main .block-container {
    background: rgba(15, 15, 15, 0.7) !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(197, 160, 89, 0.3) !important;
    border-radius: 20px !important;
    padding: 3rem !important;
}

/* 3. Zlatni Glow naslovi */
h1, h2, h3 {
    color: #D4AF37 !important;
    text-shadow: 0 0 10px rgba(212, 175, 55, 0.6) !important;
    text-transform: uppercase;
    letter-spacing: 3px !important;
}

/* 4. Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(10, 10, 10, 0.95) !important;
    border-right: 1px solid #C5A059 !important;
}

/* 5. Inputi - luksuzna ivica */
.stTextInput > div > div > input {
    background: #0a0a0a !important;
    border: 1px solid #C5A059 !important;
    color: #fff !important;
    border-radius: 8px !important;
}

/* 6. Dugmad */
div.stButton > button {
    background: linear-gradient(135deg, #C5A059, #8B6508) !important;
    color: #000 !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 6px !important;
    transition: 0.3s !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# FUNCTIONS
# ==========================


def get_player(uid):

    return pd.read_sql(
        """
        SELECT *
        FROM players
        WHERE uid=?
        """,
        conn,
        params=(uid,)
    )



def save_player(
        uid,
        brand,
        closure,
        reward,
        tags,
        notes
):

    cur.execute(
        """
        INSERT OR REPLACE INTO players
        (
        uid,
        brand,
        closure,
        reward,
        tags,
        notes
        )
        VALUES (?,?,?,?,?,?)
        """,
        (
            uid,
            brand,
            closure,
            reward,
            tags,
            notes
        )
    )

    conn.commit()



def add_month(
        uid,
        month,
        deposit,
        segment,
        status
):

    cur.execute(
        """
        SELECT id
        FROM monthly
        WHERE uid=? AND month=?
        """,
        (
            uid,
            month
        )
    )


    if cur.fetchone():

        cur.execute(
            """
            UPDATE monthly
            SET deposit=?,
                segment=?,
                status=?
            WHERE uid=? AND month=?
            """,
            (
                deposit,
                segment,
                status,
                uid,
                month
            )
        )


    else:

        cur.execute(
            """
            INSERT INTO monthly
            (
            uid,
            month,
            deposit,
            segment,
            status
            )
            VALUES (?,?,?,?,?)
            """,
            (
                uid,
                month,
                deposit,
                segment,
                status
            )
        )


    conn.commit()



def get_monthly(uid):

    return pd.read_sql(
        """
        SELECT
        ID,
        month AS Month,
        deposit AS Deposit,
        segment AS Segment,
        status AS Status
        FROM monthly
        WHERE uid=?
        ORDER BY id
        """,
        conn,
        params=(uid,)
    )
    


def get_promo(uid):

    return pd.read_sql(
        """
        SELECT
        month AS Month,
        promo_type AS Promo,
        amount AS Amount,
        notes AS Notes
        FROM promo
        WHERE uid=?
        ORDER BY id
        """,
        conn,
        params=(uid,)
    )


st.sidebar.markdown("""
<h2 style="
color:#D4AF37;
text-align:center;
">
👑 VIP BO
</h2>

<p style="
color:#888;
text-align:center;
font-size:12px;
">
VIP Management System
</p>
""", unsafe_allow_html=True)


menu = st.sidebar.radio(
    "Navigacija",
    [
        "👤 Player",
        "➜] Add Month",
        "☰ Manage Uploads",
        "─୨ৎ─ Promo",
        "💢 Missing Players"
    ],
    label_visibility="collapsed"
)

uid = ""
player = pd.DataFrame()

st.title("VIP")
# ==========================
# UPLOAD MONTH
# ==========================

if menu == "➜] Add Month":

    st.subheader("📥 Upload Monthly Report")

    col1, _ = st.columns([1, 2]) 
    with col1: 
        month = st.text_input("Mesec", placeholder="June 2026")
        file = st.file_uploader("CSV fajl", type="csv")

    if file:

        df = pd.read_csv(file)

        df["customer_id"] = df["customer_id"].astype(float).astype(int).astype(str)

        with st.expander("Preview fajla"):

            st.dataframe(
                df.head(10),
                use_container_width=True,
                height=250
            )


        if st.button(
            "⬆️ Import Month"
        ):

            cur.execute(
                """
                DELETE FROM monthly
                WHERE month=?
                """,
                (
                    month,
                )
            )

            conn.commit()
            
            needed = [
                "customer_id",
                "brand",
                "NextMonthBin",
                "account_status",
                "vips"
            ]


            missing = [
                x for x in needed
                if x not in df.columns
            ]


            if missing:

                st.error(
                    f"Nedostaju kolone: {missing}"
                )


            else:

                count = 0


                for _, row in df.iterrows():

                    uid = str(int(float(row["customer_id"])))

                    cur.execute(
                        """
                        SELECT uid
                        FROM players
                        WHERE uid=?
                        """,
                        (uid,)
                    )


                    exists = cur.fetchone()


                    if not exists:

                        cur.execute(
                            """
                            INSERT INTO players
                            (
                            uid,
                            brand
                            )
                            VALUES (?,?)
                            """,
                            (
                                uid,
                                row["brand"]
                            )
                        )


                    add_month(
                        uid,
                        month,
                        str(row["NextMonthBin"]),
                        str(row["vips"]),
                        str(row["account_status"])
                    )


                    count += 1


                conn.commit()


                st.success(
                    f"Uspešno dodato: {count} igrača"
                )


# ==========================
# MANAGE UPLOADS
# ==========================

if menu == "☰ Manage Uploads":

    st.subheader("☰ Uploaded Months")


    uploads = pd.read_sql(
        """
        SELECT
        month AS Month,
        COUNT(*) AS Players
        FROM monthly
        GROUP BY month
        ORDER BY month
        """,
        conn
    )

    if uploads.empty:
        st.info("No monthly reports have been uploaded yet.")
        st.stop()

    st.dataframe(
        uploads,
        hide_index=True,
        use_container_width=True
    )


    delete_month = st.selectbox(
        "Delete month",
        uploads["Month"].tolist()
    )


    if st.button("🗑 Delete Selected Month"):

        cur.execute(
            """
            DELETE FROM monthly
            WHERE month=?
            """,
            (delete_month,)
        )

        conn.commit()

        st.success(
            "Mesec obrisan"
        )

        st.rerun()

# ==========================
# MISSING PLAYERS
# ==========================

if menu == "💢 Missing Players":

    st.subheader("💢 Players Missing From Current Month")

    months = pd.read_sql(
        """
        SELECT DISTINCT month
        FROM monthly
        """,
        conn
    )["month"].tolist()

    
    if not months:
        st.info("No monthly reports have been uploaded yet.")
        st.stop()

    
    selected_month = st.selectbox(
        "Mesec",
        months
    )


    current_players = pd.read_sql(
        """
        SELECT uid
        FROM monthly
        WHERE month=?
        """,
        conn,
        params=(selected_month,)
    )


    all_previous = pd.read_sql(
        """
        SELECT
            m.uid,
            p.brand AS Brand,
            m.month,
            m.segment,
            m.status
        FROM monthly m
        LEFT JOIN players p
            ON m.uid = p.uid
        WHERE m.month != ?
        """,
        conn,
        params=(selected_month,)
     )


    missing = all_previous[
        ~all_previous["uid"].isin(
            current_players["uid"]
        )
    ]


    if missing.empty:

        st.success(
            "Nema igrača koji fale 🎉"
        )

    else:

        st.write(
            f"Fale u {selected_month}: {missing['uid'].nunique()}"
        )


        last_seen = (
            missing
            .sort_values("month")
            .groupby("uid")
            .tail(1)
        )


        brands = ["All"] + sorted(
            last_seen["Brand"].dropna().unique().tolist()
        )


        selected_brand = st.selectbox(
            "Brand",
            brands
        )


        if selected_brand != "All":

            last_seen = last_seen[
                last_seen["Brand"] == selected_brand
            ]

        last_seen = last_seen.head(50)

        df_to_show = last_seen.reset_index()

        prikaz = last_seen.reset_index()
        
        st.dataframe(
            prikaz,
            column_config={
                "uid": st.column_config.TextColumn("UID", copy_value=True)
            },
            use_container_width=True,
            hide_index=True
        )
        
# ==========================
# PLAYER PAGE
# ==========================

if menu == "👤 Player":
    st.subheader("🔍︎ Search Player")
    
    col1, col2 = st.columns([2, 1]) 
    with col1:
        uid = st.text_input("UID", placeholder="Unesi UID")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True) 
        search_btn = st.button("🔍 Search")

    if uid or search_btn:
        player = get_player(uid)
        if player.empty:
            st.warning("Igrač nije pronađen")
        else:
            p = player.iloc[0]
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("UID", p['uid'])
            with c2: st.metric("Brand", p['brand'])
            with c3: st.metric("Reward", p['reward'] if p['reward'] else "-")
            
            st.subheader("✏️ Edit Player")
            edit_c1, edit_c2 = st.columns(2)
            
            with edit_c1:
                closure = st.selectbox("Closure", ["", "Yes", "No"], index=["","Yes","No"].index(p['closure']) if p['closure'] in ["","Yes","No"] else 0)
            with edit_c2:
                reward = st.multiselect("Reward Preference", ["Cashback", "Bonus", "Free Spins"], default=p['reward'].split(",") if p['reward'] else [])
            
            tags = st.multiselect("Tags", ["Bonus Hunter", "Chargeback", "Closure Risk", "High Depositor"], default=p['tags'].split(",") if p['tags'] else [])
            notes = st.text_area("Notes", value=p['notes'] if p['notes'] else "")

            if st.button("💾 Save Changes"):
                save_player(uid, p['brand'], closure, ",".join(reward), ",".join(tags), notes)
                st.success("Sačuvano!")
                st.rerun()

            # -------------------
            # PLAYER CARD
            # -------------------

            st.markdown(
                """
                <div class="small-title">
                👤 Player Info
                </div>
                """,
                unsafe_allow_html=True
            )


            c1, c2, c3 = st.columns(
                [1,1,2]
            )


            with c1:

                st.markdown(
                    f"""
                    <div class="vip-card">

                    <b>UID</b><br>
                    {p['uid']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with c2:

                st.markdown(
                    f"""
                    <div class="vip-card">

                    <b>Brand</b><br>
                    {p['brand']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with c3:

                reward = (
                    p["reward"]
                    if p["reward"]
                    else "-"
                )

                tags = (
                    p["tags"]
                    if p["tags"]
                    else "-"
                )


                st.markdown(
                    f"""
                    <div class="vip-card">

                   <b>Reward:</b> {reward}<br>
                   <b>Tags:</b> {tags}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # -------------------
            # MONTHLY HISTORY FIRST
            # -------------------

            st.markdown(
                """
                <div class="small-title">
                📊 Monthly History
                </div>
                """,
                unsafe_allow_html=True
            )


            history = get_monthly(uid)

            if not history.empty:

                edited_history = st.data_editor(
                    history.drop(columns=["Status"]),
                    hide_index=True,
                    use_container_width=True,
                    height=200,
                    disabled=["id", "Month", "Segment"],
                    column_config={
                        "id": None
                    }
                )

                if st.button("💾 Save"):

                    for _, row in edited_history.iterrows():

                        cur.execute(
                            """
                            UPDATE monthly
                            SET deposit=?
                            WHERE id=?
                            """,
                            (
                                row["Deposit"],
                                row["id"]
                            )
                        )

                    conn.commit()

                    st.success("Monthly history updated.")

                    st.rerun()

           
            else:

                st.caption(
                    "Nema mesečne istorije"
                )



                    # -------------------
            # PROMO HISTORY + EDIT
            # -------------------

            st.markdown(
                """
                <div class="small-title">
                ➕ Promo History
                </div>
                """,
                unsafe_allow_html=True
            )


            promo = pd.read_sql(
                """
                SELECT
                id,
                month AS Month,
                promo_type AS Promo,
                amount AS Amount,
                notes AS Notes
                FROM promo
                WHERE uid=?
                ORDER BY id
                """,
                conn,
                params=(uid,)
            )


            if not promo.empty:


                st.dataframe(
                    promo.drop(columns=["id"]),
                    hide_index=True,
                    use_container_width=True,
                    height=180
                )


                st.markdown(
                    "#### ✏️ Edit Promo"
                )


                selected_promo = st.selectbox(
                    "Izaberi promo za izmenu",
                    promo["id"].tolist(),
                    format_func=lambda x:
                    f"{promo[promo['id']==x]['Month'].values[0]} - {promo[promo['id']==x]['Promo'].values[0]}"
                )


                selected = promo[
                    promo["id"] == selected_promo
                ].iloc[0]


                edit_col1, edit_col2 = st.columns(2)


                with edit_col1:

                    edit_month = st.text_input(
                        "Mesec",
                        value=selected["Month"]
                    )


                    edit_amount = st.text_input(
                        "Amount",
                        value=str(selected["Amount"])
                    )


                with edit_col2:

                    edit_promo = st.multiselect(
                        "Promo Type",
                        [
                            "Cashback",
                            "Bonus",
                            "Free Spins",
                            "Tournament"
                        ],
                        default=[
                            x for x in str(selected["Promo"]).split(",")
                            if x
                        ]
                    )


                    edit_notes = st.text_area(
                        "Promo Notes",
                        value=selected["Notes"],
                        height=80
                    )


                save_col, delete_col = st.columns(2)


                with save_col:

                    if st.button(
                        "💾 Save Promo Changes"
                    ):

                        cur.execute(
                            """
                            UPDATE promo
                            SET
                            month=?,
                            promo_type=?,
                            amount=?,
                            notes=?
                            WHERE id=?
                            """,
                            (
                                edit_month,
                                ",".join(edit_promo),
                                edit_amount,
                                edit_notes,
                                selected_promo
                            )
                        )

                        conn.commit()

                        st.success(
                            "Promo izmenjen"
                        )

                        st.rerun()



                with delete_col:

                    if st.button(
                        "🗑 Delete Promo"
                    ):

                        cur.execute(
                            """
                            DELETE FROM promo
                            WHERE id=?
                            """,
                            (
                                selected_promo,
                            )
                        )

                        conn.commit()

                        st.success(
                            "Promo obrisan"
                        )

                        st.rerun()


            else:

                st.caption(
                    "Nema promo zapisa"
                )


            # -------------------
            # END PROMO HISTORY
            # -------------------
# ==========================
# EDIT PLAYER
# ==========================

if menu == "🔍 Player":

    if uid and not player.empty:


        p = player.iloc[0]


        st.markdown(
            """
            <div class="small-title">
            ✏️ Edit Player
            </div>
            """,
            unsafe_allow_html=True
        )


        col1, col2 = st.columns(2)


        with col1:

            closure = st.selectbox(
                "Closure",
                [
                    "",
                    "Yes",
                    "No"
                ],
                index=
                [
                    "",
                    "Yes",
                    "No"
                ].index(p["closure"])
                if p["closure"] in ["","Yes","No"]
                else 0
            )


        with col2:

            reward = st.multiselect(
                "Reward Preference",
                [
                    "Cashback",
                    "Bonus",
                    "Free Spins",
                    "All"
                ],
                default=
                p["reward"].split(",")
                if p["reward"]
                else []
            )



        tags = st.multiselect(
            "Tags",
            [
                "Bonus Hunter",
                "Chargeback",
                "Closure Risk",
                "Cashback Lover",
                "Free Spins Lover",
                "High Depositor",
                "Reactivated"
            ],
            default=
            p["tags"].split(",")
            if p["tags"]
            else []
        )


        notes = st.text_area(
            "Notes",
            value=p["notes"],
            height=100
        )


        if st.button(
            "💾 Save Changes"
        ):


            save_player(
                uid,
                p["brand"],
                closure,
                ",".join(reward),
                ",".join(tags),
                notes
            )


            st.success(
                "Sačuvano!"
            )

            st.rerun()




# ==========================
# PROMO ADD
# ==========================

if menu == "─୨ৎ─ Promo":


    st.subheader(
        "➕ Add Promo"
    )


    uid = st.text_input(
        "UID"
    )


    if uid:


        player = get_player(uid)


        if player.empty:

            st.warning(
                "UID ne postoji"
            )


        else:


            st.success(
                f"{player.iloc[0]['brand']}"
            )


            c1, c2 = st.columns(2)


            with c1:

                month = st.text_input(
                    "Mesec",
                    placeholder="June 2026"
                )


            with c2:

                amount = st.text_input(
                    "Amount"
                )


            promo_type = st.multiselect(
                "Promo Type",
                [
                    "Cashback",
                    "Bonus",
                    "Free Spins",
                    "Tournament"
                ]
            )


            notes = st.text_area(
                "Promo Notes",
                height=80
            )



            if st.button(
                "➕ Add Promo"
            ):


                cur.execute(
                    """
                    INSERT INTO promo
                    (
                    uid,
                    month,
                    promo_type,
                    amount,
                    notes
                    )
                    VALUES (?,?,?,?,?)
                    """,
                    (
                        uid,
                        month,
                        ",".join(promo_type),
                        amount,
                        notes
                    )
                )


                conn.commit()


                st.success(
                    "Promo dodat"
                )


                st.rerun()
