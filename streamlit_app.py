import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.ticker import PercentFormatter

st.set_page_config(page_title="Sustainable Finance Portfolio Tool", layout="wide")

# ==========================================================
# HELPER / CALCULATION FUNCTIONS (unchanged logic)
# ==========================================================

def convert_to_100(score, agency):
    agency = agency.lower()
    if agency == "sustainalytics":
        score = float(score)
        if score >= 50:
            return 0.0
        converted = 100 - (score / 50) * 100
        return max(0.0, min(100.0, converted))
    elif agency == "msci":
        msci_map = {
            "ccc": 0.0, "b": 16.7, "bb": 33.4, "bbb": 50.1,
            "a": 66.8, "aa": 83.5, "aaa": 100.0
        }
        score = str(score).strip().lower()
        if score not in msci_map:
            raise ValueError("Invalid MSCI rating")
        return msci_map[score]
    elif agency == "refinitiv":
        score = int(float(score))
        refinitiv_map = {0: 0.0, 1: 10.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 95.0}
        if score not in refinitiv_map:
            raise ValueError("Invalid Refinitiv / LSEG score")
        return refinitiv_map[score]
    elif agency == "s&p":
        return max(0.0, min(100.0, float(score)))
    else:
        raise ValueError("Unknown agency.")


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
        w1 ** 2 * sd1 ** 2 +
        (1 - w1) ** 2 * sd2 ** 2 +
        2 * rho * w1 * (1 - w1) * sd1 * sd2
    )


def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2


def run_calculations(r1, r2, sd1, sd2, rho, r_free, gamma,
                     esg1_100, esg2_100, lambda_esg):
    esg1_1 = convert_100_to_1(esg1_100)
    esg2_1 = convert_100_to_1(esg2_100)

    weights = np.linspace(0, 1, 1000)
    returns, risks, esg_scores_100, sharpe_ratios = [], [], [], []

    for w in weights:
        port_ret = portfolio_return(w, r1, r2)
        port_sd = portfolio_sd(w, sd1, sd2, rho)
        port_esg_display = portfolio_esg(w, esg1_100, esg2_100)

        returns.append(port_ret)
        risks.append(port_sd)
        esg_scores_100.append(port_esg_display)

        sharpe = (port_ret - r_free) / port_sd if port_sd > 0 else -np.inf
        sharpe_ratios.append(sharpe)

    max_sharpe_index = np.argmax(sharpe_ratios)
    w1_tangency = weights[max_sharpe_index]
    w2_tangency = 1 - w1_tangency
    ret_tangency = returns[max_sharpe_index]
    sd_tangency = risks[max_sharpe_index]
    esg_tangency_100 = esg_scores_100[max_sharpe_index]

    esg_threshold = get_esg_threshold(lambda_esg, esg1_100, esg2_100)

    eligible_weights, eligible_returns, eligible_risks = [], [], []
    eligible_esg_scores, eligible_sharpes = [], []

    for i, w in enumerate(weights):
        if esg_scores_100[i] >= esg_threshold:
            eligible_weights.append(w)
            eligible_returns.append(returns[i])
            eligible_risks.append(risks[i])
            eligible_esg_scores.append(esg_scores_100[i])
            eligible_sharpes.append(
                (returns[i] - r_free) / risks[i] if risks[i] > 0 else -np.inf
            )

    if len(eligible_weights) == 0:
        return None, "No portfolios satisfy the ESG threshold."

    max_sharpe_esg_index = np.argmax(eligible_sharpes)
    w1_tangency_esg = eligible_weights[max_sharpe_esg_index]
    w2_tangency_esg = 1 - w1_tangency_esg
    ret_tangency_esg = eligible_returns[max_sharpe_esg_index]
    sd_tangency_esg = eligible_risks[max_sharpe_esg_index]
    esg_tangency_esg_100 = eligible_esg_scores[max_sharpe_esg_index]

    # Investor allocation
    if gamma > 0 and sd_tangency > 0:
        y_all_raw = (ret_tangency - r_free) / (gamma * (sd_tangency ** 2))
        y_all = min(max(y_all_raw, 0), 1)
        rf_all = 1 - y_all
    else:
        y_all = rf_all = np.nan

    if gamma > 0 and sd_tangency_esg > 0:
        y_esg_raw = (ret_tangency_esg - r_free) / (gamma * (sd_tangency_esg ** 2))
        y_esg = min(max(y_esg_raw, 0), 1)
        rf_esg = 1 - y_esg
    else:
        y_esg = rf_esg = np.nan

    result = dict(
        weights=weights, returns=returns, risks=risks,
        esg_scores_100=esg_scores_100, sharpe_ratios=sharpe_ratios,
        w1_tangency=w1_tangency, w2_tangency=w2_tangency,
        ret_tangency=ret_tangency, sd_tangency=sd_tangency,
        esg_tangency_100=esg_tangency_100,
        esg_threshold=esg_threshold,
        w1_tangency_esg=w1_tangency_esg, w2_tangency_esg=w2_tangency_esg,
        ret_tangency_esg=ret_tangency_esg, sd_tangency_esg=sd_tangency_esg,
        esg_tangency_esg_100=esg_tangency_esg_100,
        eligible_sharpes=eligible_sharpes,
        max_sharpe_esg_index=max_sharpe_esg_index,
        max_sharpe_index=max_sharpe_index,
        y_all=y_all, rf_all=rf_all, y_esg=y_esg, rf_esg=rf_esg,
    )
    return result, None


def build_frontier_figure(res, r1, r2, sd1, sd2, rho, r_free,
                           esg1_100, esg2_100, asset1_name, asset2_name):
    weights_plot = np.linspace(-1.0, 2.0, 1200)
    returns_frontier = [portfolio_return(w, r1, r2) for w in weights_plot]
    sds_frontier = [portfolio_sd(w, sd1, sd2, rho) for w in weights_plot]
    esg_frontier = [portfolio_esg(w, esg1_100, esg2_100) for w in weights_plot]

    sds_frontier_esg, returns_frontier_esg = [], []
    for i in range(len(weights_plot)):
        if esg_frontier[i] >= res["esg_threshold"]:
            sds_frontier_esg.append(sds_frontier[i])
            returns_frontier_esg.append(returns_frontier[i])

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.plot(sds_frontier, returns_frontier, color="blue", linewidth=2,
            label="Frontier without ESG constraint")
    ax.plot(sds_frontier_esg, returns_frontier_esg, color="green", linewidth=2,
            label="Frontier with ESG constraint")

    sd_max = max(max(sds_frontier), max(sds_frontier_esg) if sds_frontier_esg else 0,
                 res["sd_tangency"], res["sd_tangency_esg"]) * 1.05
    sd_range = np.linspace(0, sd_max, 300)

    cml_all = r_free + ((res["ret_tangency"] - r_free) / res["sd_tangency"]) * sd_range
    cml_esg = r_free + ((res["ret_tangency_esg"] - r_free) / res["sd_tangency_esg"]) * sd_range

    ax.plot(sd_range, cml_all, linestyle="--", color="blue", linewidth=1.8,
            label="CML without ESG constraint")
    ax.plot(sd_range, cml_esg, linestyle="--", color="green", linewidth=1.8,
            label="CML with ESG constraint")

    ax.scatter(res["sd_tangency"], res["ret_tangency"], color="blue", marker="*",
               s=200, edgecolors="black", linewidths=0.8, zorder=5,
               label="Optimal risky portfolio (no ESG constraint)")
    ax.scatter(res["sd_tangency_esg"], res["ret_tangency_esg"], color="green", marker="*",
               s=200, edgecolors="black", linewidths=0.8, zorder=6,
               label="Optimal risky portfolio (with ESG constraint)")

    ax.annotate("No ESG", (res["sd_tangency"], res["ret_tangency"]),
                textcoords="offset points", xytext=(-28, -14), fontsize=9, color="blue")
    ax.annotate("ESG", (res["sd_tangency_esg"], res["ret_tangency_esg"]),
                textcoords="offset points", xytext=(8, 8), fontsize=9, color="green")

    ax.scatter(0, r_free, color="black", marker="s", s=90, label="Risk-free asset")

    frontier_x = sds_frontier + sds_frontier_esg + [0]
    frontier_y = returns_frontier + returns_frontier_esg + [r_free]
    ax.set_xlim(0, max(frontier_x) * 1.02)
    ax.set_ylim(min(frontier_y) - 0.01, max(frontier_y) + 0.01)

    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel("Risk (Standard Deviation)")
    ax.set_ylabel("Expected Return")
    ax.set_title("Efficient Frontier with ESG Constraint")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def build_esg_sharpe_figure(res, r1, r2, sd1, sd2, rho, r_free, esg1_100, esg2_100):
    weights_esg_plot = np.linspace(0, 1, 400)
    esg_vals, sharpe_vals = [], []
    for w in weights_esg_plot:
        port_ret = portfolio_return(w, r1, r2)
        port_sd = portfolio_sd(w, sd1, sd2, rho)
        port_esg = portfolio_esg(w, esg1_100, esg2_100)
        sharpe = (port_ret - r_free) / port_sd if port_sd > 0 else -np.inf
        esg_vals.append(port_esg)
        sharpe_vals.append(sharpe)

    tangency_sharpe = (res["ret_tangency"] - r_free) / res["sd_tangency"] if res["sd_tangency"] > 0 else -np.inf
    tangency_esg_sharpe = (res["ret_tangency_esg"] - r_free) / res["sd_tangency_esg"] if res["sd_tangency_esg"] > 0 else -np.inf

    fig2, ax2 = plt.subplots(figsize=(9, 6))
    ax2.plot(esg_vals, sharpe_vals, linewidth=2, color="red", label="ESG-Sharpe Ratio Frontier")

    ax2.scatter(res["esg_tangency_100"], tangency_sharpe, marker="*", s=220,
                color="blue", edgecolors="black", linewidths=0.8, zorder=5,
                label="Tangency Portfolio (All)")
    ax2.scatter(res["esg_tangency_esg_100"], tangency_esg_sharpe, marker="*", s=220,
                color="green", edgecolors="black", linewidths=0.8, zorder=6,
                label="Tangency Portfolio (ESG)")

    ax2.annotate("All", (res["esg_tangency_100"], tangency_sharpe),
                 textcoords="offset points", xytext=(-18, -12), fontsize=9, color="blue")
    ax2.annotate("ESG", (res["esg_tangency_esg_100"], tangency_esg_sharpe),
                 textcoords="offset points", xytext=(8, 8), fontsize=9, color="green")

    ax2.set_xlabel("Portfolio ESG Score (0-100)")
    ax2.set_ylabel("Sharpe Ratio")
    ax2.set_title("ESG-Sharpe Ratio Frontier")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    plt.tight_layout()
    return fig2


# ==========================================================
# STREAMLIT UI
# ==========================================================

st.title("Sustainable Finance Portfolio Tool")
st.markdown(
    "Compare two investments based on **financial performance**, **risk**, and **ESG preferences**."
)

# ---------- SIDEBAR: all inputs ----------
with st.sidebar:
    st.header("Inputs")

    # --- ESG method ---
    st.subheader("ESG Information Method")
    esg_method = st.radio(
        "How would you like to enter ESG information?",
        ["Overall ESG score", "Separate E, S, G scores"],
        help="Choose based on what data you have available for both assets."
    )
    use_separate_scores = (esg_method == "Separate E, S, G scores")

    pillar_weights = None
    if use_separate_scores:
        st.markdown("**ESG Pillar Weights** (must sum to 100)")
        w_e = st.number_input("Environmental weight (%)", 0.0, 100.0, 33.34, step=0.01)
        w_s = st.number_input("Social weight (%)", 0.0, 100.0, 33.33, step=0.01)
        w_g = st.number_input("Governance weight (%)", 0.0, 100.0, 33.33, step=0.01)
        pillar_sum = w_e + w_s + w_g
        if abs(pillar_sum - 100) > 0.1:
            st.warning(f"Weights sum to {pillar_sum:.2f}%, not 100%. Please adjust.")
        pillar_weights = (w_e, w_s, w_g)

    st.divider()

    # --- Asset names ---
    st.subheader("Asset Names")
    asset1_name = st.text_input("Asset 1 name", value="Asset 1",
                                placeholder="e.g. Apple, FTSE 100 ETF")
    asset2_name = st.text_input("Asset 2 name", value="Asset 2",
                                placeholder="e.g. Microsoft, S&P 500 ETF")

    st.divider()

    # --- Financial inputs ---
    st.subheader("Financial Information")
    col1, col2 = st.columns(2)
    with col1:
        r1_pct = st.number_input(f"{asset1_name} expected return (%)", value=8.0, step=0.1)
        sd1_pct = st.number_input(f"{asset1_name} volatility (%)", value=15.0, min_value=0.01, step=0.1)
    with col2:
        r2_pct = st.number_input(f"{asset2_name} expected return (%)", value=10.0, step=0.1)
        sd2_pct = st.number_input(f"{asset2_name} volatility (%)", value=20.0, min_value=0.01, step=0.1)

    r1, r2 = r1_pct / 100, r2_pct / 100
    sd1, sd2 = sd1_pct / 100, sd2_pct / 100

    st.divider()

    # --- Market inputs ---
    st.subheader("Market Information")
    rho = st.slider("Correlation coefficient (rho)", -1.0, 1.0, 0.3, step=0.01)
    r_free_pct = st.number_input("Risk-free rate (%)", value=2.0, step=0.1)
    r_free = r_free_pct / 100

    st.divider()

    # --- Risk aversion ---
    st.subheader("Risk Aversion (Gamma)")
    gamma_mode = st.radio("Do you know your gamma?",
                          ["I know my gamma", "Help me find it (questionnaire)"])

    if gamma_mode == "I know my gamma":
        gamma = st.slider(
            "Gamma (negative = risk-loving, 0 = neutral, positive = risk-averse)",
            -10.0, 10.0, 2.0, step=0.1
        )
    else:
        st.markdown("Answer the 5 questions below:")
        q_labels = [
            "1 = Avoid risk · 5 = Seek high risk",
            "1 = Strongly agree (prefer slow/steady) · 5 = Strongly disagree",
            "1 = Sell everything · 5 = Buy more on the dip",
            "1 = Very little in high-risk · 5 = All of it",
            "1 = Strongly agree (prefer guaranteed) · 5 = Strongly disagree",
        ]
        q_titles = [
            "Q1. General attitude to investment risk",
            "Q2. Prefer slow but steady growth",
            "Q3. Portfolio drops 20% — your reaction?",
            "Q4. How much in a high-risk investment?",
            "Q5. Small guaranteed vs large uncertain return",
        ]
        scores = []
        for title, label in zip(q_titles, q_labels):
            scores.append(st.slider(title, 1, 5, 3, help=label))

        avg = sum(scores) / len(scores)
        if avg <= 1.5:
            gamma, label = 8, "Very Cautious"
        elif avg <= 2.3:
            gamma, label = 4, "Cautious"
        elif avg <= 3.2:
            gamma, label = 0, "Moderate / Risk-Neutral"
        elif avg <= 4.1:
            gamma, label = -4, "Adventurous"
        else:
            gamma, label = -8, "Very Adventurous / Risk-Loving"
        st.info(f"Your profile: **{label}** (gamma = {gamma})")

    st.divider()

    # --- ESG Scores ---
    st.subheader("ESG Scores")

    AGENCY_OPTIONS = ["Sustainalytics", "Refinitiv (LSEG)", "MSCI", "S&P Dow Jones"]
    AGENCY_KEYS = ["sustainalytics", "refinitiv", "msci", "s&p"]

    def esg_score_widget(asset_name, key_prefix):
        agency_label = st.selectbox(
            f"Rating agency for {asset_name}",
            AGENCY_OPTIONS,
            key=f"{key_prefix}_agency"
        )
        agency = AGENCY_KEYS[AGENCY_OPTIONS.index(agency_label)]

        if use_separate_scores:
            scores_100 = {}
            for pillar in ["Environmental", "Social", "Governance"]:
                scores_100[pillar] = esg_input_for_agency(
                    agency, f"{pillar} score for {asset_name}", f"{key_prefix}_{pillar}"
                )
            if any(v is None for v in scores_100.values()):
                return None
            we, ws, wg = pillar_weights
            overall_100 = (
                (we / 100) * scores_100["Environmental"] +
                (ws / 100) * scores_100["Social"] +
                (wg / 100) * scores_100["Governance"]
            )
            st.caption(f"Combined ESG score (0-100): **{overall_100:.2f}**")
            return overall_100
        else:
            return esg_input_for_agency(
                agency, f"Overall ESG score for {asset_name}", f"{key_prefix}_overall"
            )

    def esg_input_for_agency(agency, label, key):
        if agency == "msci":
            msci_options = ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"]
            rating = st.selectbox(label, msci_options, index=3, key=key)
            msci_map = {"CCC": 0.0, "B": 16.7, "BB": 33.4, "BBB": 50.1,
                        "A": 66.8, "AA": 83.5, "AAA": 100.0}
            val = msci_map[rating]
            st.caption(f"Converted to 0-100 scale: **{val:.1f}**")
            return val
        elif agency == "refinitiv":
            raw = st.selectbox(label + " (0-5)", [0, 1, 2, 3, 4, 5], index=3, key=key)
            refinitiv_map = {0: 0.0, 1: 10.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 95.0}
            val = refinitiv_map[raw]
            st.caption(f"Converted to 0-100 scale: **{val:.1f}**")
            return val
        elif agency == "sustainalytics":
            raw = st.number_input(label + " (0 = best, 50+ = worst)", 0.0, 100.0,
                                  20.0, step=0.1, key=key)
            val = max(0.0, 100 - (min(raw, 50) / 50) * 100)
            st.caption(f"Converted to 0-100 scale: **{val:.1f}**")
            return val
        else:  # s&p
            val = st.number_input(label + " (0-100)", 0.0, 100.0, 50.0, step=0.1, key=key)
            return val

    esg1_100 = esg_score_widget(asset1_name, "a1")
    esg2_100 = esg_score_widget(asset2_name, "a2")

    st.divider()

    # --- ESG preference ---
    st.subheader("ESG Preference (Lambda)")
    lambda_choice = st.radio(
        "Which statement best describes you?",
        [
            "I would not accept a lower return for better ESG (lambda = 0)",
            "I would accept a small reduction (lambda = 0.25)",
            "I would accept a moderate reduction (lambda = 0.75)",
            "I would accept a significant reduction for strong ESG (lambda = 1)",
        ]
    )
    lambda_map = {0: 0.0, 1: 0.25, 2: 0.75, 3: 1.0}
    lambda_esg = lambda_map[[
        "I would not accept a lower return for better ESG (lambda = 0)",
        "I would accept a small reduction (lambda = 0.25)",
        "I would accept a moderate reduction (lambda = 0.75)",
        "I would accept a significant reduction for strong ESG (lambda = 1)",
    ].index(lambda_choice)]

    st.divider()
    run_button = st.button("Run Analysis", type="primary", use_container_width=True)

# ==========================================================
# MAIN AREA: Results
# ==========================================================

if not run_button:
    st.info("Fill in your inputs in the sidebar, then click **Run Analysis**.")
    st.stop()

# Validate pillar weights
if use_separate_scores and abs((w_e + w_s + w_g) - 100) > 0.1:
    st.error("ESG pillar weights must sum to 100. Please fix in the sidebar.")
    st.stop()

if esg1_100 is None or esg2_100 is None:
    st.error("Please complete all ESG score inputs.")
    st.stop()

# Run
res, err = run_calculations(
    r1, r2, sd1, sd2, rho, r_free, gamma,
    esg1_100, esg2_100, lambda_esg
)

if err:
    st.error(f"Calculation error: {err}")
    st.stop()

# ---------- INPUTS SUMMARY ----------
st.header("Your Inputs Summary")
inputs_df = pd.DataFrame({
    "Item": [
        "ESG preference strength (lambda)",
        "Minimum ESG score (ESG-constrained set)",
        "Risk-free rate",
        "Risk aversion (gamma)"
    ],
    "Value": [
        f"{lambda_esg:.2f}",
        f"{res['esg_threshold']:.2f}",
        f"{r_free * 100:.2f}%",
        f"{gamma:.2f}"
    ]
})
st.dataframe(inputs_df, use_container_width=True, hide_index=True)

# ---------- PORTFOLIO COMPARISON ----------
st.header("Portfolio Comparison")
portfolio_df = pd.DataFrame({
    "Metric": [
        f"{asset1_name} weight",
        f"{asset2_name} weight",
        "Expected return",
        "Risk (standard deviation)",
        "Portfolio ESG score",
        "Sharpe ratio",
    ],
    "Optimal (no ESG constraint)": [
        f"{res['w1_tangency'] * 100:.2f}%",
        f"{res['w2_tangency'] * 100:.2f}%",
        f"{res['ret_tangency'] * 100:.2f}%",
        f"{res['sd_tangency'] * 100:.2f}%",
        f"{res['esg_tangency_100']:.2f}",
        f"{res['sharpe_ratios'][res['max_sharpe_index']]:.4f}",
    ],
    "Optimal (with ESG constraint)": [
        f"{res['w1_tangency_esg'] * 100:.2f}%",
        f"{res['w2_tangency_esg'] * 100:.2f}%",
        f"{res['ret_tangency_esg'] * 100:.2f}%",
        f"{res['sd_tangency_esg'] * 100:.2f}%",
        f"{res['esg_tangency_esg_100']:.2f}",
        f"{res['eligible_sharpes'][res['max_sharpe_esg_index']]:.4f}",
    ]
})
st.dataframe(portfolio_df, use_container_width=True, hide_index=True)

# ---------- INVESTOR ALLOCATION ----------
st.header("Investor Allocation")
alloc_df = pd.DataFrame({
    "Allocation": ["Weight in optimal risky portfolio", "Weight in risk-free asset"],
    "No ESG constraint": [
        f"{res['y_all'] * 100:.2f}%" if not np.isnan(res['y_all']) else "N/A",
        f"{res['rf_all'] * 100:.2f}%" if not np.isnan(res['rf_all']) else "N/A",
    ],
    "With ESG constraint": [
        f"{res['y_esg'] * 100:.2f}%" if not np.isnan(res['y_esg']) else "N/A",
        f"{res['rf_esg'] * 100:.2f}%" if not np.isnan(res['rf_esg']) else "N/A",
    ]
})
st.dataframe(alloc_df, use_container_width=True, hide_index=True)
st.caption(
    "Note: We suggest investing 100% into the optimal risky portfolio "
    "(i.e. no allocation to the risk-free asset)."
)

# ---------- IMPACT OF ESG CONSTRAINT ----------
st.header("Impact of Applying the ESG Constraint")
impact_df = pd.DataFrame({
    "Change": ["Expected return change", "Risk change", "Portfolio ESG score change"],
    "Value": [
        f"{(res['ret_tangency_esg'] - res['ret_tangency']) * 100:.2f} percentage points",
        f"{(res['sd_tangency_esg'] - res['sd_tangency']) * 100:.2f} percentage points",
        f"{(res['esg_tangency_esg_100'] - res['esg_tangency_100']):.2f} points",
    ]
})
st.dataframe(impact_df, use_container_width=True, hide_index=True)
st.caption("All changes = ESG-constrained value minus non-ESG-constrained value.")

if res["esg_tangency_100"] >= res["esg_threshold"]:
    st.info(
        "The unconstrained optimal portfolio already satisfies the ESG requirement, "
        "so the ESG constraint does not materially change the optimal risky portfolio."
    )
else:
    st.info(
        "Applying your ESG preferences excludes some portfolio combinations, "
        "so the ESG-constrained optimal portfolio differs from the unconstrained one."
    )

# ---------- CHARTS ----------
st.header("Charts")

tab1, tab2 = st.tabs(["Efficient Frontier", "ESG-Sharpe Frontier"])

with tab1:
    fig1 = build_frontier_figure(
        res, r1, r2, sd1, sd2, rho, r_free,
        esg1_100, esg2_100, asset1_name, asset2_name
    )
    st.pyplot(fig1)
    st.caption(
        "The star markers indicate the optimal risky portfolio (highest Sharpe ratio) "
        "before and after applying the ESG requirement. If the two stars do not overlap, "
        "your ESG preferences change the optimal portfolio."
    )

with tab2:
    fig2 = build_esg_sharpe_figure(
        res, r1, r2, sd1, sd2, rho, r_free, esg1_100, esg2_100
    )
    st.pyplot(fig2)
    st.caption(
        "Blue star: highest Sharpe ratio overall. "
        "Green star: highest Sharpe ratio among portfolios meeting your ESG preference. "
        "The gap between stars shows the ESG-return trade-off."
    )
