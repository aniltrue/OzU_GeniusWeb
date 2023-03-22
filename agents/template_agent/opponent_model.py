from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.DiscreteValueSet import DiscreteValueSet
from geniusweb.issuevalue.Domain import Domain
from geniusweb.issuevalue.Value import Value
from agents.template_agent.utils import *


class OpponentModel:
    """
        Opponent Model

        As a default, Classical Frequentist Opponent Model is implemented in Hardheaded.
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    offers: list    # Received bids
    domain: Domain  # Agent's domain
    issues: dict    # Issues
    alpha: float    # Parameter for Issue Weight update

    def __init__(self, domain: Domain, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        """
            Constructor
        :param domain: Negotiation domain
        :param profile: Linear additive profile
        :param progress: Negotiation session progress time
        :param kwargs: Other
        """
        self.domain = domain
        self.profile = profile
        self.progress = progress
        self.offers = []

        self.alpha = 0.1

        self.issues = {issue: Issue(values) for issue, values in domain.getIssuesValues().items()}
        self.normalize()

    def update(self, bid: Bid, **kwargs):
        """
            This method is called when a bid received.
        :param bid: Received bid
        :return: Nothing
        """

        # Add into offers list
        if bid is None:
            return

        self.offers.append(bid)

        # Call each issue object with corresponding received value.
        for issue_name, issue_obj in self.issues.items():
            issue_obj.update(bid.getValue(issue_name), **kwargs)

        # Update issue weights
        if len(self.offers) >= 2:
            self.update_issue_weights()

        # Renormalize
        self.normalize()

    def update_issue_weights(self):
        """
            This method updates the issue weights by considering last two consecutive bids.
        :return: Nothing
        """
        t = get_time(self.progress)

        last_two_bids = self.offers[-2:]

        for issue_name, issue_obj in self.issues.items():
            if last_two_bids[0].getValue(issue_name) == last_two_bids[1].getValue(issue_name):
                issue_obj.weight += self.alpha * (1. - t)

    def get_utility(self, bid: Bid) -> float:
        """
            This method calculates estimated utility.
        :param bid: The bid will be calculated.
        :return: Estimated Utility
        """
        if bid is None:
            return 0.0

        total = 0.0

        for issue_name, issue_obj in self.issues.items():
            total += issue_obj.get_utility(bid.getValue(issue_name))

        return total

    def normalize(self):
        """
            This method normalize the Value and Issue weights.
             - Value weight must be in range [0.0, 1.0]
             - Sum of issue weights must be 1.0
        :return: Nothing
        """
        total_issue_weight = 0.
        for issue_name, issue_obj in self.issues.items():
            total_issue_weight += issue_obj.weight
            max_val = max(issue_obj.value_weights.values())

            for value_name in issue_obj.value_weights:
                issue_obj.value_weights[value_name] /= max_val

        for issue_obj in self.issues.values():
            issue_obj.weight /= total_issue_weight

class Issue:
    """
        This class can be used to estimate issue weight and value weights.
    """
    weight: float = 1.0    # Issue Weight
    value_weights: dict    # Value Weights

    def __init__(self, values: DiscreteValueSet, **kwargs):
        """
            Constructor
        :param values: The set of discrete value set
        :param kwargs: Others
        """
        # Initial value weights are zero
        self.value_weights = {value: 0.0 + 1e-10 for value in values}

    def update(self, value: Value, **kwargs):
        """
            This method will be called when a bid received.
        :param value: Received bid
        :return: None
        """
        if value is None:
            return

        self.value_weights[value] += 1.

    def get_utility(self, value: Value) -> float:
        """
            Calculate estimated utility of the issue with value
        :param value: The value of Issue
        :return: Estimated Utility
        """
        if value is None:
            return 0.0

        return self.weight * self.value_weights[value]
