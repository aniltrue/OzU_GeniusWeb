from agents.template_agent.utils import *
import os
import pickle


class LearningModel:
    """
        Learning Model
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    received_bids: list                 # Received bids
    my_bids: list                       # Generated bids by Bidding Strategy
    data: dict                          # Data will be saved.

    def __init__(self, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        """
            Constructor
        :param profile: Linear additive profile
        :param progress: Negotiation session progress time
        :param kwargs: Other
        """
        self.profile = profile
        self.progress = progress
        self.received_bids = []
        self.my_bids = []
        self.data = {}

    def receive_bid(self, bid: Bid, **kwargs):
        """
            This method is called when a bid is received from the opponent.
        :param bid: Received bid
        :param kwargs: Other
        :return: Nothing
        """
        if bid is not None:
            self.received_bids.append(bid)

    def save_bid(self, bid: Bid, **kwargs):
        """
            Save
        :param bid:
        :param kwargs:
        :return:
        """
        self.my_bids.append(bid)

    def reach_agreement(self, accepted_bid: Bid, opponent_accepted: bool, **kwargs):
        time = get_time(self.progress)

        self.accepted_bid = accepted_bid
        self.opponent_accepted = opponent_accepted
        self.acceptance_time = time

    def save_data(self, storage_dir: str, opponent_agent: str, **kwargs):
        """
            This method is called at the end of negotiation session to save learning data
        :param storage_dir: Storage directory
        :param opponent_agent: The name of opponent agent
        :param kwargs: Others
        :return: Nothing
        """
        # If there is no information
        if opponent_agent is None or storage_dir is None:
            return

        # Save the data as Pickle format.
        with open(f"{storage_dir}/{opponent_agent}_data.pkl", "wb") as f:
            pickle.dump(self.data, f)

    def load_data(self, storage_dir: str, opponent_agent: str, **kwargs) -> dict:
        """
            This method is called at the beginning of the negotiation session to get learned data
        :param storage_dir: Storage directory
        :param opponent_agent: The name of the opponent agent
        :param kwargs: Others
        :return: Learned data as directory
        """
        self.data = {}

        # If there is no information
        if storage_dir is None or opponent_agent is None:
            return self.data

        # Load corresponding data
        if os.path.exists(f"{storage_dir}/{opponent_agent}_data.pkl"):
            with open(f"{storage_dir}/{opponent_agent}_data.pkl", "rb") as f:
                self.data = pickle.load(f)

        return self.data
