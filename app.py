
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

DB_NAME = "expenses.db"

INCOME_CATEGORIES = [
    "Salary", "Business", "Investment", "Other"
]

EXPENSE_CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills",
    "Education", "Health", "Rent", "Entertainment", "Other"
]

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def get_connection():
    return sqlite3.connect(DB_NAME)
def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            transaction_date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()
def get_connection():
    return sqlite3.connect(DB_NAME)
def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            transaction_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()

def get_transactions():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC",
        conn
    )
    conn.close()
    return df

# -------------------------------
# ADD TRANSACTION
# -------------------------------
st.sidebar.title("💰 Expense Manager")
st.sidebar.subheader("Add Transaction")

transaction_type = st.sidebar.selectbox(
    "Transaction Type",
    ["Expense", "Income"]
)

categories = (
    INCOME_CATEGORIES
    if transaction_type == "Income"
    else EXPENSE_CATEGORIES
)

category = st.sidebar.selectbox("Category", categories)

amount = st.sidebar.number_input(
    "Amount (₹)",
    min_value=0.0,
    step=100.0
)

description = st.sidebar.text_input("Description")

transaction_date = st.sidebar.date_input(
    "Date",
    value=date.today()
)

if st.sidebar.button("Save Transaction", use_container_width=True):
    if amount > 0:
        conn = get_connection()
        conn.execute("""
            INSERT INTO transactions
            (transaction_type, category, amount, description, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            transaction_type,
            category,
            amount,
            description,
            str(transaction_date)
        ))
        conn.commit()
        conn.close()

        st.sidebar.success("Transaction saved successfully!")
        st.rerun()
    else:
        st.sidebar.error("Enter an amount greater than zero.")

# -------------------------------
# LOAD DATA
# -------------------------------
df = get_transactions()

st.title("💰 Personal Expense Tracker")
st.caption("Manage your income, expenses and financial performance.")

# -------------------------------
# MONTH FILTER
# -------------------------------
if not df.empty:
    df["month"] = df["transaction_date"].str[:7]
    months = sorted(df["month"].dropna().unique(), reverse=True)
else:
    months = []

selected_month = st.selectbox(
    "Select Reporting Month",
    ["All Months"] + list(months)
)

if selected_month == "All Months":
    report_df = df.copy()
else:
    report_df = df[df["month"] == selected_month].copy()

# -------------------------------
# FINANCIAL CALCULATIONS
# -------------------------------
if not report_df.empty:
    total_income = report_df.loc[
        report_df["transaction_type"] == "Income", "amount"
    ].sum()

    total_expenses = report_df.loc[
        report_df["transaction_type"] == "Expense", "amount"
    ].sum()
else:
    total_income = 0
    total_expenses = 0

balance = total_income - total_expenses

# -------------------------------
# DASHBOARD
# -------------------------------
st.subheader("📊 Financial Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Total Income", f"₹{total_income:,.2f}")
c2.metric("Total Expenses", f"₹{total_expenses:,.2f}")
c3.metric("Available Balance", f"₹{balance:,.2f}")

st.divider()

# -------------------------------
# EXPENSE CHART
# -------------------------------

# -------------------------------
# PROFESSIONAL ANALYTICS DASHBOARD
# -------------------------------

st.divider()
st.header("📊 Financial Analytics")

# 1. Expense Pie Chart
st.subheader("🥧 Category-wise Expense Distribution")

expense_df = report_df[
    report_df["transaction_type"] == "Expense"
].copy()

if not expense_df.empty:

    category_data = (
        expense_df.groupby("category", as_index=False)["amount"]
        .sum()
    )

    fig_pie = px.pie(
        category_data,
        names="category",
        values="amount",
        hole=0.45,
        title="Where Does Your Money Go?"
    )

    fig_pie.update_traces(
        textinfo="label+percent"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.info("No expense data available.")

# 2. Monthly Income vs Expenses
st.subheader("📅 Monthly Income vs Expenses")

if not df.empty:

    monthly_data = (
        df.groupby(["month", "transaction_type"])["amount"]
        .sum()
        .reset_index()
    )

    fig_monthly = px.bar(
        monthly_data,
        x="month",
        y="amount",
        color="transaction_type",
        barmode="group",
        title="Monthly Financial Comparison",
        labels={
            "month": "Month",
            "amount": "Amount (₹)",
            "transaction_type": "Type"
        }
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )

else:
    st.info("No monthly records available.")

# 3. Daily Expense Trend
st.subheader("📈 Daily Spending Trend")

if not expense_df.empty:

    daily_data = (
        expense_df.groupby("transaction_date")["amount"]
        .sum()
        .reset_index()
    )

    fig_daily = px.line(
        daily_data,
        x="transaction_date",
        y="amount",
        markers=True,
        title="Daily Expense Movement",
        labels={
            "transaction_date": "Date",
            "amount": "Expense (₹)"
        }
    )

    st.plotly_chart(
        fig_daily,
        use_container_width=True
    )

else:
    st.info("No daily expense records available.")

# -------------------------------
# TRANSACTION HISTORY
# -------------------------------


# ---------------------------------
# MONTHLY BUDGET & SAVINGS TRACKER
# ---------------------------------

st.divider()
st.header("💰 Monthly Budget & Savings")

monthly_budget = st.number_input(
    "Set Your Monthly Expense Budget (₹)",
    min_value=0.0,
    value=30000.0,
    step=1000.0
)

budget_df = report_df.copy()

budget_df["transaction_date"] = pd.to_datetime(
    budget_df["transaction_date"]
)

today = date.today()

current_month = budget_df[
    (budget_df["transaction_date"].dt.month == today.month) &
    (budget_df["transaction_date"].dt.year == today.year)
]

monthly_expenses = current_month[
    current_month["transaction_type"] == "Expense"
]["amount"].sum()

monthly_income = current_month[
    current_month["transaction_type"] == "Income"
]["amount"].sum()

remaining_budget = monthly_budget - monthly_expenses

savings = monthly_income - monthly_expenses

col1, col2, col3 = st.columns(3)

col1.metric("Monthly Budget", f"₹{monthly_budget:,.2f}")

col2.metric("Monthly Expenses", f"₹{monthly_expenses:,.2f}")

col3.metric(
    "Remaining Budget",
    f"₹{remaining_budget:,.2f}"
)

if monthly_budget > 0:
    st.progress(
        min(monthly_expenses / monthly_budget, 1.0)
    )

    if monthly_expenses > monthly_budget:
        st.error("⚠️ You have exceeded your monthly budget!")
    else:
        st.success("You are within your monthly budget.")

if monthly_income > 0:
    savings_rate = (savings / monthly_income) * 100
    st.metric("Monthly Savings", f"₹{savings:,.2f}")
    st.metric("Savings Rate", f"{savings_rate:.1f}%")
st.divider()
st.subheader("📋 Transaction History")

if not report_df.empty:

    display_df = report_df[
        ["id", "transaction_date", "transaction_type",
         "category", "amount", "description"]
    ].copy()

    display_df.columns = [
        "ID", "Date", "Type", "Category", "Amount (₹)", "Description"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No transactions found.")

# -------------------------------
# EDIT TRANSACTION
# -------------------------------
st.divider()
st.subheader("✏️ Edit Transaction")

if not df.empty:

    selected_id = st.selectbox(
        "Select Transaction ID to Edit",
        df["id"].tolist()
    )

    selected_record = df[df["id"] == selected_id].iloc[0]

    with st.form("edit_form"):

        edit_type = st.selectbox(
            "Transaction Type",
            ["Expense", "Income"],
            index=["Expense", "Income"].index(
                selected_record["transaction_type"]
            )
        )

        edit_categories = (
            INCOME_CATEGORIES
            if edit_type == "Income"
            else EXPENSE_CATEGORIES
        )

        old_category = selected_record["category"]

        category_options = list(edit_categories)

        if old_category not in category_options:
            category_options.append(old_category)

        edit_category = st.selectbox(
            "Category",
            category_options,
            index=category_options.index(old_category)
        )

        edit_amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            value=float(selected_record["amount"]),
            step=100.0
        )

        edit_description = st.text_input(
            "Description",
            value=str(selected_record["description"] or "")
        )

        edit_date = st.date_input(
            "Date",
            value=date.fromisoformat(
                selected_record["transaction_date"]
            )
        )

        update_button = st.form_submit_button(
            "Update Transaction"
        )

        if update_button:
            if edit_amount > 0:
                conn = get_connection()

                conn.execute("""
                    UPDATE transactions
                    SET transaction_type = ?,
                        category = ?,
                        amount = ?,
                        description = ?,
                        transaction_date = ?
                    WHERE id = ?
                """, (
                    edit_type,
                    edit_category,
                    edit_amount,
                    edit_description,
                    str(edit_date),
                    int(selected_id)
                ))

                conn.commit()
                conn.close()

                st.success("Transaction updated successfully!")
                st.rerun()
            else:
                st.error("Amount must be greater than zero.")

# -------------------------------
# DELETE TRANSACTION
# -------------------------------
st.divider()
st.subheader("🗑️ Delete Transaction")

if not df.empty:

    delete_id = st.selectbox(
        "Select Transaction ID to Delete",
        df["id"].tolist(),
        key="delete_id"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this transaction."
    )

    if st.button("Delete Selected Transaction"):
        if confirm_delete:
            conn = get_connection()

            conn.execute(
                "DELETE FROM transactions WHERE id = ?",
                (int(delete_id),)
            )

            conn.commit()
            conn.close()

            st.success("Transaction deleted successfully!")
            st.rerun()
        else:
            st.warning("Please confirm before deleting.")

# -------------------------------
# EXCEL EXPORT
# -------------------------------
st.divider()
st.subheader("📥 Download Financial Report")

if not report_df.empty:

    export_df = report_df[
        ["id", "transaction_date", "transaction_type",
         "category", "amount", "description"]
    ].copy()

    export_df.columns = [
        "ID", "Date", "Type", "Category", "Amount (INR)", "Description"
    ]

    import io

    excel_file = io.BytesIO()

    with pd.ExcelWriter(
        excel_file,
        engine="openpyxl"
    ) as writer:
        export_df.to_excel(
            writer,
            sheet_name="Transactions",
            index=False
        )

    st.download_button(
        label="Download Excel Report",
        data=excel_file.getvalue(),
        file_name="Expense_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("No records available to export.")

# -------------------------------
# FOOTER
# -------------------------------
st.divider()
st.caption("Personal Expense Tracker | Built with Python and Streamlit")
