from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.DiscreteValueSet import DiscreteValueSet
from geniusweb.issuevalue.Domain import Domain
from geniusweb.issuevalue.Value import Value
from agents.template_agent.utils import *


class OpponentModel:
    """
        Opponent Model
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    offers: list    # Received bids
    domain: Domain  # Agent's domain
    issues: dict    # Issues

    def __init__(self, domain: Domain, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.domain = domain
        self.profile = profile
        self.progress = progress
        self.offers = []

        self.issues = {issue: Issue(values) for issue, values in domain.getIssuesValues().items()}

    def update(self, bid: Bid, **kwargs):
        """
            This method will be called when a bid received.
        @param bid: Received bid
        @return: None
        """

        # Add into offers list
        if bid is None:
            return

        self.offers.append(bid)

        # Call each issue object with corresponding received value.
        for issue_name, issue_obj in self.issues.items():
            issue_obj.update(bid.getValue(issue_name), **kwargs)

    def get_utility(self, bid: Bid) -> float:
        """
            This method calculates estimated utility.
        @param bid: The bid will be calculated.
        @return: Estimated Utility
        """
        if bid is None:
            return 0.0

        total = 0.0

        for issue_name, issue_obj in self.issues.items():
            total += issue_obj.get_utility(bid.getValue(issue_name))

        return total


class Issue:
    """
        This class can be used to estimate issue weight and value weights.
    """
    weight: float = 0.0    # Issue Weight
    value_weights: dict    # Value Weights

    def __init__(self, values: DiscreteValueSet, **kwargs):
        # Initial value weights are zero
        self.value_weights = {value: 0.0 for value in values}

    def update(self, value: Value, **kwargs):
        """
            This method will be called when a bid received.
        @param value: Received bid
        @return: None
        """
        if value is None:
            return

        pass

    def get_utility(self, value: Value) -> float:
        """
            Calculate estimated utility of the issue with value
        @param value: Value of Issue
        @return: Estimated Utility
        """
        if value is None:
            return 0.0

        return self.weight * self.value_weights[value]
