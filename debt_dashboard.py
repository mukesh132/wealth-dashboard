
import math
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Debt Management Dashboard", layout="wide")
st.title("Debt Management Dashboard")
st.caption("Load your debts, tweak assumptions, and compare Snowball vs Avalanche strategies.")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    # Clean columns
    for col in ["Rate", "Balance", "Payment", "Extra"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    return df

uploaded = st.sidebar.file_uploader("Upload your debts CSV", type=["csv"])
if uploaded is None:
    st.sidebar.info("No file uploaded. Using the starter 'debts.csv'. You can replace it with your own CSV anytime.")
    df = load_data("debts.csv")
else:
    df = load_data(uploaded)

st.subheader("Current Debts")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Global inputs
st.sidebar.header("Assumptions")
extra_budget = st.sidebar.number_input("Monthly EXTRA budget across all debts ($)", min_value=0.0, value=500.0, step=50.0, help="Extra money directed to one focus debt at a time.")
max_months = st.sidebar.number_input("Max months to simulate", min_value=1, value=600, step=12)
start_date = st.sidebar.date_input("Simulation start date", value=datetime.today())
compounding = st.sidebar.selectbox("Compounding frequency", options=["Monthly"], index=0, help="Currently monthly only.")
min_floor = st.sidebar.number_input("Minimum payment floor per debt ($)", min_value=0.0, value=0.0, step=25.0, help="If a Payment is 0, enforce this minimum to avoid never-ending balances.")

st.sidebar.header("Strategy")
strategy = st.sidebar.radio("Choose strategy", ["Debt Snowball (smallest balance first)", "Debt Avalanche (highest rate first)"])

def order_debts(d):
    if strategy.startswith("Debt Snowball"):
        return d.sort_values(["Balance", "Rate"], ascending=[True, False]).index.tolist()
    else:
        return d.sort_values(["Rate", "Balance"], ascending=[False, True]).index.tolist()

def next_month(dt):
    y, m = dt.year, dt.month
    if m == 12:
        return datetime(y+1, 1, dt.day)
    # keep same day or clamp
    try:
        return datetime(y, m+1, dt.day)
    except ValueError:
        # end-of-month handling
        return datetime(y, m+1, 1) - timedelta(days=1)

def simulate(dframe: pd.DataFrame):
    d = dframe.copy()
    d["Balance"] = d["Balance"].astype(float)
    d["Rate"] = d["Rate"].astype(float).fillna(0.0)
    d["Payment"] = d["Payment"].astype(float).fillna(0.0)
    d["Extra"] = d["Extra"].astype(float).fillna(0.0)
    # Ensure payments have a minimum
    d.loc[d["Payment"] <= 0, "Payment"] = min_floor

    history = []  # records per month
    month = 0
    current_date = datetime.combine(start_date, datetime.min.time())

    while month < max_months and (d["Balance"] > 0.01).any():
        # interest accrual
        interest = d["Balance"] * (d["Rate"].fillna(0.0) / 12.0)

        # Base payments (minimums)
        base_pay = d["Payment"].clip(lower=0.0)

        # Choose focus account for extra
        order = order_debts(d)
        focus_idx = None
        for i in order:
            if d.loc[i, "Balance"] > 0.01:
                focus_idx = i
                break

        extra_vec = pd.Series(0.0, index=d.index)
        if focus_idx is not None and extra_budget > 0:
            extra_vec.loc[focus_idx] = extra_budget

        total_pay = base_pay + d["Extra"] + extra_vec

        # Prevent overpay: payment cannot exceed balance + this month's interest
        payoff_cap = d["Balance"] + interest
        applied = total_pay.clip(upper=payoff_cap)

        # Update balances
        new_balance = d["Balance"] + interest - applied
        new_balance = new_balance.clip(lower=0.0)

        # Track history
        history.append({
            "Date": current_date,
            "Month": month,
            "Total Balance": new_balance.sum(),
            "Total Interest This Month": float(interest.sum()),
            "Total Payment This Month": float(applied.sum()),
            "Focus Debt": d.loc[focus_idx, "Name"] if focus_idx is not None else ""
        })

        d["Balance"] = new_balance
        month += 1
        current_date = next_month(current_date)

    hist = pd.DataFrame(history)
    # Final stats per debt
    result = dframe.copy()
    result["Ending Balance"] = d["Balance"]
    result["Is Paid"] = result["Ending Balance"] <= 0.01

    return hist, result

hist, result = simulate(edited)

# KPIs
col1, col2, col3, col4 = st.columns(4)
total_debt = result["Ending Balance"].sum()
months_to_clear = int(hist["Month"].max()) if not hist.empty else 0
total_interest = hist["Total Interest This Month"].sum() if not hist.empty else 0.0
total_payment = hist["Total Payment This Month"].sum() if not hist.empty else 0.0

col1.metric("Total Ending Debt ($)", f"{total_debt:,.2f}")
col2.metric("Estimated Months to Payoff", f"{months_to_clear}")
col3.metric("Total Interest Paid ($)", f"{total_interest:,.2f}")
col4.metric("Total Payments Made ($)", f"{total_payment:,.2f}")

# Charts (matplotlib, single-plot, no explicit colors)
if not hist.empty:
    st.subheader("Total Balance Over Time")
    fig1, ax1 = plt.subplots()
    ax1.plot(hist["Date"], hist["Total Balance"])
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Total Balance ($)")
    ax1.set_title("Total Balance Over Time")
    st.pyplot(fig1)

    st.subheader("Monthly Interest Paid Over Time")
    fig2, ax2 = plt.subplots()
    ax2.plot(hist["Date"], hist["Total Interest This Month"])
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Interest ($)")
    ax2.set_title("Monthly Interest Paid Over Time")
    st.pyplot(fig2)

st.subheader("Final Status by Debt")
st.dataframe(result, use_container_width=True)

st.download_button("Download edited debts as CSV", edited.to_csv(index=False).encode("utf-8"), file_name="debts_edited.csv", mime="text/csv")

st.divider()
st.markdown("""
**How it works**
- Interest is accrued monthly as `balance * rate / 12`.
- Minimum payments are applied to all debts.
- Your chosen strategy picks one **focus debt** per month for all extra budget.
- Overpayments are capped at the remaining balance + current month's interest.
- Repeat each month until debts are cleared or the max months is reached.

**Tips**
- For Avalanche, fill in missing rates (e.g., credit cards) to prioritize correctly.
- For Snowball, the balances drive the order even if rates are 0.
- Set a non-zero **Minimum payment floor** if any debt has Payment = 0.
- You can add/remove debts right in the table above.
""")
