from agents.hybrid.utils import *


class BiddingStrategy:
    """
        Hybrid Agent Implementation:

            Solver Agent: Towards Emotional and Opponent-Aware Agent for Human-Robot Negotiation
            https://www.researchgate.net/publication/357708964_Solver_Agent_Towards_Emotional_and_Opponent-Aware_Agent_for_Human-Robot_Negotiation
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    my_offers: list
    received_offers: list

    p0: float = 1.0
    p1: float = 0.7
    p2: float = 0.4
    p3: float = 0.5
    window_lower_bound: float = 0.02
    window_upper_bound: float = 0.02
    epsilon: float = 0.05

    def __init__(self, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.profile = profile
        self.progress = progress
        self.my_offers = []
        self.received_offers = []

    def received_bid(self, bid: Bid, **kwargs):
        if bid is not None:
            self.received_offers.append(bid)

    def generate(self, **kwargs) -> Bid:
        time = get_time(self.progress)

        log_fn = kwargs["log"]

        time_utility = self.time_based(time, log_fn)

        if len(self.my_offers) < 1 or len(self.received_offers) < 2:
            target_utility = time_utility
        else:
            behavior_utility = self.behaviour_based(time, log_fn)

            target_utility = (1 - time * time) * behavior_utility + time * time * time_utility

        target_utility = max(self.p2, min(self.p0, target_utility))

        log_fn("Target Utility: %f" % target_utility)

        bids = get_bids_at(self.profile, target_utility, self.window_lower_bound, self.window_upper_bound)

        if len(bids) > 0:
            selected_bid = bids[0]

            opponent_model = kwargs["opponent_model"]

            for bid in bids:
                if opponent_model.get_utility(bid) * get_utility(self.profile, bid) > \
                        opponent_model.get_utility(selected_bid) * get_utility(self.profile, selected_bid):
                    selected_bid = bid
        else:
            selected_bid = get_bid_at(self.profile, target_utility)

        self.my_offers.append(selected_bid)

        log_fn("Offered Bid: %f" % get_utility(self.profile, selected_bid))

        return selected_bid

    def time_based(self, time: float, log_fn) -> float:
        utility = (1 - time) * (1 - time) * self.p0 + \
            2 * (1 - time) * time * self.p1 + \
            time * time * self.p2

        log_fn("Time Based: %f" % utility)

        return utility

    def behaviour_based(self, time: float, log_fn) -> float:
        W = {
            1: [1],
            2: [0.25, 0.75],
            3: [0.11, 0.22, 0.66],
            4: [0.05, 0.15, 0.3, 0.5],
        }

        diff = [get_utility(self.profile, self.received_offers[i + 1]) - get_utility(self.profile, self.received_offers[i])
                for i in range(len(self.received_offers) - 1)]

        if len(diff) > len(W):
            diff = diff[:len(W)]

        delta = sum([u * w for u, w in zip(diff, W[len(diff)])])

        utility = get_utility(self.profile, self.my_offers[-1]) - (self.p3 + self.p3 * time) * delta

        log_fn("Behaviour Based: %f" % utility)

        return utility

    def update(self, learned_data: list, log_fn):
        domain_size = AllBidsList(self.profile.getDomain()).size()

        p1_ratio = 0.6
        min_utility, max_utility = get_min_max_utility(self.profile)

        if len(learned_data) >= 2:
            previous_data = learned_data[-2]
            current_data = learned_data[-1]

            if abs(previous_data["p1"] - current_data["p1"]) <= self.epsilon:
                p1_ratio += 0.1
                self.p2 += 0.1
                self.p3 = 0.2
            if current_data["domain_size"] > previous_data["domain_size"] and abs(previous_data["p1"] - current_data["p1"]) <= self.epsilon:
                p1_ratio += 0.1
                self.window_upper_bound += 0.01
                self.window_lower_bound -= 0.01

        reservation_utility = get_reservation_value(self.profile)

        self.p0 = min(1.0, max_utility)
        self.p2 = max([min_utility, self.p2, reservation_utility])
        self.p1 = (self.p2 + self.p0) * p1_ratio

        log_fn("P0: %f, P1: %f, P2: %f" % (self.p0, self.p1, self.p2))
