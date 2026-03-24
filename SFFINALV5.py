#!/usr/bin/env python
# coding: utf-8

# In[5]:


# streamlit_app.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

st.set_page_config(page_title="Sustainable Finance Portfolio Tool", layout="wide")

# ------------------------------------------
# Helper Functions
# ------------------------------------------
def convert_to_100(score, agency):
    agency = agency.lower()
    if agency == "sustainalytics":
        score = float(score)
        if score >= 50:
            return 0.0
        return max(0.0, min(100.0, 100 - (score / 50) * 100))
    elif agency == "msci":
        msci_map = {
            "ccc": 0.0,
            "b": 16.7,
            "bb": 33.4,
            "bbb": 50.1,
            "a": 66.8,
            "aa": 83.5,
            "aaa": 100.0
        }
        score = str(score).strip().lower()
        if score not in msci_map:
            raise ValueError("Invalid MSCI rating")
        return msci_map[score]
    elif agency == "refinitiv":
        score = int(float(score))
        refinitiv_map = {0:0.0,1:10.0,2:25.0,3:50.0,4:75.0,5:95.0}
        if score not in refinitiv_map:
            raise ValueError("Invalid Refinitiv / LSEG score")
        return refinitiv_map[score]
    elif agency == "s&p":
        score = float(score)
        return max(0.0, min(100.0, score))
    else:
        raise ValueError("Unknown agency.")

def convert_100_to_1(score_100):
    return score_100 / 100

def portfolio_return(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(
        w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2*rho*w1*(1-w1)*sd1*sd2
    )

def portfolio_esg(w1, esg1, esg2):
    return w1*esg1 + (1-w1)*esg2

def get_esg_threshold(lambda_esg, esg1_100, esg2_100):
    return min(esg1_100, esg2_100) + lambda_esg*(max(esg1_100, esg2_100)-min(esg1_100, esg2_100))

# ------------------------------------------
# Streamlit UI
# ------------------------------------------
st.title("🌱 Sustainable Finance Portfolio Tool")
st.write("Compare two investments based on financial performance, risk, and ESG preferences.")

# ------------------------------------------
# Asset Information
# ------------------------------------------
st.header("Asset Information")
asset1_name = st.text_input("Name of the first company or fund", "Apple")
asset2_name = st.text_input("Name of the second company or fund", "Microsoft")

st.subheader(f"Financial Information for {asset1_name}")
r1 = st.number_input(f"Expected annual return for {asset1_name} (%)", min_value=-100.0, max_value=100.0, value=8.0)/100
sd1 = st.number_input(f"Annual volatility for {asset1_name} (%)", min_value=0.0, max_value=100.0, value=15.0)/100

st.subheader(f"Financial Information for {asset2_name}")
r2 = st.number_input(f"Expected annual return for {asset2_name} (%)", min_value=-100.0, max_value=100.0, value=10.0)/100
sd2 = st.number_input(f"Annual volatility for {asset2_name} (%)", min_value=0.0, max_value=100.0, value=20.0)/100

st.header("Market Information")
rho = st.number_input(f"Correlation coefficient between {asset1_name} and {asset2_name}", -1.0, 1.0, 0.2)
r_free = st.number_input("Risk-free rate (%)", 0.0, 20.0, 2.0)/100

# ------------------------------------------
# ESG Information
# ------------------------------------------
st.header("ESG Information")
esg_input_method = st.radio("Do you want to enter:", 
                            ["Overall ESG scores for both assets", 
                             "Separate Environmental, Social, and Governance (E/S/G) scores for both assets"])
use_separate_scores = (esg_input_method == "Separate Environmental, Social, and Governance (E/S/G) scores for both assets")

pillar_weights = None
if use_separate_scores:
    st.subheader("Pillar Weights (%)")
    w_e = st.number_input("Environmental weight", 0, 100, 33)
    w_s = st.number_input("Social weight", 0, 100, 33)
    w_g = st.number_input("Governance weight", 0, 100, 34)
    if w_e + w_s + w_g != 100:
        st.warning("Weights must add up to 100%. Using default 33/33/34.")
        w_e, w_s, w_g = 33, 33, 34
    pillar_weights = (w_e, w_s, w_g)

def ask_esg_score_streamlit(asset_name, use_separate_scores, pillar_weights):
    agency = st.selectbox(f"ESG rating agency for {asset_name}", ["Sustainalytics", "Refinitiv", "MSCI", "S&P"])
    agency_key = agency.lower()
    
    if use_separate_scores:
        e_raw = st.text_input(f"{asset_name} Environmental score", "25")
        s_raw = st.text_input(f"{asset_name} Social score", "25")
        g_raw = st.text_input(f"{asset_name} Governance score", "25")
        e_100 = convert_to_100(e_raw, agency_key)
        s_100 = convert_to_100(s_raw, agency_key)
        g_100 = convert_to_100(g_raw, agency_key)
        w_e, w_s, w_g = pillar_weights
        overall_100 = (w_e/100)*e_100 + (w_s/100)*s_100 + (w_g/100)*g_100
        overall_1 = convert_100_to_1(overall_100)
        return overall_100, overall_1
    else:
        overall_raw = st.text_input(f"{asset_name} Overall ESG score", "50")
        overall_100 = convert_to_100(overall_raw, agency_key)
        overall_1 = convert_100_to_1(overall_100)
        return overall_100, overall_1

esg1_100, esg1_1 = ask_esg_score_streamlit(asset1_name, use_separate_scores, pillar_weights)
esg2_100, esg2_1 = ask_esg_score_streamlit(asset2_name, use_separate_scores, pillar_weights)

st.header("ESG Preference")
lambda_esg = st.slider("How important is ESG in your portfolio? (0 = not at all, 1 = very important)", 0.0, 1.0, 0.5)

# ------------------------------------------
# Portfolio Calculations
# ------------------------------------------
weights = np.linspace(0, 1, 1000)
returns, risks, esg_scores_100, sharpe_ratios = [], [], [], []

for w in weights:
    port_ret = portfolio_return(w, r1, r2)
    port_sd = portfolio_sd(w, sd1, sd2, rho)
    port_esg_display = portfolio_esg(w, esg1_100, esg2_100)
    
    returns.append(port_ret)
    risks.append(port_sd)
    esg_scores_100.append(port_esg_display)
    
    sharpe = (port_ret - r_free)/port_sd if port_sd>0 else -np.inf
    sharpe_ratios.append(sharpe)

# Tangency portfolios
max_sharpe_index = np.argmax(sharpe_ratios)
w1_tangency = weights[max_sharpe_index]
w2_tangency = 1 - w1_tangency
ret_tangency = returns[max_sharpe_index]
sd_tangency = risks[max_sharpe_index]
esg_tangency_100 = esg_scores_100[max_sharpe_index]

# ESG-constrained portfolios
esg_threshold = get_esg_threshold(lambda_esg, esg1_100, esg2_100)
eligible_indices = [i for i, esg in enumerate(esg_scores_100) if esg >= esg_threshold]
if not eligible_indices:
    st.error("No portfolio satisfies your ESG threshold. Adjust lambda or scores.")
else:
    eligible_sharpes = [(returns[i]-r_free)/risks[i] if risks[i]>0 else -np.inf for i in eligible_indices]
    max_sharpe_esg_index = eligible_indices[np.argmax(eligible_sharpes)]
    w1_tangency_esg = weights[max_sharpe_esg_index]
    w2_tangency_esg = 1 - w1_tangency_esg
    ret_tangency_esg = returns[max_sharpe_esg_index]
    sd_tangency_esg = risks[max_sharpe_esg_index]
    esg_tangency_esg_100 = esg_scores_100[max_sharpe_esg_index]

# ------------------------------------------
# Display Results
# ------------------------------------------
st.header("Portfolio Comparison")
portfolio_table = pd.DataFrame({
    "Metric": [f"{asset1_name} weight", f"{asset2_name} weight", "Expected return", "Risk (std dev)", "Portfolio ESG score", "Sharpe ratio"],
    "Optimal risky portfolio (no ESG constraint)":[f"{w1_tangency*100:.2f}%", f"{w2_tangency*100:.2f}%", f"{ret_tangency*100:.2f}%", f"{sd_tangency*100:.2f}%", f"{esg_tangency_100:.2f}", f"{sharpe_ratios[max_sharpe_index]:.4f}"],
    "Optimal risky portfolio (with ESG constraint)":[f"{w1_tangency_esg*100:.2f}%", f"{w2_tangency_esg*100:.2f}%", f"{ret_tangency_esg*100:.2f}%", f"{sd_tangency_esg*100:.2f}%", f"{esg_tangency_esg_100:.2f}", f"{eligible_sharpes[np.argmax(eligible_sharpes)]:.4f}"]
})
st.dataframe(portfolio_table)

# ------------------------------------------
# Plot Efficient Frontier
# ------------------------------------------
st.header("Efficient Frontier")
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(risks, returns, color="blue", label="Frontier")
ax.scatter(sd_tangency, ret_tangency, color="blue", marker="*", s=100, label="Tangency")
ax.scatter(sd_tangency_esg, ret_tangency_esg, color="green", marker="*", s=100, label="Tangency ESG")
ax.set_xlabel("Risk (Std Dev)")
ax.set_ylabel("Expected Return")
ax.set_title("Efficient Frontier with ESG Constraint")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)


# In[ ]:




