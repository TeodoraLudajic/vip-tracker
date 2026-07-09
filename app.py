import streamlit as st
import pandas as pd
import sqlite3


# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="VIP BO",
    page_icon="👑",
    layout="wide"
)


DB = "vip_podaci.db"


# ==========================
# DATABASE
# ==========================

conn = sqlite3.connect(
    DB,
    check_same_thread=False
)

cur = conn.cursor()


def setup_db():

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


setup_db()



# ==========================
# STYLE
# ==========================

st.markdown("""
<style>

.main .block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}


.vip-card {

    background-color:#181818;

    padding:6px;

    border-radius:12px;

    border:1px solid #333;

    margin-bottom:10px;

}


.small-title {

    font-size:18px;

    font-weight:600;

    margin-bottom:8px;

}


.badge {

    display:inline-block;

    background:#303030;

    padding:4px 10px;

    border-radius:15px;

    margin:2px;

    font-size:13px;

}


div[data-testid="stDataFrame"] {

    height:auto;

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



st.sidebar.title("👑 VIP BO")


menu = st.sidebar.radio(
    "",
    [
        "🔍 Player",
        "📥 Upload Month",
        "🗂 Manage Uploads",
        "🎁 Promo",
        "📉 Missing Players"
    ]
)


st.title("🎰 VIP Back Office")
# ==========================
# UPLOAD MONTH
# ==========================

if menu == "📥 Upload Month":

    st.subheader("📥 Upload Monthly Report")


    month = st.text_input(
        "Mesec",
        placeholder="June 2026"
    )


    file = st.file_uploader(
        "CSV fajl",
        type="csv"
    )


    if file:

        df = pd.read_csv(file)


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

                    uid = str(
                        int(row["customer_id"])
                    )


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

if menu == "🗂 Manage Uploads":

    st.subheader("🗂 Uploaded Months")


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

if menu == "📉 Missing Players":

    st.subheader("📉 Players Missing From Current Month")


    months = pd.read_sql(
        """
        SELECT DISTINCT month
        FROM monthly
        """,
        conn
    )["month"].tolist()


    selected_month = st.selectbox(
        "Izaberi trenutni mesec",
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
            f"Broj igrača koji nisu u {selected_month}: {missing['uid'].nunique()}"
        )


        last_seen = (
            missing
            .sort_values("month")
            .groupby("uid")
            .tail(1)
        )


        st.dataframe(
            last_seen,
            hide_index=True,
            use_container_width=True
        )
        
# ==========================
# PLAYER PAGE
# ==========================

if menu == "🔍 Player":


    st.subheader(
        "🔍 Search Player"
    )


    uid = st.text_input(
        "UID",
        placeholder="Unesi UID"
    )


    if uid:


        player = get_player(uid)


        if player.empty:

            st.warning(
                "Igrač nije pronađen"
            )


        else:


            p = player.iloc[0]



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
                🎁 Promo History
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

if menu == "🎁 Promo":


    st.subheader(
        "🎁 Add Promo"
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
