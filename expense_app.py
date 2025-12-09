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

# ---------- PINK PIXEL CSS ----------
def inject_custom_css():
    st.markdown(
        """
        <style>
        /* === APP BACKGROUND: soft pink pixel grid === */
        .stApp {
            background:
              linear-gradient(90deg, rgba(255,255,255,0.35) 1px, transparent 1px),
              linear-gradient(180deg, rgba(255,255,255,0.35) 1px, #ffe6f2 1px),
              radial-gradient(circle at 0 0, #ffc1e3 0, #ffe6f7 40%, #ffd9ec 80%);
            background-size: 16px 16px, 16px 16px, cover;
            color: #4a2456;
            font-family: "Press Start 2P", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }

        html, body, [class*="css"] {
            font-family: "Press Start 2P", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* === TOP TITLE STYLES === */
        .top-title {
            font-size: 1.4rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #ff6ea9; /* medium pink */
            text-shadow: 3px 3px 0 #ff94c2, 5px 5px 0 #2c2a87; /* light pink + dark outline */
            margin-bottom: 0.5rem;
        }
        .top-subtitle {
            font-size: 0.7rem;
            color: #ff7eb8;
            text-shadow: 2px 2px 0 #ffffff;
            margin-bottom: 1.5rem;
        }

        /* === PINK PIXEL CARDS === */
        .pixel-card {
            border: 3px solid #2c2a87;     /* dark blue outline */
            border-radius: 0;
            padding: 1rem;
            margin-bottom: 1.5rem;
            background: #ffe6f7;           /* pale pink */
            box-shadow: 4px 4px 0 #ff94c2; /* pink shadow */
        }

        .pixel-card h1, .pixel-card h2, .pixel-card h3 {
            color: #ff4f9a;
            text-shadow: 2px 2px 0 #ffffff;
        }

        /* === WIDGETS (buttons, inputs, selects) === */
        .stButton>button,
        .stCheckbox,
        .stTextInput>div>div>input,
        .stNumberInput input,
        div[data-baseweb="select"] > div {
            border-radius: 0 !important;
            border: 2px solid #2c2a87 !important;
            background: #ffd9ec !important;
            color: #4a2456 !important;
            box-shadow: 3px 3px 0 #ff94c2 !important;
        }

        .stButton>button:hover {
            background: #ff6ea9 !important;
            color: #ffffff !important;
            box-shadow: 4px 4px 0 #2c2a87 !important;
        }

        /* Inputs text caret color */
        input {
            caret-color: #ff4f9a !important;
        }

        /* TABLES / DATAFRAMES */
        .stDataFrame, .stTable {
            border-radius: 0 !important;
            border: 2px solid #2c2a87 !important;
            box-shadow: 3px 3px 0 #ff94c2 !important;
        }

        /* Sidebar background soften */
        [data-testid="stSidebar"] {
            background-color: #ffe6f7 !important;
            border-right: 3px solid #2c2a87;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

inject_custom_css()

# ---------- TITLE ----------
st.markdown(
    "<div class='top-title'>💸 Katie's Expense Tracker</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='top-subtitle'>Cute pink pixels. Track spending & IOUs with love. ♡</div>",
    unsafe_allow_html=True,
)

# If you save your pixel image as 'katie_pixel.png' in this folder,
# you can uncomment this line to show it:
# st.image("katie_pixel.png", width=140)

# ---------- FILE NAMES ----------
EXPENSE_FILE = "expenses.csv"
OWED_FILE = "owed.csv"   # where we store “people owe me” items

# ---------- LOAD EXPENSES ----------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

    if os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["Amount"] = float(row["Amount"])
                if "Card" not in row:
                    row["Card"] = "Unknown"
                st.session_state.expenses.append(row)

df = None
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    df["Date"] = pd.to_datetime(df["Date"])

# ---------- LOAD OWED ITEMS ----------
if "owed" not in st.session_state:
    st.session_state.owed = []

    if os.path.exists(OWED_FILE):
        with open(OWED_FILE, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["Amount"] = float(row["Amount"])
                st.session_state.owed.append(row)

# Track last action in owed section for undo
if "last_owed_action" not in st.session_state:
    st.session_state.last_owed_action = None

# ---------- SIDEBAR FILTERS (YEAR / MONTH / CARD) ----------
st.sidebar.header("Filters")

filtered_df = None
selected_year = None
selected_month_name = "All months"
selected_card_label = "All cards"

if df is not None and not df.empty:
    years = sorted(df["Date"].dt.year.unique())
    selected_year = st.sidebar.selectbox("Year", years, index=len(years) - 1)

    month_names = [
        "All months",
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    month_numbers = [None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    selected_month_name = st.sidebar.selectbox("Month", month_names, index=0)
    selected_month = month_numbers[month_names.index(selected_month_name)]

    cards = sorted(df["Card"].astype(str).unique())
    card_options = ["All cards"] + cards
    selected_card_label = st.sidebar.selectbox("Card", card_options, index=0)

    filtered_df = df[df["Date"].dt.year == selected_year]

    if selected_month is not None:
        filtered_df = filtered_df[filtered_df["Date"].dt.month == selected_month]

    if selected_card_label != "All cards":
        filtered_df = filtered_df[filtered_df["Card"] == selected_card_label]
else:
    st.sidebar.info("No data yet to filter.")

# ---------- ADD EXPENSE ----------
st.markdown("<div class='pixel-card'>", unsafe_allow_html=True)
st.header("➕ Add New Expense")

with st.form("expense_form"):
    description = st.text_input("Description", placeholder="e.g. Groceries, Uber, Rent")

    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"]
    )

    card = st.selectbox(
        "Card Used 💳",
        ["Visa", "Mastercard", "Amex", "Debit", "Cash", "Other"]
    )

    amount = st.number_input("Amount (£)", min_value=0.0, format="%.2f")
    exp_date = st.date_input("Date", value=date.today())

    submitted = st.form_submit_button("Add Expense")

if submitted:
    if description and amount > 0:
        new_expense = {
            "Description": description,
            "Category": category,
            "Card": card,
            "Amount": float(amount),
            "Date": exp_date.strftime("%Y-%m-%d")
        }

        st.session_state.expenses.append(new_expense)

        file_exists = os.path.exists(EXPENSE_FILE)
        with open(EXPENSE_FILE, mode="a", newline="") as f:
            fieldnames = ["Description", "Category", "Card", "Amount", "Date"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_expense)

        st.success("Expense added and saved permanently! 💾")
        st.rerun()
    else:
        st.error("Enter a description and an amount greater than zero.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- MONEY PEOPLE OWE ME ----------
st.markdown("<div class='pixel-card'>", unsafe_allow_html=True)
st.header("🔫 Give me my money bro 🔫")

total_owed = sum(item["Amount"] for item in st.session_state.owed) if st.session_state.owed else 0.0
st.write(f"**Total people owe you: £{total_owed:.2f}**")

with st.form("owed_form"):
    who = st.text_input("Who owes you?", placeholder="e.g. Alice")
    owed_desc = st.text_input("What is it for?", placeholder="e.g. Dinner split")
    owed_card = st.selectbox(
        "Which card did you use to pay? 💳",
        ["Visa", "Mastercard", "Amex", "Debit", "Cash", "Other"],
        key="owed_card_select"
    )
    owed_amount = st.number_input(
        "Amount they owe (£)",
        min_value=0.0,
        format="%.2f",
        key="owed_amount_input"
    )
    owed_date = st.date_input(
        "Date of expense",
        value=date.today(),
        key="owed_date_input"
    )

    owed_submitted = st.form_submit_button("Add to owed list")

if owed_submitted:
    if who and owed_desc and owed_amount > 0:
        new_owed = {
            "Who": who,
            "Description": owed_desc,
            "Card": owed_card,
            "Amount": float(owed_amount),
            "Date": owed_date.strftime("%Y-%m-%d")
        }
        st.session_state.owed.append(new_owed)

        file_exists = os.path.exists(OWED_FILE)
        with open(OWED_FILE, mode="a", newline="") as f:
            fieldnames = ["Who", "Description", "Card", "Amount", "Date"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_owed)

        st.session_state.last_owed_action = {
            "kind": "add",
            "items": [new_owed],
        }

        st.success("Added to 'people owe me' list ✅")
        st.rerun()
    else:
        st.error("Please fill in who, what for, and an amount > 0.")

if st.session_state.owed:
    st.subheader("Pending payments")

    to_remove_indices = []
    settlements = []

    for i, item in enumerate(st.session_state.owed):
        cols = st.columns([1, 5])
        with cols[0]:
            paid = st.checkbox("", key=f"paid_{i}")
        with cols[1]:
            st.write(
                f"**{item['Who']}** owes **£{item['Amount']:.2f}** "
                f"for **{item['Description']}** "
                f"(date: {item['Date']}, card: {item['Card']})"
            )

        if paid:
            reimb_desc = f"Reimbursement from {item['Who']} - {item['Description']}"
            reimb = {
                "Description": reimb_desc,
                "Category": "Reimbursement",
                "Card": item["Card"],
                "Amount": float(item["Amount"]),
                "Date": date.today().strftime("%Y-%m-%d"),
            }

            st.session_state.expenses.append(reimb)

            file_exists = os.path.exists(EXPENSE_FILE)
            with open(EXPENSE_FILE, mode="a", newline="") as f:
                fieldnames = ["Description", "Category", "Card", "Amount", "Date"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(reimb)

            to_remove_indices.append(i)
            settlements.append({"owed": item, "reimb": reimb})

    if to_remove_indices:
        for idx in sorted(to_remove_indices, reverse=True):
            st.session_state.owed.pop(idx)

        if st.session_state.owed:
            with open(OWED_FILE, mode="w", newline="") as f:
                fieldnames = ["Who", "Description", "Card", "Amount", "Date"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in st.session_state.owed:
                    writer.writerow(row)
        else:
            if os.path.exists(OWED_FILE):
                os.remove(OWED_FILE)

        st.session_state.last_owed_action = {
            "kind": "settle",
            "items": settlements,
        }

        st.success("Marked as paid ✅ and added reimbursement to your tracker.")
        st.rerun()
else:
    st.info("No one owes you money right now.")

st.subheader("🪄 Undo last change in 'people owe me'")

if st.button("Undo last owed action"):
    action = st.session_state.get("last_owed_action")

    if not action:
        st.warning("There is no recent owed action to undo.")
    else:
        kind = action["kind"]
        items = action["items"]

        if kind == "add":
            target = items[0]
            for idx in range(len(st.session_state.owed) - 1, -1, -1):
                o = st.session_state.owed[idx]
                if (
                    o["Who"] == target["Who"]
                    and o["Description"] == target["Description"]
                    and o["Card"] == target["Card"]
                    and float(o["Amount"]) == float(target["Amount"])
                    and o["Date"] == target["Date"]
                ):
                    st.session_state.owed.pop(idx)
                    break

            if st.session_state.owed:
                with open(OWED_FILE, "w", newline="") as f:
                    fieldnames = ["Who", "Description", "Card", "Amount", "Date"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in st.session_state.owed:
                        writer.writerow(row)
            else:
                if os.path.exists(OWED_FILE):
                    os.remove(OWED_FILE)

            st.success("Undid last 'add to owed list' action.")
            st.session_state.last_owed_action = None
            st.rerun()

        elif kind == "settle":
            for pair in items:
                owed_item = pair["owed"]
                reimb = pair["reimb"]

                st.session_state.owed.append(owed_item)

                for idx in range(len(st.session_state.expenses) - 1, -1, -1):
                    e = st.session_state.expenses[idx]
                    if (
                        e["Description"] == reimb["Description"]
                        and e["Category"] == reimb["Category"]
                        and e["Card"] == reimb["Card"]
                        and float(e["Amount"]) == float(reimb["Amount"])
                        and e["Date"] == reimb["Date"]
                    ):
                        st.session_state.expenses.pop(idx)
                        break

            if st.session_state.owed:
                with open(OWED_FILE, "w", newline="") as f:
                    fieldnames = ["Who", "Description", "Card", "Amount", "Date"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in st.session_state.owed:
                        writer.writerow(row)
            else:
                if os.path.exists(OWED_FILE):
                    os.remove(OWED_FILE)

            if st.session_state.expenses:
                with open(EXPENSE_FILE, "w", newline="") as f:
                    fieldnames = ["Description", "Category", "Card", "Amount", "Date"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in st.session_state.expenses:
                        writer.writerow(row)
            else:
                if os.path.exists(EXPENSE_FILE):
                    os.remove(EXPENSE_FILE)

            st.success("Undid last 'paid' action and restored owed + expenses.")
            st.session_state.last_owed_action = None
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------- EXPENSE TABLES & CHARTS ----------
st.markdown("<div class='pixel-card'>", unsafe_allow_html=True)

st.header("📄 All Expenses")
if df is not None and not df.empty:
    st.dataframe(df.sort_values("Date"), width="stretch")
else:
    st.info("No expenses recorded yet.")

st.header("📂 Filtered (Year / Month / Card)")
if filtered_df is not None and not filtered_df.empty:
    st.write(
        f"Showing **{selected_year}** / **{selected_month_name}** / **{selected_card_label}**"
    )
    st.dataframe(filtered_df.sort_values("Date"), width="stretch")
else:
    st.info("No expenses match those filters yet.")

st.header("📊 Charts")
if filtered_df is not None and not filtered_df.empty:
    daily = filtered_df.groupby("Date")["Amount"].sum()
    st.subheader("Daily total")
    st.line_chart(daily)

    cat_totals = filtered_df.groupby("Category")["Amount"].sum()
    st.subheader("By category")
    st.bar_chart(cat_totals)
else:
    st.info("Add expenses and pick a period to see charts.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- UNDO LAST EXPENSE ----------
st.markdown("<div class='pixel-card'>", unsafe_allow_html=True)
st.header("🪄 Undo Last Expense")

if st.button("Undo Last Expense"):
    if st.session_state.expenses:
        removed = st.session_state.expenses.pop()

        if st.session_state.expenses:
            with open(EXPENSE_FILE, "w", newline="") as f:
                fieldnames = ["Description", "Category", "Card", "Amount", "Date"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in st.session_state.expenses:
                    writer.writerow(row)
        else:
            if os.path.exists(EXPENSE_FILE):
                os.remove(EXPENSE_FILE)

        st.success(
            f"Removed ➝ {removed['Description']} (£{removed['Amount']:.2f})"
        )
        st.rerun()
    else:
        st.warning("Nothing to undo.")

st.markdown("</div>", unsafe_allow_html=True)
