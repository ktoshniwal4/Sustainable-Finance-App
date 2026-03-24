#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display

def get_number(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = float(input(prompt).strip())
            if minimum is not None and value < minimum:
                print(f"Please enter a value of at least {minimum}.")
                continue
            if maximum is not None and value > maximum:
                print(f"Please enter a value of at most {maximum}.")
                continue
            return value
        except ValueError:
            print("That entry is not valid. Please enter a number and try again.")


def get_choice(prompt, valid_choices):
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_choices:
            return choice
        print(f"That entry is not valid. Please enter one of: {', '.join(valid_choices)}")

def show_table(df):
    try:
        from IPython import get_ipython
        ip = get_ipython()

        # If running in a Jupyter notebook, use rich HTML display
        if ip is not None and "ZMQInteractiveShell" in str(type(ip)):
            display(df.style.hide(axis="index"))
        else:
            # Fallback for normal Python/PyCharm console
            print(df.to_string(index=False))
    except Exception:
        print(df.to_string(index=False))

def convert_to_100(score, agency):
    agency = agency.lower()

    if agency == "sustainalytics":
        score = float(score)

        # 0 is best, 50 or above is treated as worst in this model
        if score >= 50:
            return 0.0

        converted = 100 - (score / 50) * 100
        return max(0.0, min(100.0, converted))

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
        refinitiv_map = {
            0: 0.0,
            1: 10.0,
            2: 25.0,
            3: 50.0,
            4: 75.0,
            5: 95.0
        }
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


def ask_agency(asset_name):
    print(f"\nWhat rating agency are the ESG scores for {asset_name} from?")
    print("1. Sustainalytics")
    print("2. Refinitiv (LSEG)")
    print("3. MSCI")
    print("4. S&P Dow Jones")

    choice = get_choice("Enter 1, 2, 3, or 4: ", ["1", "2", "3", "4"])

    if choice == "1":
        return "sustainalytics"
    elif choice == "2":
        return "refinitiv"
    elif choice == "3":
        return "msci"
    else:
        return "s&p"


def ask_esg_input_method():
    print("=" * 60)
    print("ESG INFORMATION METHOD")
    print("=" * 60)
    print("How would you like to enter ESG information for your two assets?")
    print("1. I know the overall ESG score for both assets")
    print("2. I know the separate Environmental, Social, and Governance scores for both assets")
    print("\nPlease choose the option that matches the information you have available for both assets.")

    return get_choice("Enter 1 or 2: ", ["1", "2"])


def ask_pillar_weights():
    print("\nYou chose to enter separate Environmental, Social, and Governance scores.")
    print("Please now choose how much importance you would like to give to each ESG pillar.")
    print("These weights will be used when calculating the overall ESG score for each asset.")
    print("The three percentages must add up to 100.")

    while True:
        w_e = get_number("Weight for Environmental (%): ", 0, 100)
        w_s = get_number("Weight for Social (%): ", 0, 100)
        w_g = get_number("Weight for Governance (%): ", 0, 100)

        if abs((w_e + w_s + w_g) - 100) < 0.001:
            return w_e, w_s, w_g

        print("Those weights do not add up to 100. Please try again.")


def get_valid_esg_input(prompt, agency):
    while True:
        raw_value = input(prompt).strip()

        try:
            converted = convert_to_100(raw_value, agency)
            return raw_value, converted

        except ValueError:
            if agency == "msci":
                print("That ESG rating is not valid. Please re-enter it using one of: CCC, B, BB, BBB, A, AA, AAA.")
            elif agency == "refinitiv":
                print("That ESG score is not valid. Please re-enter an integer from 0 to 5.")
            elif agency == "sustainalytics":
                print("That ESG score is not valid. Please re-enter a number for Sustainalytics.")
            elif agency == "s&p":
                print("That ESG score is not valid. Please re-enter a number from 0 to 100.")
            else:
                print("That ESG score is not valid. Please try again.")


def ask_esg_score(asset_name, use_separate_scores, weights=None):
    agency = ask_agency(asset_name)

    if use_separate_scores:
        print(f"\nPlease enter the separate ESG scores for {asset_name}.")
        print(f"You selected {agency.upper()} as the ESG rating provider.")

        if agency == "sustainalytics":
            print("Enter the Sustainalytics scores (range: 0-50+):")

        elif agency == "refinitiv":
            print("Enter the Refinitiv (LSEG) scores (range: 0-5):")

        elif agency == "msci":
            print("Enter the MSCI ratings (CCC, B, BB, BBB, A, AA, AAA):")

        elif agency == "s&p":
            print("Enter the S&P ESG scores (range: 0-100):")

        _, e_100 = get_valid_esg_input("Environmental score: ", agency)
        _, s_100 = get_valid_esg_input("Social score: ", agency)
        _, g_100 = get_valid_esg_input("Governance score: ", agency)

        w_e, w_s, w_g = weights
        overall_100 = (w_e / 100) * e_100 + (w_s / 100) * s_100 + (w_g / 100) * g_100
        overall_1 = convert_100_to_1(overall_100)

        print(f"\n{asset_name} ESG results:")
        print(f"Environmental score on a 0-100 scale: {e_100:.2f}")
        print(f"Social score on a 0-100 scale: {s_100:.2f}")
        print(f"Governance score on a 0-100 scale: {g_100:.2f}")
        print(f"Combined ESG score on a 0-100 scale: {overall_100:.2f}")

        return overall_100, overall_1

    else:
        print(f"\nPlease enter the overall ESG score for {asset_name}.")
        print(f"You selected {agency.upper()} as the ESG rating provider.")

        if agency == "sustainalytics":
            print("Enter the Sustainalytics score (range: 0-50+):")

        elif agency == "refinitiv":
            print("Enter the Refinitiv (LSEG) score (range: 0-5):")

        elif agency == "msci":
            print("Enter the MSCI rating (CCC, B, BB, BBB, A, AA, AAA):")

        elif agency == "s&p":
            print("Enter the S&P ESG score (range: 0-100):")

        _, overall_100 = get_valid_esg_input("Overall ESG score: ", agency)
        overall_1 = convert_100_to_1(overall_100)

        print(f"\n{asset_name} ESG results:")
        print(f"Overall ESG score on a 0-100 scale: {overall_100:.2f}")

        return overall_100, overall_1


def ask_lambda():
    print("\nWhich statement best describes you?")
    print("1. I would not accept a lower return for better ESG.")
    print("2. I would accept a small reduction in return for better ESG.")
    print("3. I would accept a moderate reduction in return for better ESG.")
    print("4. I would accept a significant reduction in return for strong ESG alignment.")

    choice = get_choice("Enter 1, 2, 3, or 4: ", ["1", "2", "3", "4"])

    lambda_map = {
        "1": 0.0,
        "2": 0.25,
        "3": 0.75,
        "4": 1.0
    }

    return lambda_map[choice]


def get_esg_threshold(lambda_esg, esg1_100, esg2_100):
    esg_min = min(esg1_100, esg2_100)
    esg_max = max(esg1_100, esg2_100)
    return esg_min + lambda_esg * (esg_max - esg_min)


def get_int_input(prompt, valid_range):
    while True:
        try:
            value = int(input(prompt).strip())
            if value in valid_range:
                return value
            print(
                f"That entry is not valid. Please enter a whole number from {min(valid_range)} to {max(valid_range)}.")
        except ValueError:
            print("That entry is not valid. Please enter a whole number.")


def ask_gamma():
    print("\nYour risk preference affects how much portfolio risk you are comfortable taking.")
    print("If you already know your risk aversion parameter gamma, enter it below.")
    print("A positive gamma means risk-averse, 0 means risk-neutral, and a negative gamma means risk-loving.")
    print("If you do not know it, type 'not sure'. This will lead you to a short questionnaire.")

    while True:
        response = input(
            "Please enter your gamma value "
            "(for example, around -10 to 10: negative = risk-loving, 0 = risk-neutral, positive = risk-averse), "
            "or type 'not sure' if you do not know your value: "
        ).strip().lower()

        if response == "not sure":
            scores = []

            # Q1
            print("Q1. How would you describe your general attitude")
            print(" towards investment risk?")
            print(" 1. I avoid risk wherever possible")
            print(" 2. I prefer low-risk, steady options")
            print(" 3. I am comfortable with moderate risk")
            print(" 4. I am generally willing to take on risk for higher returns")
            print(" 5. I actively seek high-risk, high-reward opportunities")
            scores.append(get_int_input(" Your answer (1-5): ", range(1, 6)))

            # Q2
            print('Q2. "I prefer an investment that grows slowly but')
            print(' steadily, even if it means lower overall returns."')
            print(" 1. I strongly agree")
            print(" 2. I tend to agree")
            print(" 3. I am in between")
            print(" 4. I tend to disagree")
            print(" 5. I strongly disagree")
            scores.append(get_int_input(" Your answer (1-5): ", range(1, 6)))

            # Q3
            print("Q3. Your portfolio drops 20% in value over three months.")
            print(" What is your most likely reaction?")
            print(" 1. Sell everything immediately to stop further losses")
            print(" 2. Sell some holdings to reduce exposure")
            print(" 3. Do nothing and wait for recovery")
            print(" 4. Review the portfolio but stay the course")
            print(" 5. See it as a buying opportunity and invest more")
            scores.append(get_int_input(" Your answer (1-5): ", range(1, 6)))

            # Q4
            print("Q4. If you had money to invest, how much would you")
            print(" be comfortable placing in a high-risk, high-reward")
            print(" investment?")
            print(" 1. Very little, if any")
            print(" 2. Less than a quarter")
            print(" 3. Around half")
            print(" 4. More than half")
            print(" 5. All of it")
            scores.append(get_int_input(" Your answer (1-5): ", range(1, 6)))

            # Q5
            print('Q5. "I would always prefer a small but guaranteed')
            print(' return over a larger but uncertain one."')
            print(" 1. I strongly agree")
            print(" 2. I tend to agree")
            print(" 3. I am in between")
            print(" 4. I tend to disagree")
            print(" 5. I strongly disagree")
            scores.append(get_int_input(" Your answer (1-5): ", range(1, 6)))

            avg = sum(scores) / len(scores)

            # Adjusted to fit your model's existing 0-1 gamma scale
            if avg <= 1.5:
                gamma = 8
                label = "Very Cautious"
            elif avg <= 2.3:
                gamma = 4
                label = "Cautious"
            elif avg <= 3.2:
                gamma = 0
                label = "Moderate / Risk-Neutral"
            elif avg <= 4.1:
                gamma = -4
                label = "Adventurous / Somewhat Risk-Loving"
            else:
                gamma = -8
                label = "Very Adventurous / Risk-Loving"

            print("\nQuestionnaire complete.")
            print(f"Your risk profile: {label} (gamma = {gamma})")
            return gamma

        try:
            gamma = float(response)
            if -10 <= gamma <= 10:
                return gamma
            else:
                print("That entry is not valid. Please enter a gamma value between -10 and 10, or type 'not sure'.")
        except ValueError:
            print("That entry is not valid. Please enter a gamma value between -10 and 10, or type 'not sure'.")


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


print("=" * 60)
print("Welcome to the sustainable finance portfolio tool!")
print("=" * 60)
print("This tool helps you compare two investments based on:")
print("- financial performance")
print("- risk")
print("- ESG preferences")
print("\nYou will first be asked how you would like to enter ESG information.")
print("You will then enter information for two assets.\n")

esg_input_method = ask_esg_input_method()
use_separate_scores = (esg_input_method == "2")

pillar_weights = None
if use_separate_scores:
    pillar_weights = ask_pillar_weights()

print("\n" + "=" * 60)
print("ASSET INFORMATION")
print("=" * 60)

asset1_name = input(
    "What is the name of the first company or fund you would like to include in your portfolio? "
    "(Example: Apple, Tesla, FTSE 100 ETF): "
).strip()

asset2_name = input(
    "What is the name of the second company or fund you would like to include in your portfolio? "
    "(Example: Microsoft, Nvidia, S&P 500 ETF): "
).strip()

print(f"\nPlease enter the financial information for {asset1_name}:")
r1 = get_number(
    f"What is the expected annual return for {asset1_name} (%)? "
    "Example: enter 8 for 8%: "
) / 100

sd1 = get_number(
    f"What is the expected annual volatility for {asset1_name} (standard deviation, %)? "
    "Example: enter 15 for 15%: ",
    0
) / 100

print(f"\nPlease enter the financial information for {asset2_name}:")
r2 = get_number(
    f"What is the expected annual return for {asset2_name} (%)? "
    "Example: enter 10 for 10%: "
) / 100

sd2 = get_number(
    f"What is the expected annual volatility for {asset2_name} (standard deviation, %)? "
    "Example: enter 20 for 20%: ",
    0
) / 100

print("\n" + "=" * 60)

print("MARKET INFORMATION")
print("=" * 60)

rho = get_number(
    f"What is the correlation coefficient between {asset1_name} and {asset2_name}? "
    "Enter a value between -1 and 1: ",
    -1,
    1
)

r_free = get_number(
    "What risk-free rate (%)? "
    "Example: enter 2 for 2%: "
) / 100

gamma = ask_gamma()

print("\n" + "=" * 60)

print("ESG SCORES")
print("=" * 60)

print(f"\nPlease enter the ESG information for {asset1_name}.")
esg1_100, esg1_1 = ask_esg_score(asset1_name, use_separate_scores, pillar_weights)

print(f"\nPlease enter the ESG information for {asset2_name}.")
esg2_100, esg2_1 = ask_esg_score(asset2_name, use_separate_scores, pillar_weights)

print("\n" + "=" * 60)
print("ESG PREFERENCES")
print("=" * 60)

lambda_esg = ask_lambda()

weights = np.linspace(0, 1, 1000)

returns = []
risks = []
esg_scores_100 = []
sharpe_ratios = []
utilities_esg = []
utilities_no_esg = []

for w in weights:
    port_ret = portfolio_return(w, r1, r2)
    port_sd = portfolio_sd(w, sd1, sd2, rho)
    port_esg_display = portfolio_esg(w, esg1_100, esg2_100)
    port_esg_utility = portfolio_esg(w, esg1_1, esg2_1)

    returns.append(port_ret)
    risks.append(port_sd)
    esg_scores_100.append(port_esg_display)

    if port_sd > 0:
        sharpe = (port_ret - r_free) / port_sd
    else:
        sharpe = -np.inf
    sharpe_ratios.append(sharpe)

    utility_esg = port_ret - (gamma / 2) * (port_sd ** 2) + lambda_esg * port_esg_utility
    utility_no_esg = port_ret - (gamma / 2) * (port_sd ** 2)

    utilities_esg.append(utility_esg)
    utilities_no_esg.append(utility_no_esg)

max_sharpe_index = np.argmax(sharpe_ratios)
w1_tangency = weights[max_sharpe_index]
w2_tangency = 1 - w1_tangency
ret_tangency = returns[max_sharpe_index]
sd_tangency = risks[max_sharpe_index]
esg_tangency_100 = esg_scores_100[max_sharpe_index]

# ESG threshold implied by user's ESG preference
esg_threshold = get_esg_threshold(lambda_esg, esg1_100, esg2_100)

eligible_weights = []
eligible_returns = []
eligible_risks = []
eligible_esg_scores = []
eligible_sharpes = []

for i, w in enumerate(weights):
    if esg_scores_100[i] >= esg_threshold:
        eligible_weights.append(w)
        eligible_returns.append(returns[i])
        eligible_risks.append(risks[i])
        eligible_esg_scores.append(esg_scores_100[i])

        if risks[i] > 0:
            eligible_sharpes.append((returns[i] - r_free) / risks[i])
        else:
            eligible_sharpes.append(-np.inf)

if len(eligible_weights) == 0:
    raise ValueError("No portfolios satisfy the ESG threshold.")

max_sharpe_esg_index = np.argmax(eligible_sharpes)

w1_tangency_esg = eligible_weights[max_sharpe_esg_index]
w2_tangency_esg = 1 - w1_tangency_esg
ret_tangency_esg = eligible_returns[max_sharpe_esg_index]
sd_tangency_esg = eligible_risks[max_sharpe_esg_index]
esg_tangency_esg_100 = eligible_esg_scores[max_sharpe_esg_index]

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

# ----------------------------------------------------------
# Final investor allocation between risk-free asset and tangency portfolio
# ----------------------------------------------------------
if gamma > 0 and sd_tangency > 0:
    y_all_raw = (ret_tangency - r_free) / (gamma * (sd_tangency ** 2))
else:
    y_all_raw = np.nan

if gamma > 0 and sd_tangency_esg > 0:
    y_esg_raw = (ret_tangency_esg - r_free) / (gamma * (sd_tangency_esg ** 2))
else:
    y_esg_raw = np.nan

# No borrowing / no leverage version for the app
if np.isnan(y_all_raw):
    y_all = np.nan
    rf_all = np.nan
else:
    y_all = min(max(y_all_raw, 0), 1)
    rf_all = 1 - y_all

if np.isnan(y_esg_raw):
    y_esg = np.nan
    rf_esg = np.nan
else:
    y_esg = min(max(y_esg_raw, 0), 1)
    rf_esg = 1 - y_esg

# ----------------------------------------------------------
# Inputs summary
# ----------------------------------------------------------
inputs_table = pd.DataFrame({
    "Item": [
        "ESG preference strength (lambda)",
        "Minimum ESG score needed for the ESG-constrained portfolio set",
        "Risk-free rate",
        "Risk aversion (gamma)"
    ],
    "Value": [
        f"{lambda_esg:.2f}",
        f"{esg_threshold:.2f}",
        f"{r_free * 100:.2f}%",
        f"{gamma:.2f}"
    ]
})

print("\nYour inputs:")
show_table(inputs_table)

# ----------------------------------------------------------
# Portfolio comparison
# ----------------------------------------------------------
portfolio_table = pd.DataFrame({
    "Metric": [
        f"{asset1_name} weight",
        f"{asset2_name} weight",
        "Expected return",
        "Risk (standard deviation)",
        "Portfolio ESG score",
        "Sharpe ratio"
    ],
    "Optimal risky portfolio (no ESG constraint)": [
        f"{w1_tangency * 100:.2f}%",
        f"{w2_tangency * 100:.2f}%",
        f"{ret_tangency * 100:.2f}%",
        f"{sd_tangency * 100:.2f}%",
        f"{esg_tangency_100:.2f}",
        f"{sharpe_ratios[max_sharpe_index]:.4f}"
    ],
    "Optimal risky portfolio (with ESG constraint)": [
        f"{w1_tangency_esg * 100:.2f}%",
        f"{w2_tangency_esg * 100:.2f}%",
        f"{ret_tangency_esg * 100:.2f}%",
        f"{sd_tangency_esg * 100:.2f}%",
        f"{esg_tangency_esg_100:.2f}",
        f"{eligible_sharpes[max_sharpe_esg_index]:.4f}"
    ]
})

print("\nPortfolio comparison:")
show_table(portfolio_table)

# ----------------------------------------------------------
# Final investor allocation
# ----------------------------------------------------------
allocation_table = pd.DataFrame({
    "Allocation": [
        "Weight in the optimal risky portfolio",
        "Weight in the risk-free asset"
    ],
    "No ESG constraint": [
        f"{y_all * 100:.2f}%" if not np.isnan(y_all) else "N/A",
        f"{rf_all * 100:.2f}%" if not np.isnan(rf_all) else "N/A"
    ],
    "With ESG constraint": [
        f"{y_esg * 100:.2f}%" if not np.isnan(y_esg) else "N/A",
        f"{rf_esg * 100:.2f}%" if not np.isnan(rf_esg) else "N/A"
    ]
})

# ----------------------------------------------------------
# Impact of ESG constraint
# ----------------------------------------------------------
impact_table = pd.DataFrame({
    "Change": [
        "Expected return change",
        "Risk change",
        "Portfolio ESG score change"
    ],
    "Value": [
        f"{(ret_tangency_esg - ret_tangency) * 100:.2f} percentage points",
        f"{(sd_tangency_esg - sd_tangency) * 100:.2f} percentage points",
        f"{(esg_tangency_esg_100 - esg_tangency_100):.2f} points"
    ]
})

print("\nImpact of applying the ESG constraint:")
show_table(impact_table)

print("\nNote on the impact table:")
print("All changes are calculated as: ESG-constrained value - non-ESG-constrained value.")

if esg_tangency_100 >= esg_threshold:
    print("\nExplanation:")
    print("The portfolio that is optimal without an ESG constraint already satisfies the ESG requirement,")
    print("so applying the ESG constraint does not materially change the optimal risky portfolio.")
else:
    print("\nExplanation:")
    print("Accounting for these ESG requirements excludes some portfolio combinations from the available investment set,")
    print("so the ESG-constrained optimal risky portfolio is different from the unconstrained one.")

print("\nNote:")
print("The optimal risky portfolio shown above is the tangency portfolio in each case.")
print("We suggest the user invests 100% into the risky portfolio with no weight allocation into the risk-free asset.")

# ==========================================================
# Mean-Variance Frontier with ESG Constraint (TEXTBOOK GRAPH)
# ==========================================================

from matplotlib.ticker import PercentFormatter

# Wider range for DISPLAY ONLY so the frontier looks more complete
weights_plot = np.linspace(-1.0, 2.0, 1200)

returns_frontier = [portfolio_return(w, r1, r2) for w in weights_plot]
sds_frontier = [portfolio_sd(w, sd1, sd2, rho) for w in weights_plot]
esg_frontier = [portfolio_esg(w, esg1_100, esg2_100) for w in weights_plot]

sds_frontier_esg = []
returns_frontier_esg = []

for i in range(len(weights_plot)):
    if esg_frontier[i] >= esg_threshold:
        sds_frontier_esg.append(sds_frontier[i])
        returns_frontier_esg.append(returns_frontier[i])

fig, ax = plt.subplots(figsize=(10, 7))

# Frontier without ESG constraint
ax.plot(
    sds_frontier,
    returns_frontier,
    color="blue",
    linewidth=2,
    label="Frontier without ESG constraint"
)

# Frontier with ESG constraint
ax.plot(
    sds_frontier_esg,
    returns_frontier_esg,
    color="green",
    linewidth=2,
    label="Frontier with ESG constraint"
)

# CML lines
sd_max = max(max(sds_frontier), max(sds_frontier_esg), sd_tangency, sd_tangency_esg) * 1.05
sd_range = np.linspace(0, sd_max, 300)

cml_all = r_free + ((ret_tangency - r_free) / sd_tangency) * sd_range
cml_esg = r_free + ((ret_tangency_esg - r_free) / sd_tangency_esg) * sd_range

ax.plot(
    sd_range,
    cml_all,
    linestyle="--",
    color="blue",
    linewidth=1.8,
    label="CML without ESG constraint"
)

ax.plot(
    sd_range,
    cml_esg,
    linestyle="--",
    color="green",
    linewidth=1.8,
    label="CML with ESG constraint"
)

# Tangency stars
ax.scatter(
    sd_tangency,
    ret_tangency,
    color="blue",
    marker="*",
    s=100,
    edgecolors="black",
    linewidths=0.8,
    zorder=5,
    label="Optimal risky portfolio (no ESG constraint)"
)

ax.scatter(
    sd_tangency_esg,
    ret_tangency_esg,
    color="green",
    marker="*",
    s=100,
    edgecolors="black",
    linewidths=0.8,
    zorder=6,
    label="Optimal risky portfolio (with ESG constraint)"
)

# Labels next to stars
ax.annotate(
    "No ESG",
    (sd_tangency, ret_tangency),
    textcoords="offset points",
    xytext=(-28, -14),
    fontsize=9,
    color="blue"
)

ax.annotate(
    "ESG",
    (sd_tangency_esg, ret_tangency_esg),
    textcoords="offset points",
    xytext=(8, 8),
    fontsize=9,
    color="green"
)

# Risk-free asset
ax.scatter(
    0,
    r_free,
    color="black",
    marker="s",
    s=90,
    label="Risk-free asset"
)

# Better axis scaling
frontier_x = sds_frontier + sds_frontier_esg + [0]
frontier_y = returns_frontier + returns_frontier_esg + [r_free]

ax.set_xlim(0, max(frontier_x) * 1.02)
ax.set_ylim(min(frontier_y) - 0.01, max(frontier_y) + 0.01)

# Percent axes
ax.xaxis.set_major_formatter(PercentFormatter(1.0))
ax.yaxis.set_major_formatter(PercentFormatter(1.0))

ax.set_xlabel("Risk (Standard Deviation)")
ax.set_ylabel("Expected Return")
ax.set_title("Efficient Frontier with ESG Constraint")
ax.legend()
ax.grid(True, alpha=0.3)

plt.show()

print("\nNotes:")
print("This chart shows the risk-return trade-off from combining the two selected assets.")
print("The star markers indicate the optimal risky portfolio in each case, meaning the portfolio with the highest Sharpe ratio before and after applying the ESG requirement.")
print("If the two stars do not overlap, this means your ESG preferences change the portfolio that provides the best risk-adjusted return for you.")

# ==========================================================
# ESG-Sharpe Frontier
# ==========================================================

weights_esg_plot = np.linspace(0, 1, 400)

esg_vals = []
sharpe_vals = []

for w in weights_esg_plot:
    port_ret = portfolio_return(w, r1, r2)
    port_sd = portfolio_sd(w, sd1, sd2, rho)
    port_esg = portfolio_esg(w, esg1_100, esg2_100)

    if port_sd > 0:
        sharpe = (port_ret - r_free) / port_sd
    else:
        sharpe = -np.inf

    esg_vals.append(port_esg)
    sharpe_vals.append(sharpe)

fig2, ax2 = plt.subplots(figsize=(9, 6))

ax2.plot(
    esg_vals,
    sharpe_vals,
    linewidth=2,
    color="red",
    label="ESG-Sharpe Ratio Frontier"
)

# Tangency points
tangency_sharpe = (ret_tangency - r_free) / sd_tangency if sd_tangency > 0 else -np.inf
tangency_esg_sharpe = (ret_tangency_esg - r_free) / sd_tangency_esg if sd_tangency_esg > 0 else -np.inf

ax2.scatter(
    esg_tangency_100,
    tangency_sharpe,
    marker="*",
    s=220,
    color="blue",
    edgecolors="black",
    linewidths=0.8,
    zorder=5,
    label="Tangency Portfolio (All)"
)

ax2.scatter(
    esg_tangency_esg_100,
    tangency_esg_sharpe,
    marker="*",
    s=220,
    color="green",
    edgecolors="black",
    linewidths=0.8,
    zorder=6,
    label="Tangency Portfolio (ESG)"
)

ax2.annotate(
    "All",
    (esg_tangency_100, tangency_sharpe),
    textcoords="offset points",
    xytext=(-18, -12),
    fontsize=9,
    color="blue"
)

ax2.annotate(
    "ESG",
    (esg_tangency_esg_100, tangency_esg_sharpe),
    textcoords="offset points",
    xytext=(8, 8),
    fontsize=9,
    color="green"
)

ax2.set_xlabel("Portfolio ESG Score (0-100)")
ax2.set_ylabel("Sharpe Ratio")
ax2.set_title("ESG-Sharpe Ratio Frontier")
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.show()

print("\nNotes:")
print("This chart shows how the Sharpe ratio changes as the portfolio ESG score varies across different combinations of the two assets.")
print("Blue Star: marks portfolio with highest Sharpe ratio overall")
print("Green Star: marks portfolio with highest Sharpe ratio among portfolios that satisfy your ESG preference")
print("The distance between the two stars indicates the trade-off between improving ESG performance and maintaining risk-adjusted return.")


# In[ ]:




