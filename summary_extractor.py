import json
import os.path
from pathlib import Path
from typing import Union
import pandas as pd
import numpy as np


def extract(tournament_results_json: Union[str, Path], save_dir: Union[str, Path]):
    """
        This method extracts some detailed tournament results.
    :param tournament_results_json: Path of ``tournament_results.json`` file
    :param save_dir: Directory to extract
    :return: Nothing
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    rows = []
    agent_names = set()

    # results.csv
    with open(tournament_results_json, "r") as f:
        data = json.load(f)

        for session in data:
            numbers = []

            for key in session:
                if key.startswith("agent_"):
                    numbers.append(int(key.split("_")[1]))

            agent_a, agent_b = min(numbers), max(numbers)

            row = {
                "AgentA": session[f"agent_{agent_a}"],
                "AgentAUtility": session[f"utility_{agent_a}"],
                "AgentB": session[f"agent_{agent_b}"],
                "AgentBUtility": session[f"utility_{agent_b}"],
                "Result": session["result"].capitalize()
            }

            rows.append(row)

            agent_names.add(row["AgentA"])
            agent_names.add(row["AgentB"])

    df = pd.DataFrame(data=rows)
    df.to_csv(os.path.join(save_dir, "results.csv"), sep=";")

    # Summary
    summary_rows = []

    for agent_name in agent_names:
        row = {"Agent": agent_name}

        rows_a = df.loc[df["AgentA"] == agent_name]
        rows_b = df.loc[df["AgentB"] == agent_name]

        utility = rows_a["AgentAUtility"].to_list() + rows_b["AgentBUtility"].to_list()

        row["Utility Mean"] = np.mean(utility)
        row["Utility Stdev"] = np.std(utility)

        opp_utility = rows_a["AgentBUtility"].to_list() + rows_b["AgentAUtility"].to_list()

        row["Opp. Utility Mean"] = np.mean(opp_utility)
        row["Opp. Utility Stdev"] = np.mean(opp_utility)

        row["Nash Product Mean"] = np.mean([a * b for a, b in zip(utility, opp_utility)])
        row["Nash Product Stdev"] = np.std([a * b for a, b in zip(utility, opp_utility)])

        row["Social Welfare Mean"] = np.mean([a + b for a, b in zip(utility, opp_utility)])
        row["Social Welfare Stdev"] = np.std([a + b for a, b in zip(utility, opp_utility)])

        utility = rows_a.loc[rows_a["Result"] == "Agreement", "AgentAUtility"].to_list() + rows_b.loc[rows_b["Result"] == "Agreement","AgentBUtility"].to_list()

        row["Agreement Utility Mean"] = np.mean(utility)
        row["Agreement Utility Stdev"] = np.std(utility)

        opp_utility = rows_a.loc[rows_a["Result"] == "Agreement", "AgentBUtility"].to_list() + rows_b.loc[
            rows_b["Result"] == "Agreement", "AgentAUtility"].to_list()

        row["Agreement Opp. Utility Mean"] = np.mean(opp_utility)
        row["Agreement Opp. Utility Stdev"] = np.std(opp_utility)

        row["Count"] = len(rows_a) + len(rows_b)

        results = rows_a.loc[rows_a["Result"] == "Agreement", "Result"].to_list() + rows_b.loc[rows_b["Result"] == "Agreement", "Result"].to_list()

        row["Agreement"] = len(results)

        row["AgreementRate"] = float(len(results)) / row["Count"]

        results = rows_a.loc[rows_a["Result"] == "Error", "Result"].to_list() + rows_b.loc[rows_b["Result"] == "Error", "Result"].to_list()

        row["Error"] = len(results)

        results = rows_a.loc[rows_a["Result"] == "Failed", "Result"].to_list() + rows_b.loc[rows_b["Result"] == "Failed", "Result"].to_list()

        row["Failed"] = len(results)

        summary_rows.append(row)

    pd.DataFrame(data=summary_rows).to_csv(os.path.join(save_dir, "summary.csv"), sep=";")
