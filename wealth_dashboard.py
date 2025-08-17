import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import calendar

# ==========================
# File paths
# ==========================
ASSETS_FILE = "assets.csv"
DEBTS_FILE = "debts.csv"

# ==========================
# Utility functions
# ==========================
@st.cache_data
def load_assets():
    try:
        return pd.read_csv(ASSETS_FILE)
    except:
        return pd.DataFrame(columns=["Name", "Owner", "Type", "Institution", "Value", "Rate of Return"])

def load_debts():
    try:
        df = pd.read_csv(DEBTS_FILE)
        df["Due Date"] = pd.to_datetime(df["Due Date"], errors='coerce')
        df["Payment"] = pd.to_numeric(df["Payment"], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Name","Owner","Type","#Number","Creditor","Org Start Amount",
                                     "Start Date","Rate","Balance","Payment","Due Date","Extra","End Date"])

def save_assets(df):
    df.to_csv(ASSETS_FILE, index=False)

def save_debts(df):
    df.to_csv(DEBTS_FILE, index=False)

# ==========================
# Page Setup
# ==========================
st.set_page_config(page_title="💰 Wealth Management Dashboard", layout="wide")

# ==========================
# CSS for Modern UI + Trendy Look
# ==========================
st.markdown("""
<style>
body, .main { 
    background: linear-gradient(135deg, #e0f7fa, #ffe0b2); 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
}
.big-title { 
    font-size: 40px !important; 
    font-weight: 700; 
    color: #1D3557; 
    text-align:center; 
    margin-bottom:20px; 
    text-shadow: 1px 1px 5px rgba(0,0,0,0.1);
}
.section-header { 
    font-size: 26px !important; 
    color: #264653; 
    margin-top: 25px; 
    margin-bottom:15px; 
}
.metric-card { 
    background: linear-gradient(145deg, #ffb347, #ffcc33); 
    color: #1D3557; 
    border-radius: 15px;
    padding: 20px; 
    margin: 10px 0; 
    text-align: center; 
    font-weight: 600; 
    box-shadow: 0px 10px 25px rgba(0,0,0,0.15); 
    transition: transform 0.3s, box-shadow 0.3s;
}
.metric-card:hover { 
    transform: scale(1.05); 
    box-shadow: 0px 15px 35px rgba(0,0,0,0.25);
}
.day-box { 
    border:1px solid #ddd; 
    border-radius:10px; 
    padding:8px; 
    margin:2px; 
    min-height:70px; 
    background-color:#ffffff; 
    position:relative;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}
.day-header { 
    font-weight:bold; 
    font-size:14px; 
    color:#1D3557; 
    margin-bottom:5px; 
}
.payment-item { 
    font-size:12px; 
    padding:4px; 
    border-radius:6px; 
    margin-bottom:3px; 
    color:white; 
    cursor:pointer;
    transition: all 0.2s;
}
.payment-item:hover { 
    opacity:0.8; 
    transform: scale(1.05); 
}
.nav-bar { 
    display:flex; 
    justify-content:center; 
    margin-bottom:25px; 
}
.nav-item { 
    margin:0 15px; 
    padding:12px 25px; 
    border-radius:12px; 
    font-size:18px; 
    font-weight:bold; 
    cursor:pointer; 
    transition:0.3s; 
    display:flex; 
    align-items:center; 
    text-decoration:none; 
    color:#1D3557; 
    background-color:#e0e0e0;
}
.nav-item:hover { 
    background: linear-gradient(135deg,#ff7e5f,#feb47b); 
    color:white; 
    transform:scale(1.05);
}
.nav-item-active { 
    background: linear-gradient(135deg,#ff7e5f,#ffb347); 
    color:white; 
}
.nav-icon { 
    margin-right:8px; 
    font-size:20px; 
}
@media(max-width:768px) {
    .big-title { font-size:30px !important; }
    .section-header { font-size:20px !important; }
    .metric-card { padding: 15px; font-size: 14px; }
    .day-box { min-height:60px; font-size:11px; }
    .nav-item { padding:10px 15px; font-size:16px; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">💼 Wealth Management Dashboard</p>', unsafe_allow_html=True)

# ==========================
# Navigation Buttons
# ==========================
st.session_state.setdefault("page", "Assets")
cols = st.columns(3)
buttons = [("Assets", "💰"), ("Debts", "💳"), ("Calendar", "📅")]

for i, (name, icon) in enumerate(buttons):
    if cols[i].button(f"{icon} {name}"):
        st.session_state.page = name

# ==========================
# Assets Page
# ==========================
def assets_page():
    st.markdown('<p class="section-header">📊 Asset Overview</p>', unsafe_allow_html=True)
    df_assets = load_assets()
    
    if df_assets.empty:
        st.info("No assets found. Create **assets.csv** with columns: Name, Owner, Type, Institution, Value, Rate of Return")
    else:
        # Editable DataFrame
        st.subheader("📋 Asset Table (Editable)")
        edited_df = st.data_editor(df_assets, num_rows="dynamic", use_container_width=True)
        if not edited_df.equals(df_assets):
            save_assets(edited_df)
            st.success("Asset table updated and saved successfully!")
            df_assets = edited_df
        
        # Metrics
        total_assets = df_assets["Value"].sum()
        avg_return = df_assets["Rate of Return"].mean()
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card">💰 Total Assets<br><h3>${total_assets:,.2f}</h3></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card">📈 Avg Rate of Return<br><h3>{avg_return:.2f}%</h3></div>', unsafe_allow_html=True)
        
        # Pie Chart
        fig = px.pie(df_assets, names='Type', values='Value', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(title_text="Asset Allocation by Type", title_x=0.5, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# ==========================
# Debts Page
# ==========================
def debts_page():
    st.markdown('<p class="section-header">💳 Debt Management</p>', unsafe_allow_html=True)
    df = load_debts()
    
    if df.empty:
        st.info("No debts found. Create **debts.csv** with appropriate columns.")
    else:
        # Editable DataFrame
        st.subheader("📋 Debt Table (Editable)")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if not edited_df.equals(df):
            save_debts(edited_df)
            st.success("Debt table updated and saved successfully!")
            df = edited_df
        
        # Metrics
        total_debt = df["Balance"].sum()
        avg_rate = pd.to_numeric(df["Rate"], errors="coerce").fillna(0).mean()
        total_payment = df["Payment"].sum()
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card">💸 Total Debt<br><h3>${total_debt:,.2f}</h3></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card">📊 Avg Interest Rate<br><h3>{avg_rate:.2f}%</h3></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card">💵 Monthly Payments<br><h3>${total_payment:,.2f}</h3></div>', unsafe_allow_html=True)
        
        # Bar Chart
        fig = px.bar(df, x="Creditor", y="Balance", color="Rate", text="Balance",
                     color_continuous_scale=px.colors.sequential.Plasma)
        fig.update_layout(title="Debt Balances by Creditor", title_x=0.5, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# ==========================
# Calendar Page
# ==========================
def calendar_page():
    st.markdown('<p class="section-header">📅 Debt Payment Calendar</p>', unsafe_allow_html=True)
    df = load_debts()
    
    if df.empty:
        st.info("No debts found. Please ensure debts.csv exists.")
        return
    
    today = datetime.date.today()
    year = st.selectbox("Year", range(today.year, today.year + 5), index=0)
    month = st.selectbox("Month", range(1, 13), index=today.month-1)
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    
    st.markdown(f"### {calendar.month_name[month]} {year}")
    
    # Day names
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day_name in enumerate(day_names):
        cols[i].markdown(f"**{day_name}**", unsafe_allow_html=True)
    
    # Calendar grid with payments
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
                    if st.button(f"Add/Edit Payment {day}", key=f"{day}_btn"):
                        with st.form(f"form_{day}"):
                            name = st.text_input("Name", "")
                            creditor = st.text_input("Creditor", "")
                            balance = st.number_input("Balance ($)", min_value=0.0)
                            rate = st.number_input("Rate (%)", min_value=0.0)
                            payment = st.number_input("Payment ($)", min_value=0.0)
                            due_date_input = st.date_input("Due Date", day_date)
                            submitted = st.form_submit_button("Save Payment")
                            if submitted:
                                new_row = {"Name": name, "Creditor": creditor, "Balance": balance,
                                           "Rate": rate, "Payment": payment, "Due Date": due_date_input}
                                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                                save_debts(df)
                                st.success("Payment saved successfully!")
                                st.experimental_rerun()

# ==========================
# Render Selected Page
# ==========================
if st.session_state.page == "Assets":
    assets_page()
elif st.session_state.page == "Debts":
    debts_page()
elif st.session_state.page == "Calendar":
    calendar_page()
