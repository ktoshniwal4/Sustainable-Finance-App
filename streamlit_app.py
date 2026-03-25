import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# --- 1. INITIALIZATION & SESSION STATE ---
# We use session state to handle the questionnaire logic without losing data on rerun.
if 'gamma' not in st.session_state:
    st.session_state.gamma = 3.0

# --- 2. CORE FINANCIAL & ESG LOGIC ---
def portfolio_return(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2*rho*w1*(1-w1)*sd1*sd2)

def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2

def convert_to_100(score, agency):
    """Retains original mapping logic including MSCI letter grades."""
    agency = agency.lower()
    try:
        if agency == "sustainalytics":
            s = float(score)
            return max(0.0, min(100.0, 100 - (s / 50) * 100)) if s < 50 else 0.0
        elif agency == "msci":
            msci_map = {"ccc": 0.0, "b": 16.7, "bb": 33.4, "bbb": 50.1, "a": 66.8, "aa": 83.5, "aaa": 100.0}
            return msci_map.get(str(score).strip().lower(), 0.0)
        elif agency == "refinitiv":
            r_map = {0: 0.0, 1: 10.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 95.0}
            return r_map.get(int(float(score)), 0.0)
        elif agency == "s&p":
            return max(0.0, min(100.0, float(score)))
    except:
        return 0.0
    return 0.0

# --- 3. APP INTERFACE ---
st.set_page_config(page_title="Sustainable Finance Tool", layout="wide")
st.title("🌱 Sustainable Finance Portfolio Tool")
st.markdown("Compare investments based on financial performance, risk, and ESG alignment.")

# --- 4. SIDEBAR: ASSET & MARKET DATA ---
st.sidebar.header("1. ASSET INFORMATION")
asset1_name = st.sidebar.text_input("Asset 1 Name", "Apple")
asset2_name = st.sidebar.text_input("Asset 2 Name", "Tesla")

st.sidebar.subheader("Returns & Volatility")
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    r1 = st.number_input(f"{asset1_name} Return %", value=8.0) / 100
    sd1 = st.number_input(f"{asset1_name} Vol %", value=15.0) / 100
    agency1 = st.selectbox(f"{asset1_name} Agency", ["MSCI", "Sustainalytics", "Refinitiv", "S&P"], key="ag1")
with col_s2:
    r2 = st.number_input(f"{asset2_name} Return %", value=10.0) / 100
    sd2 = st.number_input(f"{asset2_name} Vol %", value=20.0) / 100
    agency2 = st.selectbox(f"{asset2_name} Agency", ["MSCI", "Sustainalytics", "Refinitiv", "S&P"], key="ag2")

st.sidebar.divider()
st.sidebar.header("2. MARKET DATA")
rho = st.sidebar.slider("Correlation Coefficient", -1.0, 1.0, 0.2)
r_free = st.sidebar.number_input("Risk-free Rate %", value=2.0) / 100

# --- 5. RISK PREFERENCE (GAMMA QUESTIONNAIRE) ---
st.header("Step 1: Determine Risk Aversion (Gamma)")
with st.expander("Uncertain about your Gamma? Take the Risk Questionnaire"):
    q1 = st.selectbox("Q1. General attitude toward risk?", ["1. Avoid risk", "2. Low-risk steady", "3. Moderate", "4. High return focus", "5. High-risk seeker"])
    q2 = st.selectbox("Q2. Preference for slow/steady growth?", ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])
    q3 = st.selectbox("Q3. Reaction to 20% drop?", ["1. Sell all", "2. Sell some", "3. Wait", "4. Stay course", "5. Buy more"])
    q4 = st.selectbox("Q4. Comfort with high-risk placement?", ["1. Very little", "2. < Quarter", "3. Half", "4. > Half", "5. All"])
    q5 = st.selectbox("Q5. Prefer small guaranteed return?", ["1. Strongly Agree", "2. Agree", "3. Neutral", "4. Disagree", "5. Strongly Disagree"])
    
    # Calculation matches original logic
    avg_score = (int(q1[0]) + int(q2[0]) + int(q3[0]) + int(q4[0]) + int(q5[0])) / 5
    if avg_score <= 1.5: st.session_state.gamma = 8.0
    elif avg_score <= 2.3: st.session_state.gamma = 4.0
    elif avg_score <= 3.2: st.session_state.gamma = 0.0
    elif avg_score <= 4.1: st.session_state.gamma = -4.0
    else: st.session_state.gamma = -8.0
    
st.write(f"Current Gamma Value: **{st.session_state.gamma}**")

# --- 6. ESG INPUTS (PILLAR SUPPORT) ---
st.header("Step 2: Enter ESG Information")
esg_method = st.radio("Choose Input Method:", ["Overall Scores", "Separate E, S, and G Pillars"], horizontal=True)

w_e, w_s, w_g = 34, 33, 33 # Defaults
if esg_method == "Separate E, S, and G Pillars":
    c_w1, c_w2, c_w3 = st.columns(3)
    with c_w1: w_e = st.number_input("Env Weight %", 0, 100, 34)
    with c_w2: w_s = st.number_input("Soc Weight %", 0, 100, 33)
    with c_w3: w_g = st.number_input("Gov Weight %", 0, 100, 33)
    if (w_e + w_s + w_g) != 100:
        st.error("⚠️ Weights must sum to 100%!")

def get_esg_input(name, agency, key_p):
    if esg_method == "Overall Scores":
        if agency == "MSCI":
            val = st.selectbox(f"{name} Rating", ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"], index=3, key=f"{key_p}_o")
        elif agency == "Refinitiv":
            val = st.number_input(f"{name} Score (0-5)", 0, 5, 3, key=f"{key_p}_o")
        else:
            val = st.number_input(f"{name} Score (0-100)", 0.0, 100.0, 50.0, key=f"{key_p}_o")
        return convert_to_100(val, agency)
    else:
        st.write(f"**{name} ({agency})**")
        if agency == "MSCI":
            e = st.selectbox(f"{name} Env", ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"], index=3, key=f"{key_p}_e")
            s = st.selectbox(f"{name} Soc", ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"], index=3, key=f"{key_p}_s")
            g = st.selectbox(f"{name} Gov", ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"], index=3, key=f"{key_p}_g")
        elif agency == "Refinitiv":
            e = st.number_input(f"{name} Env (0-5)", 0, 5, 3, key=f"{key_p}_e")
            s = st.number_input(f"{name} Soc (0-5)", 0, 5, 3, key=f"{key_p}_s")
            g = st.number_input(f"{name} Gov (0-5)", 0, 5, 3, key=f"{key_p}_g")
        else:
            e = st.number_input(f"{name} Env", 0.0, 100.0, 50.0, key=f"{key_p}_e")
            s = st.number_input(f"{name} Soc", 0.0, 100.0, 50.0, key=f"{key_p}_s")
            g = st.number_input(f"{name} Gov", 0.0, 100.0, 50.0, key=f"{key_p}_g")
        
        e_100, s_100, g_100 = convert_to_100(e, agency), convert_to_100(s, agency), convert_to_100(g, agency)
        return (w_e/100)*e_100 + (w_s/100)*s_100 + (w_g/100)*g_100

col_esg1, col_esg2 = st.columns(2)
with col_esg1: esg1_100 = get_esg_input(asset1_name, agency1, "p1")
with col_esg2: esg2_100 = get_esg_input(asset2_name, agency2, "p2")

# --- 7. ESG PREFERENCES ---
st.header("Step 3: ESG Preferences")
lambda_choice = st.select_slider("Willingness to sacrifice return for better ESG:", 
                                 options=["None", "Small", "Moderate", "Significant"])
l_map = {"None": 0.0, "Small": 0.25, "Moderate": 0.75, "Significant": 1.0}
lambda_esg = l_map[lambda_choice]
esg_threshold = min(esg1_100, esg2_100) + lambda_esg * (max(esg1_100, esg2_100) - min(esg1_100, esg2_100))
st.info(f"Target Portfolio ESG Score: **{esg_threshold:.2f}**")

# --- 8. CALCULATIONS ---
weights = np.linspace(0, 1, 1000)
rets = portfolio_return(weights, r1, r2)
vols = portfolio_sd(weights, sd1, sd2, rho)
esgs = portfolio_esg(weights, esg1_100, esg2_100)
sharpes = (rets - r_free) / vols

idx_all = np.argmax(sharpes)
eligible = np.where(esgs >= esg_threshold)[0]

if len(eligible) == 0:
    st.error("❌ No portfolio combinations meet your ESG criteria with these assets.")
else:
    idx_esg = eligible[np.argmax(sharpes[eligible])]

    # --- 9. DISPLAY RESULTS ---
    st.header("Step 4: Results & Visuals")
    res_df = pd.DataFrame({
        "Metric": [f"{asset1_name} Weight", f"{asset2_name} Weight", "Exp. Return", "Risk (Vol)", "ESG Score", "Sharpe Ratio"],
        "Optimal (Unconstrained)": [f"{weights[idx_all]*100:.1f}%", f"{(1-weights[idx_all])*100:.1f}%", f"{rets[idx_all]*100:.2f}%", f"{vols[idx_all]*100:.2f}%", f"{esgs[idx_all]:.2f}", f"{sharpes[idx_all]:.4f}"],
        "Optimal (ESG Constrained)": [f"{weights[idx_esg]*100:.1f}%", f"{(1-weights[idx_esg])*100:.1f}%", f"{rets[idx_esg]*100:.2f}%", f"{vols[idx_esg]*100:.2f}%", f"{esgs[idx_esg]:.2f}", f"{sharpes[idx_esg]:.4f}"]
    })
    st.table(res_df)

    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Efficient Frontier
    ax1.plot(vols, rets, color="gray", alpha=0.3, label="All Portfolios")
    ax1.plot(vols[eligible], rets[eligible], color="green", linewidth=3, label="ESG Compliant")
    ax1.scatter(vols[idx_all], rets[idx_all], marker="*", s=250, color="blue", label="Max Sharpe")
    ax1.scatter(vols[idx_esg], rets[idx_esg], marker="*", s=250, color="green", label="Max Sharpe (ESG)")
    ax1.set_xlabel("Volatility (Risk)")
    ax1.set_ylabel("Expected Return")
    ax1.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax1.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax1.legend()
    ax1.set_title("Efficient Frontier")

    # ESG-Sharpe Trade-off
    ax2.plot(esgs, sharpes, color="red", linewidth=2)
    ax2.axvline(esg_threshold, color="black", linestyle="--", label="User Threshold")
    ax2.set_xlabel("Portfolio ESG Score")
    ax2.set_ylabel("Sharpe Ratio")
    ax2.set_title("ESG vs. Sharpe Ratio")
    ax2.legend()
    
    st.pyplot(fig)

    st.success(f"By applying your ESG constraints, your ESG score increased by **{esgs[idx_esg] - esgs[idx_all]:.2f} points**.")
