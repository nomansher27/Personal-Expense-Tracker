import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

DATA_FILE = "expenses.csv"


def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)

    return pd.DataFrame(
        columns=[
            "Date",
            "Category",
            "Amount",
            "Note"
        ]
    )


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


df = load_data()

st.title("💰 Personal Expense Tracker")
st.write(
    "Track your daily expenses, analyze spending, "
    "and understand where your money goes."
)

st.divider()

st.subheader("➕ Add New Expense")

with st.form("expense_form"):

    col1, col2 = st.columns(2)

    with col1:
        expense_date = st.date_input(
            "Date",
            value=date.today()
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Transport",
                "Shopping",
                "Bills",
                "Education",
                "Entertainment",
                "Health",
                "Other"
            ]
        )

    with col2:
        amount = st.number_input(
            "Amount (Rs.)",
            min_value=0.0,
            step=100.0
        )

        note = st.text_input(
            "Note",
            placeholder="e.g. Dinner, fuel, books..."
        )

    submitted = st.form_submit_button(
        "Add Expense"
    )


if submitted:

    if amount <= 0:
        st.warning(
            "Please enter an amount greater than 0."
        )

    else:

        new_expense = pd.DataFrame(
            [
                {
                    "Date": expense_date,
                    "Category": category,
                    "Amount": amount,
                    "Note": note
                }
            ]
        )

        df = pd.concat(
            [df, new_expense],
            ignore_index=True
        )

        save_data(df)

        st.success(
            "Expense added successfully!"
        )

        st.rerun()


if df.empty:

    st.info(
        "No expenses added yet. "
        "Add your first expense using the form above."
    )

else:

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Amount"]
    )

    st.divider()

    st.subheader("📊 Expense Overview")

    total_expense = df["Amount"].sum()
    average_expense = df["Amount"].mean()
    transaction_count = len(df)

    category_totals = (
        df.groupby("Category")["Amount"]
        .sum()
    )

    top_category = category_totals.idxmax()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Spending",
        f"Rs. {total_expense:,.0f}"
    )

    col2.metric(
        "Average Expense",
        f"Rs. {average_expense:,.0f}"
    )

    col3.metric(
        "Transactions",
        transaction_count
    )

    col4.metric(
        "Top Category",
        top_category
    )

    st.divider()

    st.subheader("🔎 Filter Expenses")

    all_categories = sorted(
        df["Category"].unique()
    )

    selected_categories = st.multiselect(
        "Select Categories",
        options=all_categories,
        default=all_categories
    )

    filtered_df = df[
        df["Category"].isin(
            selected_categories
        )
    ]

    category_summary = (
        filtered_df
        .groupby("Category")["Amount"]
        .sum()
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_bar = px.bar(
            category_summary,
            x="Category",
            y="Amount",
            title="Spending by Category"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    with col2:

        fig_pie = px.pie(
            category_summary,
            names="Category",
            values="Amount",
            title="Expense Distribution"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    st.subheader("📋 Expense History")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Expenses as CSV",
        csv,
        "expenses.csv",
        "text/csv"
    )