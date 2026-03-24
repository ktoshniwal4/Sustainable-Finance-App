#!/usr/bin/env python
# coding: utf-8

# In[1]:


#%%
import numpy as np
import matplotlib.pyplot as plt


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
    print("SECTION 1: ESG INFORMATION METHOD")
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
        print(f"\nPlease enter the separate ESG scores for {asset_name} using the {agency.upper()} format.")

        if agency == "msci":
            print("For MSCI, use one of: CCC, B, BB, BBB, A, AA, AAA")
            print("Lowercase entries will also work.")
        elif agency == "sustainalytics":
            print("For Sustainalytics, enter a number where lower is better.")
        elif agency == "refinitiv":
            print("For Refinitiv (LSEG), enter an integer from 0 to 5.")
        elif agency == "s&p":
            print("For S&P Dow Jones, enter a number from 0 to 100.")

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
        print(f"\nPlease enter the overall ESG score for {asset_name} using the {agency.upper()} format.")

        if agency == "msci":
            print("For MSCI, use one of: CCC, B, BB, BBB, A, AA, AAA")
            print("Lowercase entries will also work.")
        elif agency == "sustainalytics":
            print("For Sustainalytics, enter a number where lower is better.")
        elif agency == "refinitiv":
            print("For Refinitiv (LSEG), enter an integer from 0 to 5.")
        elif agency == "s&p":
            print("For S&P Dow Jones, enter a number from 0 to 100.")

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

def get_int_input(prompt, valid_range):
    while True:
        try:
            value = int(input(prompt).strip())
            if value in valid_range:
                return value
            print(f"That entry is not valid. Please enter a whole number from {min(valid_range)} to {max(valid_range)}.")
        except ValueError:
            print("That entry is not valid. Please enter a whole number.")

def ask_gamma():
    print("\nYour risk preference affects how much portfolio risk you are comfortable taking.")
    print("If you already know your risk aversion parameter gamma, enter it below.")
    print("A positive gamma means risk-averse, 0 means risk-neutral, and a negative gamma means risk-loving.")
    print("If you do not know it, type 'not sure'.")
    print("You will then be asked a short 5-question questionnaire.\n")

    while True:
        response = input(
            "Please enter your gamma value "
            "(for example, around -10 to 10: negative = risk-loving, 0 = risk-neutral, positive = risk-averse), "
            "or type 'not sure' if you do not know your value: "
        ).strip().lower()

        if response == "not sure":
            scores = []

            # Q1
            print("\n--- Q1: General attitude ---")
            print("Q1. How would you describe your general attitude")
            print(" towards investment risk?")
            print(" 1. I avoid risk wherever possible")
            print(" 2. I prefer low-risk, steady options")
            print(" 3. I am comfortable with moderate risk")
            print(" 4. I am generally willing to take on risk for higher returns")
            print(" 5. I actively seek high-risk, high-reward opportunities")
            scores.append(get_int_input(" Your answer (1-5): ", range(1, 6)))

            # Q2
            print("\n--- Q2: Safe vs. growth preference ---")
            print('Q2. "I prefer an investment that grows slowly but')
            print(' steadily, even if it means lower overall returns."')
            print(" 1. I strongly agree")
            print(" 2. I tend to agree")
            print(" 3. I am in between")
            print(" 4. I tend to disagree")
            print(" 5. I strongly disagree")
            scores.append(get_int_input(" Your answer (1-5): ", range(1, 6)))

            # Q3
            print("\n--- Q3: Reaction to a loss ---")
            print("Q3. Your portfolio drops 20% in value over three months.")
            print(" What is your most likely reaction?")
            print(" 1. Sell everything immediately to stop further losses")
            print(" 2. Sell some holdings to reduce exposure")
            print(" 3. Do nothing and wait for recovery")
            print(" 4. Review the portfolio but stay the course")
            print(" 5. See it as a buying opportunity and invest more")
            scores.append(get_int_input(" Your answer (1-5): ", range(1, 6)))

            # Q4
            print("\n--- Q4: High-risk allocation willingness ---")
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
            print("\n--- Q5: Certain small gain vs. uncertain large gain ---")
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
        w1**2 * sd1**2 +
        (1 - w1)**2 * sd2**2 +
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
print("SECTION 2: ASSET INFORMATION")
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
print("SECTION 3: MARKET ASSUMPTIONS")
print("=" * 60)

rho = get_number(
    f"What is the correlation coefficient between {asset1_name} and {asset2_name}? "
    "Enter a value between -1 and 1: ",
    -1,
    1
)

r_free = get_number(
    "What risk-free rate would you like to assume (%)? "
    "Example: enter 2 for 2%: "
) / 100

gamma = ask_gamma()

print("\n" + "=" * 60)
print("SECTION 4: ESG SCORES")
print("=" * 60)

print(f"\nNow enter the ESG information for {asset1_name}.")
esg1_100, esg1_1 = ask_esg_score(asset1_name, use_separate_scores, pillar_weights)

print(f"\nNow enter the ESG information for {asset2_name}.")
esg2_100, esg2_1 = ask_esg_score(asset2_name, use_separate_scores, pillar_weights)

print("\n" + "=" * 60)
print("SECTION 5: ESG PREFERENCES")
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

max_utility_esg_index = np.argmax(utilities_esg)
w1_optimal_esg = weights[max_utility_esg_index]
w2_optimal_esg = 1 - w1_optimal_esg
ret_optimal_esg = returns[max_utility_esg_index]
sd_optimal_esg = risks[max_utility_esg_index]
esg_optimal_esg_100 = esg_scores_100[max_utility_esg_index]
utility_optimal_esg = utilities_esg[max_utility_esg_index]

max_utility_no_esg_index = np.argmax(utilities_no_esg)
w1_optimal_no_esg = weights[max_utility_no_esg_index]
w2_optimal_no_esg = 1 - w1_optimal_no_esg
ret_optimal_no_esg = returns[max_utility_no_esg_index]
sd_optimal_no_esg = risks[max_utility_no_esg_index]
esg_optimal_no_esg_100 = esg_scores_100[max_utility_no_esg_index]
utility_optimal_no_esg = utilities_no_esg[max_utility_no_esg_index]

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

if use_separate_scores:
    print("\nYou entered separate Environmental, Social, and Governance scores for both assets.")
else:
    print("\nYou entered overall ESG scores for both assets.")

print("\nESG preference strength (lambda):", lambda_esg)

print("\nTangency portfolio:")
print(f"{asset1_name}: {w1_tangency * 100:.2f}%")
print(f"{asset2_name}: {w2_tangency * 100:.2f}%")
print(f"Expected return: {ret_tangency * 100:.2f}%")
print(f"Portfolio risk: {sd_tangency * 100:.2f}%")
print(f"Portfolio ESG score (0-100): {esg_tangency_100:.2f}")

print("\nOptimal portfolio if you did not care about ESG:")
print(f"{asset1_name}: {w1_optimal_no_esg * 100:.2f}%")
print(f"{asset2_name}: {w2_optimal_no_esg * 100:.2f}%")
print(f"Expected return: {ret_optimal_no_esg * 100:.2f}%")
print(f"Portfolio risk: {sd_optimal_no_esg * 100:.2f}%")
print(f"Portfolio ESG score (0-100): {esg_optimal_no_esg_100:.2f}")
print(f"Utility: {utility_optimal_no_esg:.4f}")

print("\nOptimal portfolio including your ESG preferences:")
print(f"{asset1_name}: {w1_optimal_esg * 100:.2f}%")
print(f"{asset2_name}: {w2_optimal_esg * 100:.2f}%")
print(f"Expected return: {ret_optimal_esg * 100:.2f}%")
print(f"Portfolio risk: {sd_optimal_esg * 100:.2f}%")
print(f"Portfolio ESG score (0-100): {esg_optimal_esg_100:.2f}")
print(f"Utility: {utility_optimal_esg:.4f}")

print("\nNote: ESG scores are displayed on a 0-100 scale,")
print("but a 0-1 normalized ESG scale is used inside the utility function.")

weights_plot = np.linspace(0, 1, 200)
returns_frontier = [portfolio_return(w, r1, r2) for w in weights_plot]
sds_frontier = [portfolio_sd(w, sd1, sd2, rho) for w in weights_plot]
esg_frontier = [portfolio_esg(w, esg1_100, esg2_100) for w in weights_plot]

fig, ax = plt.subplots(figsize=(9, 6))

scatter = ax.scatter(sds_frontier, returns_frontier, c=esg_frontier, cmap="YlGn", s=35)
plt.colorbar(scatter, ax=ax, label="Portfolio ESG score (0-100)")

ax.plot(sds_frontier, returns_frontier, color="blue", linewidth=1.5, alpha=0.7, label="Efficient Frontier")

if sd_tangency > 0:
    sd_max = max(sds_frontier) * 1.2
    sd_cml = np.linspace(0, sd_max, 100)
    ret_cml = r_free + ((ret_tangency - r_free) / sd_tangency) * sd_cml
    ax.plot(sd_cml, ret_cml, "g--", linewidth=2, label="Capital Market Line")

ax.scatter(sd_tangency, ret_tangency, color="red", s=120, marker="*", label="Tangency Portfolio")
ax.scatter(sd_optimal_no_esg, ret_optimal_no_esg, color="purple", s=100, marker="X", label="Optimal Portfolio (No ESG)")
ax.scatter(sd_optimal_esg, ret_optimal_esg, color="orange", s=100, marker="D", label="Optimal Portfolio (With ESG)")
ax.scatter(0, r_free, color="green", s=80, marker="s", label="Risk-Free Asset")

ax.set_xlabel("Risk (Standard Deviation)")
ax.set_ylabel("Expected Return")
ax.set_title("Portfolio Frontier with ESG Adjustment")
ax.legend()
ax.grid(True, alpha=0.3)

plt.show()

# ==========================================================
# ESG–Sharpe Frontier
# ==========================================================

weights_esg_plot = np.linspace(0, 1, 200)

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

ax2.plot(esg_vals, sharpe_vals, linewidth=2, label="ESG–Sharpe Frontier")

# Highlight key portfolios
tangency_sharpe = (ret_tangency - r_free) / sd_tangency if sd_tangency > 0 else -np.inf
opt_esg_sharpe = (ret_optimal_esg - r_free) / sd_optimal_esg if sd_optimal_esg > 0 else -np.inf
opt_no_esg_sharpe = (ret_optimal_no_esg - r_free) / sd_optimal_no_esg if sd_optimal_no_esg > 0 else -np.inf

ax2.scatter(esg_tangency_100, tangency_sharpe, marker="*", s=120, label="Tangency Portfolio")
ax2.scatter(esg_optimal_esg_100, opt_esg_sharpe, marker="D", s=100, label="Optimal (With ESG)")
ax2.scatter(esg_optimal_no_esg_100, opt_no_esg_sharpe, marker="X", s=100, label="Optimal (No ESG)")

ax2.set_xlabel("Portfolio ESG Score (0–100)")
ax2.set_ylabel("Sharpe Ratio")
ax2.set_title("ESG–Sharpe Frontier")
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.show()
#%%


# In[ ]:




