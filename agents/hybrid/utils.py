import math

from geniusweb.bidspace.AllBidsList import AllBidsList
from geniusweb.issuevalue.Bid import Bid
from geniusweb.profile.utilityspace.LinearAdditiveUtilitySpace import (
    LinearAdditiveUtilitySpace,
)
from geniusweb.progress.ProgressTime import ProgressTime
from time import time


"""
    Some useful functions
"""


def get_utility(profile: LinearAdditiveUtilitySpace, bid: Bid) -> float:
    """
        Utility of a bid.
    @param profile: Profile
    @param bid: Bid
    @return: Utility of bid
    """
    return float(profile.getUtility(bid))


def get_bid_at(profile: LinearAdditiveUtilitySpace, utility: float) -> Bid:
    """
        Get the closest bid to desired utility
    @param profile: Profile
    @param utility: Desired Utility
    @return: The closest bid to desired utility
    """
    domain = profile.getDomain()
    all_bids = AllBidsList(domain)

    closest = all_bids.get(0)

    for i in range(all_bids.size()):
        if abs(utility - get_utility(profile, all_bids.get(i))) < abs(utility - get_utility(profile, closest)):
            closest = all_bids.get(i)

    return closest


def get_bids_at(profile: LinearAdditiveUtilitySpace, utility: float, lower_bound: float = 0.02,
                upper_bound: float = 0.02) -> list:
    """
        Get bids between [utility - lower_bound, utility + upper_bound]
    @param profile: Profile
    @param utility: Desired Utility
    @param lower_bound: Lower bound of the Range
    @param upper_bound: Upper bound of the Range
    @return: List of bids in that range
    """
    domain = profile.getDomain()
    all_bids = AllBidsList(domain)

    bids = []

    for i in range(1, all_bids.size()):
        if utility - lower_bound <= get_utility(profile, all_bids.get(i)) <= utility + upper_bound:
            bids.append(all_bids.get(i))

    return bids


def get_min_max_utility(profile: LinearAdditiveUtilitySpace) -> (float, float):
    """
        Get the minimum and maximum utility value in bid space
    @param profile: Profile
    @return: Minimum and maximum utility as float
    """
    domain = profile.getDomain()
    all_bids = AllBidsList(domain)

    min_utility = 1.0
    max_utility = 0.0

    for i in range(all_bids.size()):
        min_utility = min(get_utility(profile, all_bids.get(i)), min_utility)
        max_utility = max(get_utility(profile, all_bids.get(i)), max_utility)

    return min_utility, max_utility


def get_mean_stdev(profile: LinearAdditiveUtilitySpace) -> (float, float):
    """
        Mean and standard derivation of bid space
    @param profile: Profile
    @return: Mean and standard derivation values as float
    """
    domain = profile.getDomain()
    all_bids = AllBidsList(domain)

    utilities = [get_utility(profile, all_bids.get(i)) for i in range(all_bids.size())]

    mean = sum(utilities) / len(utilities)

    stdev = math.sqrt(sum([math.pow(utility - mean, 2.) for utility in utilities]) / len(utilities))

    return mean, stdev


def get_time(progress: ProgressTime) -> float:
    """
        Get current time. Initially, it is 0; and it is 1 at the end of the negotiation.
    @param progress: ProgressTime object to calculate t
    @return: Current time as float in range [0, 1]
    """
    return progress.get(int(time() * 1000))


def get_reservation_value(profile: LinearAdditiveUtilitySpace) -> float:
    """
        Reservation bid's utility if exists. If not exist, it returns -1
    @param profile: Profile
    @return: Utility of Reservation Bid
    """
    if profile.getReservationBid() is not None:
        return get_utility(profile, profile.getReservationBid())

    return -1.0
