import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ================================
# PAGE SETUP
# ================================
st.set_page_config(page_title="Sustainable Portfolio Tool", layout="wide")

st.title("Sustainable Finance Portfolio Tool")

st.write("""
This tool helps you compare two investments based on:
- financial performance
- risk
- ESG preferences
""")

# ================================
# FUNCTIONS (UNCHANGED LOGIC)
# ================================

def convert_to_100(score, agency):
    agency = agency.lower()

    if agency == "sustainalytics":
        score = float(score)
        if score >= 50:
            return 0.0
        return max(0.0, min(100.0, 100 - (score / 50) * 100))

    elif agency == "msci":
        msci_map = {
            "ccc": 0.0, "b": 16.7, "bb": 33.4,
            "bbb": 50.1, "a": 66.8, "aa": 83.5, "aaa": 100.0
        }
        return msci_map[str(score).lower()]

    elif agency == "refinitiv":
        refinitiv_map = {0: 0, 1: 10, 2: 25, 3: 50, 4: 75, 5: 95}
        return refinitiv_map[int(score)]

    elif agency == "s&p":
        return float(score)

def portfolio_return(w, r1, r2):
    return w * r1 + (1 - w) * r2

def portfolio_sd(w, sd1, sd2, rho):
    return np.sqrt(
        w**2 * sd1**2 +
        (1-w)**2 * sd2**2 +
        2 * rho * w * (1-w) * sd1 * sd2
    )

def portfolio_esg(w, esg1, esg2):
    return w * esg1 + (1-w) * esg2

def get_esg_threshold(lambda_esg, esg1, esg2):
    return min(esg1, esg2) + lambda_esg * (max(esg1, esg2) - min(esg1, esg2))

# ================================
# ESG INPUT METHOD
# ================================

st.header("ESG Input Method")

method = st.radio(
    "How would you like to enter ESG information?",
    ["Overall ESG score", "Separate E, S, G scores"]
)

use_separate = method == "Separate E, S, G scores"

if use_separate:
    st.subheader("ESG Weights")
    w_e = st.number_input("Environmental weight (%)", 0.0, 100.0, 33.3)
    w_s = st.number_input("Social weight (%)", 0.0, 100.0, 33.3)
    w_g = st.number_input("Governance weight (%)", 0.0, 100.0, 33.4)

# ================================
# ASSET INPUTS
# ================================

st.header("Assets")

col1, col2 = st.columns(2)

with col1:
    asset1 = st.text_input("Asset 1 name", "Asset 1")
    r1 = st.number_input("Return (%) Asset 1") / 100
    sd1 = st.number_input("Volatility (%) Asset 1", min_value=0.0) / 100

with col2:
    asset2 = st.text_input("Asset 2 name", "Asset 2")
    r2 = st.number_input("Return (%) Asset 2") / 100
    sd2 = st.number_input("Volatility (%) Asset 2", min_value=0.0) / 100

# ================================
# MARKET INPUTS
# ================================

st.header("Market")

rho = st.slider("Correlation", -1.0, 1.0, 0.0)
r_free = st.number_input("Risk-free rate (%)") / 100
gamma = st.number_input("Risk aversion (gamma)", value=0.0)

# ================================
# ESG SCORES
# ================================

def esg_input_block(name):
    agency = st.selectbox(
        f"{name} ESG Provider",
        ["sustainalytics", "refinitiv", "msci", "s&p"]
    )

    if use_separate:
        e = st.text_input(f"{name} Environmental")
        s = st.text_input(f"{name} Social")
        g = st.text_input(f"{name} Governance")

        if e and s and g:
            e100 = convert_to_100(e, agency)
            s100 = convert_to_100(s, agency)
            g100 = convert_to_100(g, agency)
            total = (w_e/100)*e100 + (w_s/100)*s100 + (w_g/100)*g100
            return total
        return None

    else:
        val = st.text_input(f"{name} ESG Score")
        if val:
            return convert_to_100(val, agency)
        return None

st.header("ESG Scores")

esg1 = esg_input_block(asset1)
esg2 = esg_input_block(asset2)

# ================================
# ESG PREFERENCE
# ================================

lambda_choice = st.selectbox(
    "ESG Preference",
    ["None", "Small", "Moderate", "Strong"]
)

lambda_map = {"None":0, "Small":0.25, "Moderate":0.75, "Strong":1}
lambda_esg = lambda_map[lambda_choice]

# ================================
# RUN MODEL
# ================================

if st.button("Run Analysis"):

    weights = np.linspace(0,1,500)

    returns = []
    risks = []
    esgs = []
    sharpes = []

    for w in weights:
        r = portfolio_return(w, r1, r2)
        sd = portfolio_sd(w, sd1, sd2, rho)
        e = portfolio_esg(w, esg1, esg2)

        returns.append(r)
        risks.append(sd)
        esgs.append(e)

        if sd > 0:
            sharpes.append((r - r_free)/sd)
        else:
            sharpes.append(-np.inf)

    max_idx = np.argmax(sharpes)

    # ESG constraint
    threshold = get_esg_threshold(lambda_esg, esg1, esg2)

    eligible = [i for i in range(len(weights)) if esgs[i] >= threshold]

    esg_idx = max(eligible, key=lambda i: sharpes[i])

    # ================================
    # RESULTS TABLE
    # ================================

    df = pd.DataFrame({
        "Metric": ["Return","Risk","ESG","Sharpe"],
        "No ESG": [
            returns[max_idx],
            risks[max_idx],
            esgs[max_idx],
            sharpes[max_idx]
        ],
        "With ESG": [
            returns[esg_idx],
            risks[esg_idx],
            esgs[esg_idx],
            sharpes[esg_idx]
        ]
    })

    st.subheader("Results")
    st.dataframe(df)

    # ================================
    # PLOT
    # ================================

    fig, ax = plt.subplots()

    ax.plot(risks, returns, label="Frontier")
    ax.scatter(risks[max_idx], returns[max_idx], label="Optimal")
    ax.scatter(risks[esg_idx], returns[esg_idx], label="ESG Optimal")

    ax.set_xlabel("Risk")
    ax.set_ylabel("Return")
    ax.legend()

    st.pyplot(fig)
