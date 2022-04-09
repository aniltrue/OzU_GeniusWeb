from agents.hybrid.utils import *


class AcceptanceStrategy:
    """
        AC_Next implementation.
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    min_p2: float = 0.0
    epsilon: float = 0.05

    def __init__(self, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.profile = profile
        self.progress = progress

    def is_accepted(self, received_bid: Bid, generated_bid: Bid, **kwargs) -> bool:
        if received_bid is None:
            return False

        time = get_time(self.progress)

        received_utility = get_utility(self.profile, received_bid)
        generated_utility = get_utility(self.profile, generated_bid)

        return max(generated_utility, self.min_p2) <= received_utility

    def update(self, learned_data: list, log_fn):
        if len(learned_data) >= 2:
            previous_data = learned_data[-2]
            current_data = learned_data[-1]

            if abs(previous_data["p2"] - current_data["p2"]) <= self.epsilon:
                self.min_p2 = (previous_data["p2"] + current_data["p2"]) * .5

                log_fn("Acceptance updated: %f" % self.min_p2)