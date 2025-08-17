import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import calendar
import os

# ==========================
# File paths
# ==========================
ASSETS_FILE = "assets.csv"
DEBTS_FILE = "debts.csv"

# ==========================
# Auto-create CSVs if missing
# ==========================
def ensure_csv(file_path, columns):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)

ensure_csv(ASSETS_FILE, ["Name", "Owner", "Type", "Institution", "Value", "Rate of Return"])
ensure_csv(DEBTS_FILE, ["Name","Owner","Type","#Number","Creditor","Org Start Amount",
                        "Start Date","Rate","Balance","Payment","Due Date","Extra","End Date"])

# ==========================
# Utility functions
# ==========================
@st.cache_data
def load_assets():
    return pd.read_csv(ASSETS_FILE)

def load_debts():
    df = pd.read_csv(DEBTS_FILE)
    df["Due Date"] = pd.to_datetime(df["Due Date"], errors='coerce')
    df["Payment"] = pd.to_numeric(df["Payment"], errors='coerce').fillna(0)
    return df

def save_debts(df):
    df.to_csv(DEBTS_FILE, index=False)

# ==========================
# Page Setup
# ==========================
st.set_page_config(page_title="💰 Wealth Management Dashboard", layout="wide")

# ==========================
# CSS for Modern UI
# ==========================
st.markdown("""
<style>
body, .main { background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.big-title { font-size: 38px !important; font-weight: 700; color: #1F3C88; }
.section-header { font-size: 24px !important; color: #34495E; margin-top: 20px; }
.metric-card { background: linear-gradient(135deg, #1F3C88, #3A8DFF); color: white; border-radius: 12px;
padding: 20px; margin: 10px 0; text-align: center; font-weight: 600; box-shadow: 0px 4px 15px rgba(0,0,0,0.2); }
.day-box { border:1px solid #ccc; border-radius:6px; padding:5px; margin:2px; min-height:60px; background-color:#ffffff;}
.day-header { font-weight:bold; font-size:14px; color:#34495E; margin-bottom:5px;}
.payment-item { font-size:12px; padding:2px; border-radius:4px; margin-bottom:2px; color:white;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">💼 Wealth Management Dashboard</p>', unsafe_allow_html=True)

# ==========================
# Sidebar Navigation
# ==========================
page = st.sidebar.radio("📑 Pages", ["Assets", "Debts", "Calendar"])

# ==========================
# Assets Page
# ==========================
if page == "Assets":
    st.markdown('<p class="section-header">📊 Asset Overview</p>', unsafe_allow_html=True)
    df_assets = load_assets()
    st.dataframe(df_assets, use_container_width=True)
    total_assets = df_assets["Value"].sum() if not df_assets.empty else 0
    avg_return = df_assets["Rate of Return"].mean() if not df_assets.empty else 0
    col1, col2 = st.columns(2)
    col1.markdown(f'<div class="metric-card">💰 Total Assets<br><h3>${total_assets:,.2f}</h3></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card">📈 Avg Rate of Return<br><h3>{avg_return:.2f}%</h3></div>', unsafe_allow_html=True)
    if not df_assets.empty:
        fig = px.pie(df_assets, names='Type', values='Value', color_discrete_sequence=px.colors.qualitative.Vivid)
        fig.update_layout(title_text="Asset Allocation by Type", title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

# ==========================
# Debts Page
# ==========================
elif page == "Debts":
    st.markdown('<p class="section-header">💳 Debt Management</p>', unsafe_allow_html=True)
    df = load_debts()

    # Editable DataFrame
    st.subheader("📋 Debt Table (Editable)")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # Save changes immediately
    if not edited_df.equals(df):
        save_debts(edited_df)
        st.success("Debt table updated and saved successfully!")
        df = edited_df  # refresh

    # Metrics
    total_debt = df["Balance"].sum() if not df.empty else 0
    avg_rate = pd.to_numeric(df["Rate"], errors="coerce").fillna(0).mean() if not df.empty else 0
    total_payment = df["Payment"].sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-card">💸 Total Debt<br><h3>${total_debt:,.2f}</h3></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card">📊 Avg Interest Rate<br><h3>{avg_rate:.2f}%</h3></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card">💵 Monthly Payments<br><h3>${total_payment:,.2f}</h3></div>', unsafe_allow_html=True)

    if not df.empty:
        fig = px.bar(df, x="Creditor", y="Balance", color="Rate", text="Balance", color_continuous_scale="Blues")
        fig.update_layout(title="Debt Balances by Creditor", title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

# ==========================
# Calendar Page
# ==========================
elif page == "Calendar":
    st.markdown('<p class="section-header">📅 Debt Payment Calendar</p>', unsafe_allow_html=True)
    df = load_debts()
    today = datetime.date.today()
    year = st.selectbox("Year", range(today.year, today.year + 5), index=0)
    month = st.selectbox("Month", range(1, 13), index=today.month-1)
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    st.markdown(f"### {calendar.month_name[month]} {year}")

    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day_name in enumerate(day_names):
        cols[i].markdown(f"**{day_name}**", unsafe_allow_html=True)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].markdown('<div class="day-box"></div>', unsafe_allow_html=True)
            else:
                day_date = datetime.date(year, month, day)
                payments_today = df[df["Due Date"] == pd.to_datetime(day_date)]
                items_html = ""
                for idx, row in payments_today.iterrows():
                    items_html += f'<div class="payment-item" style="background-color:#FF5733">{row.Name}: ${row.Payment:,.0f}</div>'
                with cols[i]:
                    st.markdown(f'<div class="day-box"><div class="day-header">{day}</div>{items_html}</div>', unsafe_allow_html=True)
