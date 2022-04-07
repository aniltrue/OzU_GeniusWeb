from agents.hybrid.utils import *
import os
import pickle


class LearningModel:
    """
        Save only minimum observed utility.
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    received_bids: list
    my_bids: list
    data: dict

    def __init__(self, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.profile = profile
        self.progress = progress
        self.received_bids = []
        self.my_bids = []
        self.data = {"min_value": -1.}

    def receive_bid(self, bid: Bid, **kwargs):
        self.received_bids.append(bid)

    def save_bid(self, bid: Bid, **kwargs):
        self.my_bids.append(bid)

    def save_data(self, storage_dir: str, other: str, **kwargs):
        if other is None or storage_dir is None:
            return

        min_value = 1.0

        for bid in self.received_bids:
            min_value = min(get_utility(self.profile, bid), min_value)

        self.data = {"min_value": min_value}

        with open(f"{storage_dir}/{other}_data.pkl", "wb") as f:
            pickle.dump(self.data, f)

    def load_data(self, storage_dir: str, other: str, **kwargs) -> dict:
        self.data = {"min_value": -1.}

        if storage_dir is None or other is None:
            return self.data

        if os.path.exists(f"{storage_dir}/{other}_data.pkl"):
            with open(f"{storage_dir}/{other}_data.pkl", "rb") as f:
                self.data = pickle.load(f)

        return self.data
