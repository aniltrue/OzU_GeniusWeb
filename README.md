# CS 451/551 Project

This is the project repository for CS451/551 Project.

## Overview
- directories:
    - `agents`: Contains directories with the agents. The `template_agent` directory contains the template for this competition.
    - `domains`: Contains the domains which are problems over which the agents are supposed to negotiate.
    - `utils`: Arbitrary utilities to run sessions and process results.
- files:
    - `run.py`: Main interface to test agents in single session runs.
    - `run_tournament.py`: Main interface to test a set of agents in a tournament. Here, every agent will negotiate against every other agent in the set on every set of preferences profiles that is provided (see code).
    - `requirements.txt`: Python dependencies for this template repository.
    - `requirements_allowed.txt`: Additional dependencies that you can use. Send me a message (Discord/mail) in case you require an unlisted dependency. I will then add a compatible version to the allowed dependencies list.

## Installation
Download or clone this repository. *Note that if you fork this repository you cannot make it private*, which is default behaviour of GitHub. This will cause your code to be publicly visible if you push it to your forked repository.

We recommend using Python >= 3.9 as this version will be used during the actual competition. The required dependencies are listed in the `requirements.txt` file and can be installed through `pip install -r requirements.txt`. We advise you to create a Python virtual environment to install the dependencies in isolation (e.g. `python3.9 -m venv .venv`, see also [here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment))

As already mentioned, should you need any additional dependencies, please notify me. A few of the most common dependencies are already listed in `requirements_allowed.txt` file. 

For VSCode devcontainer users: We included a devcontainer specification in the `.devcontainer` directory.

## Quickstart
- Copy and rename the template agent's directory, files and classname.
- Read through the code to familiarise yourself with its workings. The agent already works but is not very good.
- Develop your agent in the copied directory. Make sure that all the files that you use are in the directory.
- Test your agent through `run.py`, results will be returned as dictionaries and saved as json-file. A plot of the negotiation trace will also be saved.
- In `run.py` file, stored data will be cleaned if `RESET_STORAGE` is true. Otherwise, your agent can be use previous stored data.
- You can also test your agent more extensively by running a tournament with a set of agents. Use the `run_tournament.py` script for this. Summaries of the results will be saved to the results directory.

## Documentation
The code of GeniusWebPython is properly documented. Exploring the class definitions of the classes used in the template agent is usually sufficient to understand how to work with them.

[More documentation can be found here](https://tracinsy.ewi.tudelft.nl/pubtrac/GeniusWebPython/wiki/WikiStart). This documentation was written for the Java version of GeniusWeb, but classes and functionality are identical as much as possible.


## Template Agent
To implement a negotiating agent, you can use `template_agent` as a baseline. Copy `template_agent` folder and rename it. Do not forget to change the name of the `template_agent.py` file, the name of the class and the `NAME` attribute in the `template_agent`class. Also, you should append your agent into the list of agent in both `run.py`and `run_tournament.py`. 

The `template_agent` is based on BOA components. You should implement (change) the corresponding methods in the following classes:

- `acceptance_strategy.py`: This class decides when to accept the opponent's offer (Acceptance Strategy)
- `bidding_strategy.py`: This class decides which bid will be offered to the opponent (Bidding Strategy)
- `opponent_model.py`: This class tries to estimate the opponent's preferences during a negotiation session (Opponent Model)
- `learning_model.py`: The challenge of 2023 ANAC competition is learning from the previous negotiation sessions. At the end of each negotiation session, you will get the opponent's name to store corresponding information to utilize in the next sessions where you have the same opponent.

## Notes
- You are allowed to store data after the negotiation was finished ("Finished" object received) to use for future sessions. This allows for learning opponent behaviour over time and responding to it. The directory to save this data to is passed to the agent as parameter (`storage_dir`). In the template agent the path to this directory is assign to the `self.storage_dir` variable. Your agent is run parallel against multiple opponents during the final tournament, so make sure to handle this properly. Read section 3 of the [CfP](docs/ANL_2022_CfP.pdf) for information on this.
- If you want to test your agent in a single session, you can use `run.py` instead of `run_tournament.py` file. In `run.py` file, `RESET_STORAGE` variable decides to clear the storage or not. If you want to test your agent in learning challenge, you should set `RESET_STORAGE` as `False`. Otherwise, you should set it as `True` to clear all the stored data.