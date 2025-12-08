import streamlit as st
from datetime import date
import csv
import os
import pandas as pd

st.title("💸 Katie's Expense Tracker")

FILENAME = "expenses.csv"

# -------------------------------
# Load & Store Data (CSV + session)
# -------------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

    # Load from CSV if it exists
    if os.path.exists(FILENAME):
        with open(FILENAME, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["Amount"] = float(row["Amount"])  # convert string to float
                st.session_state.expenses.append(row)

# Convert to DataFrame if we have entries
df = None
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    df["Date"] = pd.to_datetime(df["Date"])

# -------------------------------
# Sidebar Filters (Year + Month)
# -------------------------------
st.sidebar.header("Filters")

filtered_df = None
if df is not None and not df.empty:
    years = sorted(df["Date"].dt.year.unique())
    selected_year = st.sidebar.selectbox("Year", years, index=len(years) - 1)

    month_names = [
        "All months",
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    month_numbers = [None, 1,2,3,4,5,6,7,8,9,10,11,12]

    selected_month_name = st.sidebar.selectbox("Month", month_names, index=0)
    selected_month = month_numbers[month_names.index(selected_month_name)]

    filtered_df = df[df["Date"].dt.year == selected_year]
    if selected_month is not None:
        filtered_df = filtered_df[filtered_df["Date"].dt.month == selected_month]
else:
    st.sidebar.info("No data yet to filter.")

# -------------------------------
# Add Expense Form
# -------------------------------
st.header("➕ Add New Expense")

with st.form("expense_form"):
    description = st.text_input("Description", placeholder="e.g. Groceries, Uber, Rent")

    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"]
    )

    # NEW — Card Used
    card = st.selectbox(
        "Card Used 💳",
        ["Visa", "Mastercard", "Amex", "Debit", "Cash", "Other"]
    )

    amount = st.number_input("Amount (£)", min_value=0.0, format="%.2f")
    exp_date = st.date_input("Date", value=date.today())

    submitted = st.form_submit_button("Add Expense")

# Save to CSV + memory
if submitted:
    if description and amount > 0:
        new_expense = {
            "Description": description,
            "Category": category,
            "Card": card,  # ← NEW FIELD
            "Amount": float(amount),
            "Date": exp_date.strftime("%Y-%m-%d")
        }

        st.session_state.expenses.append(new_expense)

        file_exists = os.path.exists(FILENAME)
        with open(FILENAME, mode="a", newline="") as f:
            fieldnames = ["Description", "Category", "Card", "Amount", "Date"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(new_expense)

        st.success("Saved with card used 💳")
        st.rerun()
    else:
        st.error("Enter description + amount > 0")

# -------------------------------
# Display All Expenses
# -------------------------------
st.header("📄 All Expenses")
if df is not None and not df.empty:
    st.dataframe(df.sort_values("Date"), width="stretch")
else:
    st.info("No expenses yet.")

# -------------------------------
# Filtered View
# -------------------------------
st.header("📂 Filtered (Year/Month)")
if filtered_df is not None and not filtered_df.empty:
    st.write(f"Filtering → **{selected_year}** / **{selected_month_name}**")
    st.dataframe(filtered_df.sort_values("Date"), width="stretch")
else:
    st.info("No matching expenses.")

# -------------------------------
# Charts
# -------------------------------
st.header("📊 Charts")
if filtered_df is not None and not filtered_df.empty:
    daily = filtered_df.groupby("Date")["Amount"].sum()
    st.subheader("Daily Spending")
    st.line_chart(daily)

    cat_totals = filtered_df.groupby("Category")["Amount"].sum()
    st.subheader("Spending by Category")
    st.bar_chart(cat_totals)
else:
    st.info("Add expenses to see charts.")

# -------------------------------
# Undo Last Expense
# -------------------------------
st.header("🪄 Undo Last Expense")

if st.button("Undo Last Expense"):
    if st.session_state.expenses:
        removed = st.session_state.expenses.pop()

        # Rewrite CSV
        if st.session_state.expenses:
            with open(FILENAME, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["Description","Category","Card","Amount","Date"])
                writer.writeheader()
                writer.writerows(st.session_state.expenses)
        else:
            if os.path.exists(FILENAME):
                os.remove(FILENAME)

        st.success(f"Removed ➝ {removed['Description']} (£{removed['Amount']}) on {removed['Card']}")
        st.rerun()
    else:
        st.warning("Nothing to undo.")
