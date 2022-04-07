from agents.hybrid.utils import *


class AcceptanceStrategy:
    """
        AC_Next implementation.
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime

    def __init__(self, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.profile = profile
        self.progress = progress

    def is_accepted(self, received_bid: Bid, generated_bid: Bid, **kwargs) -> bool:
        if received_bid is None:
            return False

        time = get_time(self.progress)

        received_utility = get_utility(self.profile, received_bid)
        generated_utility = get_utility(self.profile, generated_bid)

        return generated_utility <= received_utility
