import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="VIP BO",
    page_icon="🎰",
    layout="wide"
)

DB = "vip_podaci.db"


def connection():
    return sqlite3.connect(DB, check_same_thread=False)


conn = connection()
cur = conn.cursor()


# =========================
# DATABASE
# =========================

cur.execute("""
CREATE TABLE IF NOT EXISTS players (
    uid TEXT PRIMARY KEY,
    brand TEXT,
    closure TEXT DEFAULT '',
    reward TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    notes TEXT DEFAULT ''
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS monthly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT,
    month TEXT,
    deposit TEXT,
    segment TEXT,
    status TEXT,
    notes TEXT DEFAULT ''
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS promo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT,
    month TEXT,
    promo_type TEXT,
    amount TEXT,
    notes TEXT DEFAULT ''
)
""")


conn.commit()


# =========================
# STYLE
# =========================

st.markdown("""
<style>

body {
background-color:#0e1117;
}

.card {
background:#1b1f24;
padding:20px;
border-radius:15px;
border:1px solid #333;
margin-bottom:15px;
}

.badge {
display:inline-block;
background:#333;
padding:6px 12px;
border-radius:20px;
margin:3px;
}

</style>
""", unsafe_allow_html=True)



# =========================
# FUNCTIONS
# =========================

def get_player(uid):

    return pd.read_sql(
        "SELECT * FROM players WHERE uid=?",
        conn,
        params=(uid,)
    )


def save_player(uid, brand, closure, reward, tags, notes):

    cur.execute("""
    INSERT OR REPLACE INTO players
    (uid,brand,closure,reward,tags,notes)
    VALUES (?,?,?,?,?,?)
    """,
    (
        uid,
        brand,
        closure,
        reward,
        tags,
        notes
    ))

    conn.commit()



def add_month(uid, month, deposit, segment, status):

    cur.execute("""
    SELECT id FROM monthly
    WHERE uid=? AND month=?
    """,
    (uid, month))


    if cur.fetchone():

        cur.execute("""
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
        ))

    else:

        cur.execute("""
        INSERT INTO monthly
        (uid,month,deposit,segment,status)
        VALUES (?,?,?,?,?)
        """,
        (
            uid,
            month,
            deposit,
            segment,
            status
        ))

    conn.commit()



st.title("🎰 VIP Back Office")

menu = st.sidebar.radio(
    "Menu",
    [
        "🔍 Player",
        "📥 Upload Month",
        "🎁 Promo"
    ]
)
# =========================
# UPLOAD MONTHLY BII REPORT
# =========================

if menu == "📥 Upload Month":

    st.header("📥 Upload BII Monthly Report")


    month = st.text_input(
        "Mesec",
        placeholder="npr. June 2026"
    )


    file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )


    if file:

        df = pd.read_csv(file)

        st.write("Preview:")
        st.dataframe(
            df.head(),
            use_container_width=True
        )


        if st.button("Import Month"):


            required = [
                "customer_id",
                "brand",
                "NextMonthBin",
                "account_status",
                "vips"
            ]


            missing = [
                x for x in required
                if x not in df.columns
            ]


            if missing:

                st.error(
                    f"Nedostaju kolone: {missing}"
                )


            else:

                added = 0


                for _, row in df.iterrows():

                    uid = str(row["customer_id"])


                    cur.execute(
                        """
                        SELECT uid FROM players
                        WHERE uid=?
                        """,
                        (uid,)
                    )


                    exists = cur.fetchone()


                    if not exists:

                        cur.execute(
                            """
                            INSERT INTO players
                            (uid,brand)
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


                    added += 1


                conn.commit()


                st.success(
                    f"Ubačeno {added} igrača za {month}"
                )



# =========================
# PLAYER PROFILE
# =========================

if menu == "🔍 Player":


    st.header("🔍 Player Search")


    uid = st.text_input(
        "UID"
    )


    if uid:


        player = get_player(uid)


        if player.empty:

            st.warning(
                "Nema igrača sa tim UID"
            )


        else:

            p = player.iloc[0]


            st.markdown(
                f"""
                <div class="card">

                <h2>👤 {p['uid']}</h2>

                <b>Brand:</b> {p['brand']}<br><br>

                <b>Closure:</b> {p['closure'] or "-"}<br><br>

                <b>Reward:</b> {p['reward'] or "-"}<br><br>

                <b>Tags:</b><br>
                {p['tags'] or "-"}

                </div>
                """,
                unsafe_allow_html=True
            )


            st.subheader(
                "📝 Notes"
            )

            st.info(
                p["notes"]
                if p["notes"]
                else "-"
            )



            st.divider()


            st.subheader(
                "✏️ Edit Player"
            )


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


            reward = st.multiselect(
                "Reward Preference",
                [
                    "Cashback",
                    "Bonus",
                    "Free Spins"
                ],
                default=
                p["reward"].split(",")
                if p["reward"]
                else []
            )


            tags_list = [
                "Bonus Hunter",
                "Chargeback",
                "Closure Risk",
                "Cashback Lover",
                "Free Spins Lover",
                "High Depositor",
                "Reactivated"
            ]


            tags = st.multiselect(
                "Tags",
                tags_list,
                default=
                p["tags"].split(",")
                if p["tags"]
                else []
            )


            notes = st.text_area(
                "Notes",
                value=p["notes"]
            )



            if st.button(
                "💾 Save"
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
                    "Sačuvano"
                )

                st.rerun()



            st.divider()


            st.subheader(
                "📊 Monthly History"
            )


            history = pd.read_sql(
                """
                SELECT
                month,
                deposit,
                segment,
                status,
                notes
                FROM monthly
                WHERE uid=?
                ORDER BY id
                """,
                conn,
                params=(uid,)
            )


            if not history.empty:

                st.dataframe(
                    history,
                    hide_index=True,
                    use_container_width=True
                )

            else:

                st.info(
                    "Nema istorije"
                )
              # =========================
# MANUAL PROMO ADD
# =========================

if menu == "🎁 Promo":

    st.header("🎁 Add Promo Information")


    uid = st.text_input(
        "UID igrača"
    )


    if uid:


        player = get_player(uid)


        if player.empty:

            st.warning(
                "Ovaj UID ne postoji. Prvo uploaduj BII mesec."
            )


        else:


            st.success(
                f"Igrač pronađen: {player.iloc[0]['brand']}"
            )


            month = st.text_input(
                "Mesec",
                placeholder="npr. June 2026"
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


            amount = st.text_input(
                "Promo Amount"
            )


            notes = st.text_area(
                "Promo Notes"
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
                    "Promo dodat!"
                )


            st.divider()


            st.subheader(
                "🎁 Promo History"
            )


            promo = pd.read_sql(
                """
                SELECT
                month,
                promo_type,
                amount,
                notes
                FROM promo
                WHERE uid=?
                ORDER BY id
                """,
                conn,
                params=(uid,)
            )


            if not promo.empty:

                st.dataframe(
                    promo,
                    hide_index=True,
                    use_container_width=True
                )

            else:

                st.info(
                    "Nema promo zapisa."
                )
