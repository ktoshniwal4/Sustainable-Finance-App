import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

# -------------------------------
# CORE FUNCTIONS
# -------------------------------
def portfolio_return(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(w1**2 * sd1**2 + (1-w1)**2 * sd2**2 + 2*rho*w1*(1-w1)*sd1*sd2)

def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2

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
        ref_map = {0: 0, 1: 10, 2: 25, 3: 50, 4: 75, 5: 95}
        return ref_map[int(score)]

    elif agency == "s&p":
        return max(0, min(100, float(score)))

# -------------------------------
# APP TITLE
# -------------------------------
st.title("🌱 Sustainable Finance Portfolio Tool")

# -------------------------------
# SIDEBAR INPUTS
# -------------------------------
st.sidebar.header("Asset Information")

asset1_name = st.sidebar.text_input("Asset 1", "Asset A")
asset2_name = st.sidebar.text_input("Asset 2", "Asset B")

col1, col2 = st.sidebar.columns(2)

with col1:
    r1 = st.number_input("Return A (%)", 0.0, 100.0, 8.0)/100
    sd1 = st.number_input("Volatility A (%)", 0.0, 100.0, 15.0)/100
    agency1 = st.selectbox("Agency A", ["MSCI", "Sustainalytics", "Refinitiv", "S&P"])

with col2:
    r2 = st.number_input("Return B (%)", 0.0, 100.0, 10.0)/100
    sd2 = st.number_input("Volatility B (%)", 0.0, 100.0, 20.0)/100
    agency2 = st.selectbox("Agency B", ["MSCI", "Sustainalytics", "Refinitiv", "S&P"])

rho = st.sidebar.slider("Correlation", -1.0, 1.0, 0.2)
r_free = st.sidebar.number_input("Risk-free (%)", 0.0, 10.0, 2.0)/100

# -------------------------------
# GAMMA (FULL QUESTIONNAIRE)
# -------------------------------
st.header("1. Risk Preference")

mode = st.radio("Gamma input:", ["Manual", "Questionnaire"])

if mode == "Manual":
    gamma = st.slider("Gamma", -10.0, 10.0, 3.0)
else:
    q1 = st.slider("Risk attitude", 1, 5, 3)
    q2 = st.slider("Prefer steady returns", 1, 5, 3)
    q3 = st.slider("Reaction to loss", 1, 5, 3)
    q4 = st.slider("High-risk allocation", 1, 5, 3)
    q5 = st.slider("Guaranteed vs risky", 1, 5, 3)

    avg = np.mean([q1,q2,q3,q4,q5])

    if avg <= 1.5: gamma = 8
    elif avg <= 2.3: gamma = 4
    elif avg <= 3.2: gamma = 0
    elif avg <= 4.1: gamma = -4
    else: gamma = -8

    st.success(f"Gamma = {gamma}")

# -------------------------------
# ESG INPUT
# -------------------------------
st.header("2. ESG Scores")

method = st.radio("Input method", ["Overall", "E,S,G"])

def get_esg(asset, agency, prefix):
    if method == "Overall":
        if agency == "MSCI":
            val = st.selectbox(f"{asset} MSCI", ["CCC","B","BB","BBB","A","AA","AAA"], key=prefix)
        elif agency == "Refinitiv":
            val = st.slider(f"{asset} (0-5)", 0,5,3,key=prefix)
        else:
            val = st.number_input(f"{asset} score", key=prefix)
        return convert_to_100(val, agency)

    else:
        st.write(f"**{asset} ESG breakdown**")

        e = st.number_input(f"{asset} E", key=prefix+"e")
        s = st.number_input(f"{asset} S", key=prefix+"s")
        g = st.number_input(f"{asset} G", key=prefix+"g")

        we = st.slider("E weight",0,100,33,key=prefix+"we")
        ws = st.slider("S weight",0,100,33,key=prefix+"ws")
        wg = 100 - we - ws

        st.caption(f"G weight auto = {wg}")

        return (we/100)*convert_to_100(e,agency) + \
               (ws/100)*convert_to_100(s,agency) + \
               (wg/100)*convert_to_100(g,agency)

colA, colB = st.columns(2)

with colA:
    esg1 = get_esg(asset1_name, agency1, "a1")
with colB:
    esg2 = get_esg(asset2_name, agency2, "a2")

# -------------------------------
# ESG PREFERENCE
# -------------------------------
st.header("3. ESG Preference")

lambda_choice = st.select_slider("Preference",
["None","Small","Moderate","Strong"])

l_map = {"None":0,"Small":0.25,"Moderate":0.75,"Strong":1}
lambda_esg = l_map[lambda_choice]

esg_threshold = min(esg1,esg2) + lambda_esg*(max(esg1,esg2)-min(esg1,esg2))

# -------------------------------
# CALCULATIONS
# -------------------------------
weights = np.linspace(0,1,1000)

rets = portfolio_return(weights,r1,r2)
vols = portfolio_sd(weights,sd1,sd2,rho)
esgs = portfolio_esg(weights,esg1,esg2)

sharpes = np.where(vols>0,(rets-r_free)/vols,-np.inf)

idx_all = np.argmax(sharpes)

eligible = np.where(esgs>=esg_threshold)[0]

if len(eligible)==0:
    st.error("No ESG portfolios possible")
    st.stop()

idx_esg = eligible[np.argmax(sharpes[eligible])]

# -------------------------------
# RESULTS TABLES
# -------------------------------
st.header("4. Results")

df = pd.DataFrame({
"Metric":["Weight A","Weight B","Return","Risk","ESG","Sharpe"],
"No ESG":[
f"{weights[idx_all]*100:.2f}%",
f"{(1-weights[idx_all])*100:.2f}%",
f"{rets[idx_all]*100:.2f}%",
f"{vols[idx_all]*100:.2f}%",
f"{esgs[idx_all]:.2f}",
f"{sharpes[idx_all]:.3f}"
],
"With ESG":[
f"{weights[idx_esg]*100:.2f}%",
f"{(1-weights[idx_esg])*100:.2f}%",
f"{rets[idx_esg]*100:.2f}%",
f"{vols[idx_esg]*100:.2f}%",
f"{esgs[idx_esg]:.2f}",
f"{sharpes[idx_esg]:.3f}"
]
})

st.table(df)

# -------------------------------
# FINAL ALLOCATION
# -------------------------------
def allocation(ret, sd):
    if gamma>0 and sd>0:
        y = (ret-r_free)/(gamma*sd**2)
        y = min(max(y,0),1)
        return y,1-y
    return np.nan,np.nan

y_all, rf_all = allocation(rets[idx_all],vols[idx_all])
y_esg, rf_esg = allocation(rets[idx_esg],vols[idx_esg])

st.subheader("Final Allocation")

st.write(pd.DataFrame({
"":[ "Risky Portfolio","Risk-free"],
"No ESG":[f"{y_all*100:.1f}%",f"{rf_all*100:.1f}%"],
"With ESG":[f"{y_esg*100:.1f}%",f"{rf_esg*100:.1f}%"]
}))

# -------------------------------
# IMPACT
# -------------------------------
st.subheader("Impact of ESG")

st.write(pd.DataFrame({
"Change":[ "Return","Risk","ESG"],
"Value":[
f"{(rets[idx_esg]-rets[idx_all])*100:.2f} pp",
f"{(vols[idx_esg]-vols[idx_all])*100:.2f} pp",
f"{(esgs[idx_esg]-esgs[idx_all]):.2f}"
]
}))

# -------------------------------
# PLOTS (SEPARATE)
# -------------------------------

# Efficient frontier
fig1, ax = plt.subplots()

ax.plot(vols,rets)
ax.plot(vols[eligible],rets[eligible])

ax.scatter(vols[idx_all],rets[idx_all])
ax.scatter(vols[idx_esg],rets[idx_esg])

ax.set_xlabel("Risk")
ax.set_ylabel("Return")
ax.set_title("Efficient Frontier")

st.pyplot(fig1)

# ESG-Sharpe
fig2, ax2 = plt.subplots()

ax2.plot(esgs,sharpes)
ax2.axvline(esg_threshold)

ax2.set_xlabel("ESG")
ax2.set_ylabel("Sharpe")
ax2.set_title("ESG-Sharpe Frontier")

st.pyplot(fig2)
