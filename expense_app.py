import streamlit as st
from datetime import date
import csv
import os
import pandas as pd

st.title("💸 Katie's Expense Tracker")

EXPENSE_FILE = "expenses.csv"
OWED_FILE = "owed.csv"   # where we store “people owe me” items

# --------------------------------
# Load expenses from CSV into session
# --------------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

    if os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["Amount"] = float(row["Amount"])
                # Older files might not have Card column; handle that
                if "Card" not in row:
                    row["Card"] = "Unknown"
                st.session_state.expenses.append(row)

# Build DataFrame from expenses
df = None
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    df["Date"] = pd.to_datetime(df["Date"])

# --------------------------------
# Load “people owe me” items
# --------------------------------
if "owed" not in st.session_state:
    st.session_state.owed = []

    if os.path.exists(OWED_FILE):
        with open(OWED_FILE, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["Amount"] = float(row["Amount"])
                st.session_state.owed.append(row)

# Track last action in owed section so we can undo it
if "last_owed_action" not in st.session_state:
    st.session_state.last_owed_action = None

# --------------------------------
# Sidebar Filters (Year + Month + Card)
# --------------------------------
st.sidebar.header("Filters")

filtered_df = None
selected_year = None
selected_month_name = "All months"
selected_card_label = "All cards"

if df is not None and not df.empty:
    # ----- Year -----
    years = sorted(df["Date"].dt.year.unique())
    selected_year = st.sidebar.selectbox("Year", years, index=len(years) - 1)

    # ----- Month -----
    month_names = [
        "All months",
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    month_numbers = [None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    selected_month_name = st.sidebar.selectbox("Month", month_names, index=0)
    selected_month = month_numbers[month_names.index(selected_month_name)]

    # ----- Card filter -----
    cards = sorted(df["Card"].astype(str).unique())
    card_options = ["All cards"] + cards
    selected_card_label = st.sidebar.selectbox("Card", card_options, index=0)

    # Apply filters step by step
    filtered_df = df[df["Date"].dt.year == selected_year]

    if selected_month is not None:
        filtered_df = filtered_df[filtered_df["Date"].dt.month == selected_month]

    if selected_card_label != "All cards":
        filtered_df = filtered_df[filtered_df["Card"] == selected_card_label]
else:
    st.sidebar.info("No data yet to filter.")

# --------------------------------
# Add Expense Form
# --------------------------------
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

# --------------------------------
# Section: Money people owe me
# --------------------------------
st.header("🔫 Give me my money bro 🔫")

# Total owed display
total_owed = sum(item["Amount"] for item in st.session_state.owed) if st.session_state.owed else 0.0
st.write(f"**Total people owe you: £{total_owed:.2f}**")

# Form to add a new "owed" item
with st.form("owed_form"):
    who = st.text_input("Who owes you?", placeholder="e.g. Alice")
    owed_desc = st.text_input("What is it for?", placeholder="e.g. Dinner split")
    owed_card = st.selectbox(
        "Which card did you use to pay? 💳",
        ["Visa", "Mastercard", "Amex", "Debit", "Cash", "Other"],
        key="owed_card_select"
    )
    owed_amount = st.number_input("Amount they owe (£)", min_value=0.0, format="%.2f", key="owed_amount_input")
    owed_date = st.date_input("Date of expense", value=date.today(), key="owed_date_input")

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

        # remember this as last action for undo
        st.session_state.last_owed_action = {
            "kind": "add",
            "items": [new_owed],
        }

        st.success("Added to 'people owe me' list ✅")
        st.rerun()
    else:
        st.error("Please fill in who, what for, and an amount > 0.")

# Show pending owed items with checkboxes
if st.session_state.owed:
    st.subheader("Pending payments")

    to_remove_indices = []
    settlements = []  # store (owed_item, reimb) for undo

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
            # 1) Add this as a reimbursement into expenses
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

            # 2) Mark this owed entry to be removed
            to_remove_indices.append(i)
            settlements.append({"owed": item, "reimb": reimb})

    # Remove paid items and rewrite owed CSV
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

        # remember this as last action for undo (settling debts)
        st.session_state.last_owed_action = {
            "kind": "settle",
            "items": settlements,
        }

        st.success("Marked as paid ✅ and added reimbursement to your tracker.")
        st.rerun()
else:
    st.info("No one owes you money right now.")

# --------------------------------
# Undo last owed action (add or settle)
# --------------------------------
st.subheader("🪄 Undo last change in 'people owe me'")

if st.button("Undo last owed action"):
    action = st.session_state.get("last_owed_action")

    if not action:
        st.warning("There is no recent owed action to undo.")
    else:
        kind = action["kind"]
        items = action["items"]

        if kind == "add":
            # Remove the last added owed item
            target = items[0]
            # Remove one matching entry from owed list (from the end)
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

            # Rewrite owed CSV
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
            # For each settlement, re-add owed item and remove reimbursement
            for pair in items:
                owed_item = pair["owed"]
                reimb = pair["reimb"]

                # Re-add owed item
                st.session_state.owed.append(owed_item)

                # Remove matching reimbursement from expenses (search from end)
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

            # Rewrite owed CSV
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

            # Rewrite expenses CSV
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

# --------------------------------
# All Expenses Table
# --------------------------------
st.header("📄 All Expenses")
if df is not None and not df.empty:
    st.dataframe(df.sort_values("Date"), width="stretch")
else:
    st.info("No expenses recorded yet.")

# --------------------------------
# Filtered View
# --------------------------------
st.header("📂 Filtered (Year / Month / Card)")
if filtered_df is not None and not filtered_df.empty:
    st.write(
        f"Showing **{selected_year}** / **{selected_month_name}** / **{selected_card_label}**"
    )
    st.dataframe(filtered_df.sort_values("Date"), width="stretch")
else:
    st.info("No expenses match those filters yet.")

# --------------------------------
# Charts
# --------------------------------
st.header("📊 Charts")
if filtered_df is not None and not filtered_df.empty:
    # Daily spending
    daily = filtered_df.groupby("Date")["Amount"].sum()
    st.subheader("Daily total")
    st.line_chart(daily)

    # By category (this will include 'Reimbursement' as its own bar)
    cat_totals = filtered_df.groupby("Category")["Amount"].sum()
    st.subheader("By category")
    st.bar_chart(cat_totals)
else:
    st.info("Add expenses and pick a period to see charts.")

# --------------------------------
# Undo Last Expense
# --------------------------------
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
