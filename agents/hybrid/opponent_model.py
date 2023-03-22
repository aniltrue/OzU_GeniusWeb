import math

from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.DiscreteValueSet import DiscreteValueSet
from geniusweb.issuevalue.Domain import Domain
from geniusweb.issuevalue.Value import Value
from agents.hybrid.utils import *
from scipy.stats import chisquare


class OpponentModel:
    """
        Frequency Based Opponent Modelling implementation:

            Rethinking Frequency Opponent Modeling in Automated Negotiation
            https://www.researchgate.net/publication/320200219_Rethinking_Frequency_Opponent_Modeling_in_Automated_Negotiation
    """
    offers: list
    domain: Domain
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    issues: dict
    alpha: float = .1
    beta: float = 5.
    window_size: int = 5

    def __init__(self, domain: Domain, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.domain = domain
        self.profile = profile
        self.progress = progress
        self.offers = []

        self.issues = {issue: Issue(values, n=len(domain.getIssuesValues().keys()))
                       for issue, values in domain.getIssuesValues().items()}

        self.log_fn = kwargs["log"]

    def update(self, bid: Bid, **kwargs):
        if bid is None:
            return

        self.offers.append(bid)

        previous_bid = {issue: self.offers[-2].getValue(issue) for issue in self.issues.keys()}\
            if len(self.offers) >= 2 else {issue: None for issue in self.issues.keys()}

        for issue_name, issue_obj in self.issues.items():
            issue_obj.update(bid.getValue(issue_name), previous_value=previous_bid[issue_name], **kwargs)

        if len(self.offers) % self.window_size == 0 and len(self.offers) > self.window_size:
            current_window = self.offers[-self.window_size:]
            previous_window = self.offers[-2 * self.window_size:-self.window_size]

            self.update_issues(previous_window, current_window)

            self.log_fn("Issue Weights updated.")

    def update_issues(self, previous_window: list, current_window: list):
        time = get_time(self.progress)
        not_changed = []
        concession = False

        def frequency(window: list, issue_name: str, issue_obj: Issue):
            values = []

            for value in issue_obj.value_weights.keys():
                total = 0.

                for bid in window:
                    if bid.getValue(issue_name) == value:
                        total += 1.

                values.append((1. + total) / (len(window)))

            return values

        for issue_name, issue_obj in self.issues.items():
            fr_current = frequency(current_window, issue_name, issue_obj)
            fr_previous = frequency(previous_window, issue_name, issue_obj)
            p_val = chisquare(fr_previous, fr_current)[1]

            if p_val > 0.05:
                not_changed.append(issue_obj)
            else:
                estimated_current = sum([fr_current[i] * w for i, w in enumerate(issue_obj.value_weights.values())])
                estimated_previous = sum([fr_previous[i] * w for i, w in enumerate(issue_obj.value_weights.values())])

                if estimated_current < estimated_previous:
                    concession = True

        if len(not_changed) != len(self.issues) and concession:
            for issue_obj in not_changed:
                issue_obj.weight += self.alpha * (1. - math.pow(time, self.beta))

        total_issue_weights = sum([issue_obj.weight for issue_obj in self.issues.values()])

        for issue_obj in self.issues.values():
            issue_obj.weight /= total_issue_weights + 1e-10

    def get_utility(self, bid: Bid) -> float:
        if bid is None:
            return 0

        total = 0.

        for issue_name, issue_obj in self.issues.items():
            total += issue_obj.get_utility(bid.getValue(issue_name))

        return total


class Issue:
    weight: float = 0.0
    value_weights: dict
    value_counter: dict
    gamma: float = .25

    def __init__(self, values: DiscreteValueSet, **kwargs):
        self.value_weights = {value: 1. for value in values}
        self.value_counter = {value: 1. for value in values}

        self.weight = 1. / kwargs["n"]

    def update(self, value: Value, **kwargs):
        if value is None:
            return

        self.value_counter[value] += 1.

        max_value = max(self.value_counter.values()) + 1e-10

        self.value_weights = {value: math.pow(self.value_counter[value], self.gamma) / math.pow(max_value, self.gamma)
                              for value in self.value_weights.keys()}

    def get_utility(self, value: Value) -> float:
        if value is None:
            return 0.

        return self.weight * self.value_weights[value]
