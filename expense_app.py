import streamlit as st
from datetime import date
import csv
import os
import pandas as pd

st.title("Katie's Expense Tracker")

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

# Build DataFrame if we have any expenses
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
    # Year selector
    years = sorted(df["Date"].dt.year.unique())
    selected_year = st.sidebar.selectbox("Year", years, index=len(years) - 1)

    # Month selector
    month_names = [
        "All months",
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    month_numbers = [None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    selected_month_name = st.sidebar.selectbox("Month", month_names, index=0)
    selected_month = month_numbers[month_names.index(selected_month_name)]

    # Apply filters
    filtered_df = df[df["Date"].dt.year == selected_year]
    if selected_month is not None:
        filtered_df = filtered_df[filtered_df["Date"].dt.month == selected_month]
else:
    st.sidebar.info("No data yet to filter.")

# -------------------------------
# Expense Input Form
# -------------------------------
st.header("➕ Add New Expense")

with st.form("expense_form"):
    description = st.text_input("Description", placeholder="e.g. Groceries, Uber, Rent")
    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"]
    )
    amount = st.number_input("Amount (£)", min_value=0.0, format="%.2f")
    exp_date = st.date_input("Date", value=date.today())

    submitted = st.form_submit_button("Add Expense")

# Save to session + CSV
if submitted:
    if description and amount > 0:
        new_expense = {
            "Description": description,
            "Category": category,
            "Amount": float(amount),
            "Date": exp_date.strftime("%Y-%m-%d")
        }

        # Add to current session
        st.session_state.expenses.append(new_expense)

        # Also append to CSV
        file_exists = os.path.exists(FILENAME)
        with open(FILENAME, mode="a", newline="") as f:
            fieldnames = ["Description", "Category", "Amount", "Date"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(new_expense)

        st.success("Expense added and saved permanently! 💾")
        st.rerun()  # reload so filters & tables update immediately
    else:
        st.error("Please enter a description and an amount greater than zero.")

# -------------------------------
# All Expenses (raw table)
# -------------------------------
st.header("📄 All Expenses")

if df is not None and not df.empty:
    st.dataframe(df.sort_values("Date"), width="stretch")
else:
    st.info("No expenses recorded yet.")

# -------------------------------
# Filtered View (based on sidebar)
# -------------------------------
st.header("📂 Filtered Expenses (by year/month)")

if filtered_df is not None and not filtered_df.empty:
    st.write(
        f"Showing expenses for **{selected_year}**"
        + ("" if selected_month is None else f", **{selected_month_name}**")
    )
    st.dataframe(filtered_df.sort_values("Date"), width="stretch")
else:
    st.info("No expenses match the selected filters yet.")

# -------------------------------
# Charts for filtered period
# -------------------------------
st.header("📊 Charts for Selected Period")

if filtered_df is not None and not filtered_df.empty:
    # Spending over time (by day)
    daily = (
        filtered_df.groupby("Date")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Date")
        .set_index("Date")
    )
    st.subheader("Spending over time (per day)")
    st.line_chart(daily)

    # Spending by category
    by_cat = (
        filtered_df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .set_index("Category")
    )
    st.subheader("Spending by category")
    st.bar_chart(by_cat)
else:
    st.info("Add some expenses and select a period to see charts.")

# -------------------------------
# Undo Last Expense
# -------------------------------
st.header("🪄 Undo Last Expense")

if st.button("Undo last added expense"):
    if st.session_state.expenses:
        removed = st.session_state.expenses.pop()

        # Rewrite the CSV from current session_state.expenses
        if st.session_state.expenses:
            with open(FILENAME, mode="w", newline="") as f:
                fieldnames = ["Description", "Category", "Amount", "Date"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for exp in st.session_state.expenses:
                    writer.writerow(exp)
        else:
            # No expenses left; remove file if it exists
            if os.path.exists(FILENAME):
                os.remove(FILENAME)

        st.success(
            f"Removed: {removed['Description']} on {removed['Date']} "
            f"for £{removed['Amount']:.2f}"
        )
        st.rerun()
    else:
        st.warning("No expenses to undo.")
