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
        self.profile = profile
        self.progress = progress
        self.received_bids = []
        self.my_bids = []
        self.data = {}

    def receive_bid(self, bid: Bid, **kwargs):
        if bid is not None:
            self.received_bids.append(bid)

    def save_bid(self, bid: Bid, **kwargs):
        self.my_bids.append(bid)

    def reach_agreement(self, accepted_bid: Bid, opponent_accepted: bool, **kwargs):
        time = get_time(self.progress)

        self.accepted_bid = accepted_bid
        self.opponent_accepted = opponent_accepted
        self.acceptance_time = time

    def save_data(self, storage_dir: str, other: str, **kwargs):
        # If there is no information
        if other is None or storage_dir is None:
            return

        # Save the data as Pickle format.
        with open(f"{storage_dir}/{other}_data.pkl", "wb") as f:
            pickle.dump(self.data, f)

    def load_data(self, storage_dir: str, other: str, **kwargs) -> dict:
        self.data = {}

        # If there is no information
        if storage_dir is None or other is None:
            return self.data

        # Load corresponding data
        if os.path.exists(f"{storage_dir}/{other}_data.pkl"):
            with open(f"{storage_dir}/{other}_data.pkl", "rb") as f:
                self.data = pickle.load(f)

        return self.data
