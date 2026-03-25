import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.ticker import PercentFormatter

st.set_page_config(page_title="Sustainable Finance Portfolio Tool", layout="wide")

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def convert_100_to_1(score_100):
    return score_100 / 100


def get_esg_threshold(lambda_esg, esg1_100, esg2_100):
    esg_min = min(esg1_100, esg2_100)
    esg_max = max(esg1_100, esg2_100)
    return esg_min + lambda_esg * (esg_max - esg_min)


def portfolio_return(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2


def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(
        w1**2 * sd1**2 +
        (1 - w1)**2 * sd2**2 +
        2 * rho * w1 * (1 - w1) * sd1 * sd2
    )


def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2


# ==========================================================
# CORE CALCULATIONS
# ==========================================================

def run_calculations(r1, r2, sd1, sd2, rho, r_free, gamma,
                     esg1_100, esg2_100, lambda_esg):

    weights = np.linspace(0, 1, 1000)
    returns, risks, esg_scores_100, sharpe_ratios = [], [], [], []

    for w in weights:
        ret = portfolio_return(w, r1, r2)
        sd = portfolio_sd(w, sd1, sd2, rho)
        esg = portfolio_esg(w, esg1_100, esg2_100)

        returns.append(ret)
        risks.append(sd)
        esg_scores_100.append(esg)

        sharpe = (ret - r_free) / sd if sd > 0 else -np.inf
        sharpe_ratios.append(sharpe)

    max_idx = np.argmax(sharpe_ratios)

    esg_threshold = get_esg_threshold(lambda_esg, esg1_100, esg2_100)

    eligible = [
        i for i in range(len(weights))
        if esg_scores_100[i] >= esg_threshold
    ]

    if not eligible:
        return None, "No portfolios satisfy ESG constraint"

    esg_sharpes = [
        (returns[i] - r_free) / risks[i] if risks[i] > 0 else -np.inf
        for i in eligible
    ]

    best_esg_idx = eligible[np.argmax(esg_sharpes)]

    def alloc(ret, sd):
        if gamma > 0 and sd > 0:
            y = (ret - r_free) / (gamma * sd**2)
            y = min(max(y, 0), 1)
            return y, 1 - y
        return np.nan, np.nan

    y_all, rf_all = alloc(returns[max_idx], risks[max_idx])
    y_esg, rf_esg = alloc(returns[best_esg_idx], risks[best_esg_idx])

    return dict(
        weights=weights,
        returns=returns,
        risks=risks,
        esg_scores_100=esg_scores_100,
        sharpe_ratios=sharpe_ratios,

        max_sharpe_index=max_idx,
        max_sharpe_esg_index=eligible.index(best_esg_idx),

        w1_tangency=weights[max_idx],
        w2_tangency=1 - weights[max_idx],
        ret_tangency=returns[max_idx],
        sd_tangency=risks[max_idx],
        esg_tangency_100=esg_scores_100[max_idx],

        w1_tangency_esg=weights[best_esg_idx],
        w2_tangency_esg=1 - weights[best_esg_idx],
        ret_tangency_esg=returns[best_esg_idx],
        sd_tangency_esg=risks[best_esg_idx],
        esg_tangency_esg_100=esg_scores_100[best_esg_idx],

        eligible_sharpes=esg_sharpes,
        esg_threshold=esg_threshold,

        y_all=y_all, rf_all=rf_all,
        y_esg=y_esg, rf_esg=rf_esg
    ), None


# ==========================================================
# UI
# ==========================================================

st.title("Sustainable Finance Portfolio Tool")

with st.sidebar:

    st.header("Inputs")

    esg_method = st.radio(
        "ESG Input Method",
        ["Overall ESG score", "Separate E, S, G scores"]
    )

    use_separate_scores = esg_method == "Separate E, S, G scores"

    pillar_weights = None

    if use_separate_scores:
        w_e = st.number_input("E weight", 0.0, 100.0, 33.3)
        w_s = st.number_input("S weight", 0.0, 100.0, 33.3)
        w_g = st.number_input("G weight", 0.0, 100.0, 33.4)
        pillar_weights = (w_e, w_s, w_g)

    asset1_name = st.text_input("Asset 1", "Asset 1")
    asset2_name = st.text_input("Asset 2", "Asset 2")

    r1 = st.number_input("Return 1 (%)", 8.0) / 100
    r2 = st.number_input("Return 2 (%)", 10.0) / 100

    sd1 = st.number_input("Volatility 1 (%)", 15.0) / 100
    sd2 = st.number_input("Volatility 2 (%)", 20.0) / 100

    rho = st.slider("Correlation", -1.0, 1.0, 0.3)

    r_free = st.number_input("Risk-free (%)", 2.0) / 100
    gamma = st.slider("Gamma", -10.0, 10.0, 2.0)

    esg1_100 = st.number_input("ESG 1", 50.0)
    esg2_100 = st.number_input("ESG 2", 60.0)

    lambda_esg = st.selectbox("Lambda", [0.0, 0.25, 0.75, 1.0])

    run_button = st.button("Run Analysis")


# ==========================================================
# MAIN
# ==========================================================

if not run_button:
    st.stop()

# FIXED VALIDATION
if use_separate_scores:
    if pillar_weights is None:
        st.error("Missing ESG weights")
        st.stop()

    w_e, w_s, w_g = pillar_weights

    if abs((w_e + w_s + w_g) - 100) > 0.1:
        st.error("Weights must sum to 100")
        st.stop()

res, err = run_calculations(
    r1, r2, sd1, sd2, rho, r_free, gamma,
    esg1_100, esg2_100, lambda_esg
)

if err:
    st.error(err)
    st.stop()

st.write("## Portfolio Comparison")

st.dataframe(pd.DataFrame({
    "Metric": ["Return", "Risk", "ESG"],
    "No ESG": [
        res["ret_tangency"],
        res["sd_tangency"],
        res["esg_tangency_100"]
    ],
    "With ESG": [
        res["ret_tangency_esg"],
        res["sd_tangency_esg"],
        res["esg_tangency_esg_100"]
    ]
}))


# ==========================================================
# GRAPHS (UNCHANGED)
# ==========================================================

def build_frontier_figure():
    fig, ax = plt.subplots()

    ax.plot(res["risks"], res["returns"])

    ax.scatter(res["sd_tangency"], res["ret_tangency"])
    ax.scatter(res["sd_tangency_esg"], res["ret_tangency_esg"])

    ax.set_xlabel("Risk")
    ax.set_ylabel("Return")

    return fig


def build_esg_sharpe():
    fig, ax = plt.subplots()

    ax.scatter(res["esg_scores_100"], res["sharpe_ratios"])

    return fig


st.pyplot(build_frontier_figure())
st.pyplot(build_esg_sharpe())
