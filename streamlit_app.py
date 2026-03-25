import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sustainable Finance Tool", layout="wide")

# --- HELPER FUNCTIONS ---
def portfolio_return(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(
        w1 ** 2 * sd1 ** 2 +
        (1 - w1) ** 2 * sd2 ** 2 +
        2 * rho * w1 * (1 - w1) * sd1 * sd2
    )

def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2

def convert_to_100(score, agency):
    agency = agency.lower()
    try:
        if agency == "sustainalytics":
            val = float(score)
            return max(0.0, min(100.0, 100 - (val / 50) * 100)) if val < 50 else 0.0
        elif agency == "msci":
            msci_map = {"ccc": 0.0, "b": 16.7, "bb": 33.4, "bbb": 50.1, "a": 66.8, "aa": 83.5, "aaa": 100.0}
            return msci_map.get(str(score).strip().lower(), 0.0)
        elif agency == "refinitiv":
            refinitiv_map = {0: 0.0, 1: 10.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 95.0}
            return refinitiv_map.get(int(float(score)), 0.0)
        elif agency == "s&p":
            return max(0.0, min(100.0, float(score)))
    except:
        return 0.0
    return 0.0

# --- APP LAYOUT ---
st.title("🌱 Sustainable Finance Portfolio Tool")
st.markdown("Compare investments based on financial performance, risk, and ESG alignment.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Portfolio Assets")
asset1_name = st.sidebar.text_input("Asset 1 Name", "Apple")
asset2_name = st.sidebar.text_input("Asset 2 Name", "Tesla")

st.sidebar.divider()
st.sidebar.header("2. Financial Assumptions")
col1, col2 = st.sidebar.columns(2)

with col1:
    st.subheader(asset1_name)
    r1 = st.number_input(f"{asset1_name} Return (%)", value=8.0) / 100
    sd1 = st.number_input(f"{asset1_name} Volatility (%)", value=15.0) / 100
    agency1 = st.selectbox(f"{asset1_name} Agency", ["Sustainalytics", "Refinitiv", "MSCI", "S&P"], key="ag1")

with col2:
    st.subheader(asset2_name)
    r2 = st.number_input(f"{asset2_name} Return (%)", value=10.0) / 100
    sd2 = st.number_input(f"{asset2_name} Volatility (%)", value=20.0) / 100
    agency2 = st.selectbox(f"{asset2_name} Agency", ["Sustainalytics", "Refinitiv", "MSCI", "S&P"], key="ag2")

st.sidebar.divider()
rho = st.sidebar.slider("Correlation Coefficient", -1.0, 1.0, 0.2)
r_free = st.sidebar.number_input("Risk-free Rate (%)", value=2.0) / 100
gamma = st.sidebar.slider("Risk Aversion (Gamma)", -10.0, 10.0, 3.0)

# --- MAIN CONTENT TABS ---
tab_esg, tab_results, tab_plots = st.tabs(["ESG Inputs", "Performance Analysis", "Visualizations"])

with tab_esg:
    st.header("ESG Profile Setup")
    esg_method = st.radio("How do you want to enter ESG data?", ["Overall Score", "Separate E, S, and G Pillars"])
    
    col_a, col_b = st.columns(2)
    
    def get_score_input(name, agency, key_p):
        if esg_method == "Overall Score":
            if agency == "MSCI":
                val = st.selectbox(f"{name} Rating", ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"], index=3, key=f"{key_p}_m")
            elif agency == "Refinitiv":
                val = st.number_input(f"{name} Score (0-5)", 0, 5, 3, key=f"{key_p}_r")
            else:
                val = st.number_input(f"{name} Score", value=25.0, key=f"{key_p}_s")
            return convert_to_100(val, agency)
        else:
            e = st.number_input(f"{name} Env", value=70.0, key=f"{key_p}_e")
            s = st.number_input(f"{name} Soc", value=60.0, key=f"{key_p}_s")
            g = st.number_input(f"{name} Gov", value=65.0, key=f"{key_p}_g")
            # For simplicity in this UI, we treat pillar scores as 0-100 or agency-specific
            e1, s1, g1 = convert_to_100(e, agency), convert_to_100(s, agency), convert_to_100(g, agency)
            return (e1 + s1 + g1) / 3

    with col_a:
        st.subheader(f"{asset1_name} ESG")
        esg1_100 = get_score_input(asset1_name, agency1, "a1")
    with col_b:
        st.subheader(f"{asset2_name} ESG")
        esg2_100 = get_score_input(asset2_name, agency2, "a2")

    st.divider()
    st.subheader("ESG Preference (Lambda)")
    lambda_choice = st.select_slider(
        "Willingness to sacrifice return for ESG score:",
        options=["None", "Small", "Moderate", "Significant"]
    )
    lambda_map = {"None": 0.0, "Small": 0.25, "Moderate": 0.75, "Significant": 1.0}
    l_esg = lambda_map[lambda_choice]
    esg_threshold = min(esg1_100, esg2_100) + l_esg * (max(esg1_100, esg2_100) - min(esg1_100, esg2_100))
    st.info(f"Minimum Portfolio ESG Score required: **{esg_threshold:.2f}**")

# --- CALCULATIONS ---
weights = np.linspace(0, 1, 1000)
rets, vols, esgs, sharpes = [], [], [], []

for w in weights:
    p_ret = portfolio_return(w, r1, r2)
    p_vol = portfolio_sd(w, sd1, sd2, rho)
    p_esg = portfolio_esg(w, esg1_100, esg2_100)
    rets.append(p_ret)
    vols.append(p_vol)
    esgs.append(p_esg)
    sharpes.append((p_ret - r_free) / p_vol if p_vol > 0 else 0)

# Optimal Portfolios
idx_all = np.argmax(sharpes)
eligible_idx = [i for i, e in enumerate(esgs) if e >= esg_threshold]

if not eligible_idx:
    st.error("No portfolio combinations meet your ESG criteria.")
    st.stop()

idx_esg = eligible_idx[np.argmax([sharpes[i] for i in eligible_idx])]

with tab_results:
    st.header("Comparison Table")
    
    res_df = pd.DataFrame({
        "Metric": [f"{asset1_name} %", f"{asset2_name} %", "Exp. Return", "Risk (Volatility)", "ESG Score", "Sharpe Ratio"],
        "Unconstrained": [
            f"{weights[idx_all]*100:.1f}%", f"{(1-weights[idx_all])*100:.1f}%", 
            f"{rets[idx_all]*100:.2f}%", f"{vols[idx_all]*100:.2f}%", 
            f"{esgs[idx_all]:.2f}", f"{sharpes[idx_all]:.4f}"
        ],
        "ESG Constrained": [
            f"{weights[idx_esg]*100:.1f}%", f"{(1-weights[idx_esg])*100:.1f}%", 
            f"{rets[idx_esg]*100:.2f}%", f"{vols[idx_esg]*100:.2f}%", 
            f"{esgs[idx_esg]:.2f}", f"{sharpes[idx_esg]:.4f}"
        ]
    })
    st.table(res_df)

    st.subheader("Impact Summary")
    ret_diff = (rets[idx_esg] - rets[idx_all]) * 100
    esg_diff = esgs[idx_esg] - esgs[idx_all]
    st.write(f"By applying your ESG constraints, your expected return changed by **{ret_diff:.2f} percentage points** and your ESG score changed by **{esg_diff:.2f} points**.")

with tab_plots:
    st.header("Visual Analysis")
    
    col_plot1, col_plot2 = st.columns(2)
    
    with col_plot1:
        st.subheader("Efficient Frontier")
        fig1, ax1 = plt.subplots()
        ax1.plot(vols, rets, label="Possible Portfolios", color="grey", alpha=0.5)
        # Highlight constrained frontier
        cvols = [vols[i] for i in eligible_idx]
        crets = [rets[i] for i in eligible_idx]
        ax1.plot(cvols, crets, color="green", linewidth=2, label="ESG Eligible")
        # Stars
        ax1.scatter(vols[idx_all], rets[idx_all], marker="*", s=200, color="blue", label="Optimal")
        ax1.scatter(vols[idx_esg], rets[idx_esg], marker="*", s=200, color="green", label="Optimal (ESG)")
        
        ax1.set_xlabel("Volatility (Risk)")
        ax1.set_ylabel("Expected Return")
        ax1.xaxis.set_major_formatter(PercentFormatter(1.0))
        ax1.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax1.legend()
        st.pyplot(fig1)

    with col_plot2:
        st.subheader("ESG-Sharpe Tradeoff")
        fig2, ax2 = plt.subplots()
        ax2.plot(esgs, sharpes, color="red")
        ax2.axvline(esg_threshold, color="black", linestyle="--", label="Your Threshold")
        ax2.scatter(esgs[idx_all], sharpes[idx_all], color="blue", marker="*")
        ax2.scatter(esgs[idx_esg], sharpes[idx_esg], color="green", marker="*")
        
        ax2.set_xlabel("Portfolio ESG Score")
        ax2.set_ylabel("Sharpe Ratio")
        ax2.legend()
        st.pyplot(fig2)

st.divider()
st.info("Note: Normalized ESG scores are scaled 0-100 where 100 is best.")
