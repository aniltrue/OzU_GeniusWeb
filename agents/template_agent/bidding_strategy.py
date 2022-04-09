from agents.template_agent.utils import *


class BiddingStrategy:
    """
        Bidding Strategy
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    my_offers: list                         # Generated offers
    received_offers: list                   # Received offers

    def __init__(self, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.profile = profile
        self.progress = progress
        self.my_offers = []
        self.received_offers = []

    def received_bid(self, bid: Bid, **kwargs):
        """
            This method will be called when a bid received.
        @param bid: Received bid.
        @param kwargs:
        @return: None
        """
        if bid is not None:
            self.received_offers.append(bid)

    def generate(self, **kwargs) -> Bid:
        """
            Generate a bid.
        @return: Bid will be offered.
        """
        # Time
        time = get_time(self.progress)

        # Target utility decreases linearly.
        target_utility = 1. - time
        # Get the closest bid to Target Utility
        bid = get_bid_at(self.profile, target_utility)

        return bid
