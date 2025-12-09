import streamlit as st
from datetime import date
import csv
import os
import pandas as pd

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Katie's Expense Tracker",
    page_icon="💸",
    layout="wide",
)

# ========= 🌸 PINK MOBILE-FRIENDLY PIXEL CSS =========
def inject_custom_css():
    st.markdown(
        """
        <style>

        /* GLOBAL + BACKGROUND */
        .stApp {
            background:
              linear-gradient(90deg, rgba(255,255,255,0.14) 1px, transparent 1px),
              linear-gradient(180deg, rgba(255,255,255,0.14) 1px, #ffe6f2 1px),
              radial-gradient(circle at top left, #ffc1e3 0, #ffe6f7 40%, #ffd9ec 80%);
            background-size: 16px 16px, 16px 16px, cover;
            font-family: "Press Start 2P", sans-serif;
        }

        html, body { -webkit-text-size-adjust: 100%; }

        /* 🔥 FORCE ALL TEXT DARK BY DEFAULT */
        * {
            color: #3a1a45 !important;
        }

        /* TITLE (override the global rule above) */
        .top-title{
            font-size: clamp(18px,4.5vw,30px);
            text-transform: uppercase;
            font-weight: 700;
            color: #ff4f9a !important;
            text-shadow:
                3px 3px 0 #ff94c2,
                4px 4px 0 #2c2a87;
        }
        .top-subtitle{
            font-size: clamp(11px,3vw,17px);
            color: #6b3c7a !important;
            text-shadow: none;
            margin-bottom: 20px;
        }

        /* PIXEL CARDS */
        .pixel-card{
            border: 3px solid #2c2a87;
            background: #ffeaf8;
            box-shadow: 4px 4px 0 #ff94c2;
            border-radius: 0;
            padding: clamp(12px,3vw,26px);
            margin-bottom: 22px;
        }
        .pixel-card h2, .pixel-card h3{
            color: #ff4f9a !important;
            font-size: clamp(15px,4vw,24px);
        }

        /* INPUTS + BUTTONS */
        .stButton>button,
        input, textarea,
        div[data-baseweb="select"]>div {
            border-radius: 0 !important;
            border: 2px solid #2c2a87 !important;
            background: #ffd9ec !important;
            color: #3a1a45 !important;
            font-size: clamp(13px,3.3vw,19px) !important;
            height: clamp(42px,7vw,65px) !important;
            box-shadow: 3px 3px 0 #ff94c2 !important;
        }
        .stButton>button:hover{
            background: #ff6ea9 !important;
            color: #ffffff !important;
            box-shadow: 4px 4px 0 #2c2a87 !important;
        }

        .stNumberInput input{
            height: clamp(42px,6.5vw,65px) !important;
        }

        ::placeholder{
            color: #6b3c7a !important;
        }

        /* CHECKBOXES */
        .stCheckbox input{ width: 22px; height: 22px; }
        .stCheckbox label{ font-size: clamp(12px,3vw,18px) !important; }

        /* TABLES */
        .stDataFrame, .stTable{
            border-radius: 0 !important;
            border: 2px solid #2c2a87 !important;
            font-size: clamp(11px,3vw,16px);
            box-shadow: 3px 3px 0 #ff94c2 !important;
        }

        /* SIDEBAR */
        [data-testid="stSidebar"]{
            background: #ffeaf8 !important;
            border-right: 3px solid #2c2a87;
            font-size: clamp(12px,3vw,16px);
        }

        </style>
        """,
        unsafe_allow_html=True
    )
# =======================================================
inject_custom_css()


# ---------- TITLE ----------
st.markdown("<div class='top-title'>💸 Katie's Expense Tracker</div>",unsafe_allow_html=True)
st.markdown("<div class='top-subtitle'>♡ I love you ♡</div>",unsafe_allow_html=True)





# ---------- FILES ----------
EXPENSE_FILE="expenses.csv"
OWED_FILE="owed.csv"


# ========== LOAD EXPENSES ==========
if "expenses" not in st.session_state:
    st.session_state.expenses=[]

    if os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE,"r") as f:
            for row in csv.DictReader(f):
                row["Amount"]=float(row["Amount"])
                if "Card" not in row: row["Card"]="Unknown"
                st.session_state.expenses.append(row)

df=None
if st.session_state.expenses:
    df=pd.DataFrame(st.session_state.expenses)
    df["Date"]=pd.to_datetime(df["Date"])


# ========== LOAD OWED ==========
if "owed" not in st.session_state:
    st.session_state.owed=[]
    if os.path.exists(OWED_FILE):
        with open(OWED_FILE,"r") as f:
            for r in csv.DictReader(f):
                r["Amount"]=float(r["Amount"])
                st.session_state.owed.append(r)

if "last_owed_action" not in st.session_state:
    st.session_state.last_owed_action=None



# ========== SIDEBAR FILTERS ==========
st.sidebar.header("Filters")

filtered_df=None
if df is not None and not df.empty:
    years=sorted(df["Date"].dt.year.unique())
    year=st.sidebar.selectbox("Year",years,index=len(years)-1)

    months=["All","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_num=[None,1,2,3,4,5,6,7,8,9,10,11,12]
    month_choice=st.sidebar.selectbox("Month",months)
    month_selected=month_num[months.index(month_choice)]

    cards=["All"]+sorted(df["Card"].astype(str).unique())
    card_choice=st.sidebar.selectbox("Card",cards)

    filtered_df=df[df["Date"].dt.year==year]
    if month_selected: filtered_df=filtered_df[filtered_df["Date"].dt.month==month_selected]
    if card_choice!="All": filtered_df=filtered_df[filtered_df["Card"]==card_choice]


# ========== ADD EXPENSE ==========
st.markdown("<div class='pixel-card'>",unsafe_allow_html=True)
st.header("➕ Add New Expense")

with st.form("add_exp"):
    desc=st.text_input("Description",placeholder="eg. Groceries, Uber, Rent")
    cat=st.selectbox("Category",["Food","Transport","Entertainment","Bills","Shopping","Other"])
    card=st.selectbox("Card Used 💳",["Visa","Mastercard","Amex","Debit","Cash","Other"])
    amt=st.number_input("Amount (£)",min_value=0.0,format="%.2f")
    d=st.date_input("Date",value=date.today())
    go=st.form_submit_button("Add Expense")

if go and desc and amt>0:
    row={"Description":desc,"Category":cat,"Card":card,"Amount":float(amt),"Date":d.strftime("%Y-%m-%d")}
    st.session_state.expenses.append(row)

    newfile=not os.path.exists(EXPENSE_FILE)
    with open(EXPENSE_FILE,"a",newline="") as f:
        w=csv.DictWriter(f,fieldnames=row.keys())
        if newfile: w.writeheader()
        w.writerow(row)

    st.success("Added! 💗")
    st.rerun()

st.markdown("</div>",unsafe_allow_html=True)


# ========== OWED SECTION ==========
st.markdown("<div class='pixel-card'>",unsafe_allow_html=True)
st.header("🔫 Give me my money bro 🔫")

owed_total=sum(o["Amount"] for o in st.session_state.owed)
st.write(f"**People owe you: £{owed_total:.2f}**")

with st.form("owed_add"):
    who=st.text_input("Who owes you?",placeholder="eg. Alice")
    why=st.text_input("What for?",placeholder="eg. Dinner Split")
    card_o=st.selectbox("Card paid with",["Visa","Mastercard","Amex","Debit","Cash","Other"])
    amt_o=st.number_input("Amount (£)",min_value=0.0,format="%.2f")
    date_o=st.date_input("Date",value=date.today())
    add_o=st.form_submit_button("Add to list")

if add_o and who and why and amt_o>0:
    entry={"Who":who,"Description":why,"Card":card_o,"Amount":float(amt_o),"Date":date_o.strftime("%Y-%m-%d")}
    st.session_state.owed.append(entry)

    newfile=not os.path.exists(OWED_FILE)
    with open(OWED_FILE,"a",newline="") as f:
        w=csv.DictWriter(f,fieldnames=entry.keys())
        if newfile: w.writeheader()
        w.writerow(entry)

    st.session_state.last_owed_action={"kind":"add","items":[entry]}
    st.success("Added to owed 💗")
    st.rerun()


# ========== MANAGE OWED LIST ==========
if st.session_state.owed:
    st.subheader("Pending Repayments")
    remove=[]
    undo_pairs=[]

    for i,item in enumerate(st.session_state.owed):
        c=st.columns([1,6])
        paid=c[0].checkbox("",key=f"owed_{i}")
        c[1].write(f"**{item['Who']} owes £{item['Amount']:.2f}** for *{item['Description']}* ({item['Card']})")

        if paid:
            reimb={
                "Description":f"Reimbursement from {item['Who']} - {item['Description']}",
                "Category":"Reimbursement",
                "Card":item["Card"],
                "Amount":float(item["Amount"]),
                "Date":date.today().strftime("%Y-%m-%d"),
            }
            st.session_state.expenses.append(reimb)

            with open(EXPENSE_FILE,"a",newline="") as f:
                w=csv.DictWriter(f,fieldnames=reimb.keys())
                if not os.path.exists(EXPENSE_FILE): w.writeheader()
                w.writerow(reimb)

            remove.append(i)
            undo_pairs.append({"owed":item,"reimb":reimb})

    if remove:
        for idx in sorted(remove,reverse=True): st.session_state.owed.pop(idx)

        if st.session_state.owed:
            with open(OWED_FILE,"w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=["Who","Description","Card","Amount","Date"])
                w.writeheader()
                for r in st.session_state.owed: w.writerow(r)
        else:
            if os.path.exists(OWED_FILE): os.remove(OWED_FILE)

        st.session_state.last_owed_action={"kind":"settle","items":undo_pairs}
        st.success("Repayment recorded 🌸")
        st.rerun()

else:
    st.info("Nobody owes you right now 💞")

# ----- UNDO OWED -----
st.subheader("🪄 Undo Owed Action")

if st.button("Undo last owed"):
    a=st.session_state.last_owed_action
    if not a: st.warning("nothing to undo!")
    else:
        if a["kind"]=="add":
            target=a["items"][0]
            st.session_state.owed=[o for o in st.session_state.owed if not(
                o["Who"]==target["Who"] and o["Description"]==target["Description"])]
            st.success("Undo added owed ✓")

        elif a["kind"]=="settle":
            for pair in a["items"]:
                st.session_state.owed.append(pair["owed"])
                st.session_state.expenses=[e for e in st.session_state.expenses if not(
                    e["Description"]==pair["reimb"]["Description"])]
            st.success("Undo repayment ✓")

        with open(OWED_FILE,"w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=["Who","Description","Card","Amount","Date"])
            w.writeheader()
            for r in st.session_state.owed: w.writerow(r)

        with open(EXPENSE_FILE,"w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=["Description","Category","Card","Amount","Date"])
            w.writeheader()
            for r in st.session_state.expenses: w.writerow(r)

        st.session_state.last_owed_action=None
        st.rerun()

st.markdown("</div>",unsafe_allow_html=True)



# ========= EXPENSE TABLE + CHARTS =========
st.markdown("<div class='pixel-card'>",unsafe_allow_html=True)

st.header("📂 All Expenses")
if df is not None and not df.empty:
    st.dataframe(df.sort_values("Date"))
else: st.info("Add something 🥺")

st.header("📊 Filtered View")
if filtered_df is not None and not filtered_df.empty:
    st.write("Filtered results below ↓")
    st.dataframe(filtered_df.sort_values("Date"))
else:
    st.info("No items for those filters 💗")

st.header("📈 Charts")
if filtered_df is not None and not filtered_df.empty:
    daily=filtered_df.groupby("Date")["Amount"].sum()
    st.subheader("Daily Totals") ; st.line_chart(daily)

    cat=filtered_df.groupby("Category")["Amount"].sum()
    st.subheader("By Category") ; st.bar_chart(cat)
else:
    st.info("Add expenses first 🌸")

st.markdown("</div>",unsafe_allow_html=True)


# ========= UNDO EXPENSE =========
st.markdown("<div class='pixel-card'>",unsafe_allow_html=True)
st.header("🪄 Undo Last Expense")

if st.button("Undo Expense"):
    if st.session_state.expenses:
        popped=st.session_state.expenses.pop()

        if st.session_state.expenses:
            with open(EXPENSE_FILE,"w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=["Description","Category","Card","Amount","Date"])
                w.writeheader()
                for r in st.session_state.expenses: w.writerow(r)
        else:
            if os.path.exists(EXPENSE_FILE): os.remove(EXPENSE_FILE)

        st.success(f"Removed {popped['Description']} 🌸")
        st.rerun()
    else: st.warning("nothing to undo")

st.markdown("</div>",unsafe_allow_html=True)
