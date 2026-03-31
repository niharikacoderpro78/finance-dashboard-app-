import streamlit as st
import sqlite3
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Finance Dashboard", layout="wide")

# ---------------- CUSTOM UI ----------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: #FFFFFF;
}

div[data-testid="stMetric"] {
    background-color: #1E222A;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}

.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
}

.stDownloadButton>button {
    background-color: #2196F3;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("finance.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    name TEXT,
    amount REAL,
    category TEXT,
    date TEXT
)
""")

# ---------------- SIDEBAR ----------------
st.sidebar.title("🔍 Filters")

filter_category = st.sidebar.selectbox(
    "Category",
    ["All", "Food", "Travel", "Shopping", "Bills", "Other"]
)

filter_date = st.sidebar.date_input("Filter by Date", value=None)

st.sidebar.markdown("---")

# Clear all button (FIXED)
if st.sidebar.checkbox("⚠️ Confirm delete all data"):
    if st.sidebar.button("🗑️ Clear All Expenses"):
        c.execute("DELETE FROM expenses")
        conn.commit()
        st.sidebar.success("All data cleared!")
        st.rerun()   # ✅ FIXED HERE

# ---------------- TITLE ----------------
st.markdown("""
# 💰 Finance Dashboard  
### Track • Analyze • Improve your spending
""")

# ---------------- HERO SECTION ----------------
st.markdown("""
<div style="background: linear-gradient(90deg, #1f4037, #99f2c8);
padding: 20px;
border-radius: 12px;
margin-bottom: 20px;
text-align: center;">
    <h2 style="color:black;">📊 Welcome to your Finance Dashboard</h2>
    <p style="color:black;">Track your expenses, analyze trends, and improve your financial habits 💰</p>
</div>
""", unsafe_allow_html=True)

# ---------------- INPUT ----------------
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    
    name = col1.text_input("Expense")
    amount = col2.number_input("Amount")
    category = col3.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Bills", "Other"]
    )
    date = col4.date_input("Date")

    if st.button("➕ Add Expense"):
        c.execute(
            "INSERT INTO expenses VALUES (?, ?, ?, ?)",
            (name, amount, category, str(date))
        )
        conn.commit()
        st.success("Expense Added!")

st.markdown("---")

# ---------------- QUERY ----------------
query = "SELECT rowid, * FROM expenses WHERE 1=1"

if filter_category != "All":
    query += f" AND category='{filter_category}'"

if filter_date:
    query += f" AND date='{str(filter_date)}'"

rows = list(c.execute(query))

df = pd.DataFrame(rows, columns=["ID", "Name", "Amount", "Category", "Date"])

# ---------------- DASHBOARD ----------------
st.subheader("📊 Overview")

total = df["Amount"].sum() if not df.empty else 0
count = len(df)

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Spent", f"₹ {total}")
col2.metric("📦 Entries", count)
col3.metric("📊 Avg Expense", f"₹ {round(total/count,2) if count else 0}")

st.markdown("---")

# ---------------- CHARTS ----------------
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    monthly = df.groupby("Month")["Amount"].sum()
    category_chart = df.groupby("Category")["Amount"].sum()

    st.subheader("📈 Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Monthly Trend")
        st.line_chart(monthly)

    with col2:
        st.write("### Category Breakdown")
        st.bar_chart(category_chart)

st.markdown("---")

# ---------------- TABLE ----------------
st.subheader("📋 Expense List")

for i, row in df.iterrows():
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
        
        col1.write(f"**{row['Name']}**")
        col2.write(f"₹ {row['Amount']}")
        col3.write(row["Category"])
        col4.write(row["Date"])
        
        if col5.button("❌", key=row["ID"]):
            c.execute("DELETE FROM expenses WHERE rowid=?", (row["ID"],))
            conn.commit()
            st.rerun()   # ✅ FIXED HERE
        
        st.markdown("---")

# ---------------- EXPORT ----------------
st.subheader("📁 Export Data")

if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name="expenses.csv",
        mime="text/csv"
    )