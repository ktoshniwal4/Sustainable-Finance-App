import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="Sustainable Portfolio Tool", layout="wide")

st.title("📊 Sustainable Finance Portfolio Tool")

# =====================================
# SIDEBAR - USER INPUTS
# =====================================
st.sidebar.header("User Preferences")

# ESG Preference
lambda_choice = st.sidebar.selectbox(
    "ESG Preference",
    ["None", "Small", "Moderate", "Strong"]
)

lambda_map = {"None":0, "Small":0.25, "Moderate":0.75, "Strong":1}
lambda_esg = lambda_map[lambda_choice]

# Risk Aversion
gamma_method = st.sidebar.radio(
    "Risk Aversion (Gamma)",
    ["Enter manually", "Use questionnaire"]
)

# =====================================
# FUNCTIONS (UNCHANGED LOGIC)
# =====================================
def convert_to_100(score, agency):
    agency = agency.lower()

    if agency == "sustainalytics":
        score = float(score)
        if score >= 50:
            return 0.0
        return 100 - (score / 50) * 100

    elif agency == "msci":
        return {
            "ccc":0,"b":16.7,"bb":33.4,"bbb":50.1,
            "a":66.8,"aa":83.5,"aaa":100
        }[score.lower()]

    elif agency == "refinitiv":
        return {0:0,1:10,2:25,3:50,4:75,5:95}[int(score)]

    elif agency == "s&p":
        return float(score)

def portfolio_return(w, r1, r2):
    return w*r1 + (1-w)*r2

def portfolio_sd(w, sd1, sd2, rho):
    return np.sqrt(w**2*sd1**2 + (1-w)**2*sd2**2 + 2*rho*w*(1-w)*sd1*sd2)

def portfolio_esg(w, e1, e2):
    return w*e1 + (1-w)*e2

def get_esg_threshold(l, e1, e2):
    return min(e1,e2) + l*(max(e1,e2)-min(e1,e2))

# =====================================
# MAIN LAYOUT
# =====================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Asset 1")
    asset1 = st.text_input("Name", "Asset 1")
    r1 = st.number_input("Return (%)", value=8.0)/100
    sd1 = st.number_input("Volatility (%)", value=15.0)/100

with col2:
    st.subheader("Asset 2")
    asset2 = st.text_input("Name ", "Asset 2")
    r2 = st.number_input("Return (%) ", value=10.0)/100
    sd2 = st.number_input("Volatility (%) ", value=20.0)/100

# =====================================
# MARKET
# =====================================
st.subheader("Market Inputs")

rho = st.slider("Correlation", -1.0, 1.0, 0.2)
r_free = st.number_input("Risk-free rate (%)", value=2.0)/100

# =====================================
# ESG INPUT METHOD
# =====================================
st.subheader("ESG Input")

esg_method = st.radio(
    "Choose ESG input method",
    ["Enter ESG scores", "Use ESG questionnaire"]
)

# =====================================
# ESG INPUTS
# =====================================
def esg_questionnaire(name):
    st.write(f"**{name} ESG Questionnaire**")
    e = st.slider(f"{name} Environmental", 0,100,50)
    s = st.slider(f"{name} Social", 0,100,50)
    g = st.slider(f"{name} Governance", 0,100,50)
    return (e+s+g)/3

def esg_manual(name):
    agency = st.selectbox(f"{name} Provider", ["sustainalytics","refinitiv","msci","s&p"])
    val = st.text_input(f"{name} ESG Score")
    if val:
        try:
            return convert_to_100(val, agency)
        except:
            st.warning(f"Invalid ESG input for {name}")
    return None

if esg_method == "Use ESG questionnaire":
    esg1 = esg_questionnaire(asset1)
    esg2 = esg_questionnaire(asset2)
else:
    esg1 = esg_manual(asset1)
    esg2 = esg_manual(asset2)

# =====================================
# GAMMA INPUT
# =====================================
if gamma_method == "Enter manually":
    gamma = st.sidebar.number_input("Gamma", value=0.0)
else:
    st.sidebar.subheader("Risk Questionnaire")

    q1 = st.sidebar.slider("Risk attitude",1,5,3)
    q2 = st.sidebar.slider("Prefer steady returns",1,5,3)
    q3 = st.sidebar.slider("Reaction to loss",1,5,3)
    q4 = st.sidebar.slider("Risk investment share",1,5,3)
    q5 = st.sidebar.slider("Guaranteed vs uncertain",1,5,3)

    avg = np.mean([q1,q2,q3,q4,q5])

    if avg <= 1.5:
        gamma = 8
    elif avg <= 2.3:
        gamma = 4
    elif avg <= 3.2:
        gamma = 0
    elif avg <= 4.1:
        gamma = -4
    else:
        gamma = -8

    st.sidebar.write(f"Gamma = {gamma}")

# =====================================
# RUN MODEL
# =====================================
if st.button("🚀 Run Analysis"):

    if esg1 is None or esg2 is None:
        st.warning("Please complete ESG inputs")
        st.stop()

    weights = np.linspace(0,1,500)

    returns, risks, esgs, sharpes = [],[],[],[]

    for w in weights:
        r = portfolio_return(w,r1,r2)
        sd = portfolio_sd(w,sd1,sd2,rho)
        e = portfolio_esg(w,esg1,esg2)

        returns.append(r)
        risks.append(sd)
        esgs.append(e)

        sharpes.append((r-r_free)/sd if sd>0 else -np.inf)

    max_idx = np.argmax(sharpes)

    threshold = get_esg_threshold(lambda_esg, esg1, esg2)
    eligible = [i for i in range(len(weights)) if esgs[i] >= threshold]
    esg_idx = max(eligible, key=lambda i: sharpes[i])

    # =====================================
    # RESULTS TABLE
    # =====================================
    st.subheader("Results Comparison")

    df = pd.DataFrame({
        "Metric":["Return","Risk","ESG","Sharpe"],
        "No ESG":[returns[max_idx],risks[max_idx],esgs[max_idx],sharpes[max_idx]],
        "With ESG":[returns[esg_idx],risks[esg_idx],esgs[esg_idx],sharpes[esg_idx]]
    })

    st.dataframe(df.style.format({
        "No ESG":"{:.4f}",
        "With ESG":"{:.4f}"
    }))

    # =====================================
    # FRONTIER PLOT
    # =====================================
    st.subheader("Efficient Frontier")

    fig, ax = plt.subplots()

    ax.plot(risks, returns, label="Frontier")
    ax.scatter(risks[max_idx], returns[max_idx], label="Optimal")
    ax.scatter(risks[esg_idx], returns[esg_idx], label="ESG Optimal")

    ax.set_xlabel("Risk")
    ax.set_ylabel("Return")
    ax.legend()
    ax.grid()

    st.pyplot(fig)

    # =====================================
    # ESG-SHARPE PLOT
    # =====================================
    st.subheader("ESG vs Sharpe")

    fig2, ax2 = plt.subplots()

    ax2.plot(esgs, sharpes)
    ax2.set_xlabel("ESG Score")
    ax2.set_ylabel("Sharpe Ratio")
    ax2.grid()

    st.pyplot(fig2)
