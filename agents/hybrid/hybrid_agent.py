import logging
import math
import os.path
import random
from typing import cast

from geniusweb.actions.Accept import Accept
from geniusweb.actions.Action import Action
from geniusweb.actions.LearningDone import LearningDone
from geniusweb.actions.Offer import Offer
from geniusweb.actions.PartyId import PartyId
from geniusweb.bidspace.AllBidsList import AllBidsList
from geniusweb.inform.ActionDone import ActionDone
from geniusweb.inform.Finished import Finished
from geniusweb.inform.Inform import Inform
from geniusweb.inform.Settings import Settings
from geniusweb.inform.YourTurn import YourTurn
from geniusweb.issuevalue.Domain import Domain
from geniusweb.party.Capabilities import Capabilities
from geniusweb.party.DefaultParty import DefaultParty
from geniusweb.profileconnection.ProfileConnectionFactory import (
    ProfileConnectionFactory,
)
from geniusweb.references.Parameters import Parameters
import pickle
from agents.hybrid.utils import *
from agents.hybrid.opponent_model import OpponentModel
from agents.hybrid.acceptance_strategy import AcceptanceStrategy
from agents.hybrid.bidding_strategy import BiddingStrategy
from agents.hybrid.learning_model import LearningModel


class HybridAgent(DefaultParty):
    """
        Hybrid Agent Implementation via Template Agent
    """
    NAME: str = "Hybrid Agent"

    def __init__(self):
        super(HybridAgent, self).__init__()

        self.domain: Domain = None
        self.parameters: Parameters = None
        self.profile: LinearAdditiveUtilitySpace = None
        self.progress: ProgressTime = None
        self.me: PartyId = None
        self.other: str = None
        self.settings: Settings = None
        self.storage_dir: str = None

        self.last_received_bid: Bid = None
        self.opponent_model: OpponentModel = None
        self.acceptance_strategy: AcceptanceStrategy = None
        self.bidding_strategy: BiddingStrategy = None
        self.learning_model: LearningModel = None

        self.log("%s is initialized." % self.NAME)

    def notifyChange(self, data: Inform):
        if isinstance(data, Settings):
            self.settings = cast(Settings, data)
            self.me = self.settings.getID()

            self.progress = self.settings.getProgress()

            self.parameters = self.settings.getParameters()
            self.storage_dir = self.parameters.get("storage_dir")

            self.parameters.get("")

            if str(self.settings.getProtocol().getURI()) == "Learn":
                self.getConnection().send(LearningDone(self.me))
                return

            profile_connection = ProfileConnectionFactory.create(
                data.getProfile().getURI(), self.getReporter()
            )
            self.profile = profile_connection.getProfile()
            self.domain = self.profile.getDomain()
            profile_connection.close()

            self.initiate()

        elif isinstance(data, ActionDone):
            action = cast(ActionDone, data).getAction()
            actor = action.getActor()

            if actor != self.me:
                if self.other is None:
                    self.other = str(actor).rsplit("_", 1)[0]
                    self.learning_model.load_data(self.storage_dir, self.other)

                    self.bidding_strategy.update(self.learning_model.data["min_value"], self.log)

                    self.log("Data loaded.")

                self.other = str(actor).rsplit("_", 1)[0]
                self.received_bid(action)
        elif isinstance(data, YourTurn):
            self.run()

        elif isinstance(data, Finished):
            if self.learning_model is not None:
                self.learning_model.save_data(self.storage_dir, self.other)
                self.log("%s data is saved." % self.other)

            self.log("%s is terminating." % self.NAME)
            super().terminate()
        else:
            self.getReporter().log(logging.WARNING, "Ignoring unknown info " + str(data))

    def initiate(self):
        self.opponent_model = OpponentModel(self.domain, self.profile, self.progress, log=self.log)
        self.bidding_strategy = BiddingStrategy(self.profile, self.progress)
        self.acceptance_strategy = AcceptanceStrategy(self.profile, self.progress)
        self.learning_model = LearningModel(self.profile, self.progress)

        if self.other is not None:
            self.learning_model.load_data(self.storage_dir, self.other)

            self.log("Data loaded.")

        self.bidding_strategy.update(self.learning_model.data["min_value"], self.log)

        self.log("%s is ready." % self.NAME)

    def getCapabilities(self) -> Capabilities:
        return Capabilities(
            set(["SAOP", "Learn"]),
            set(["geniusweb.profile.utilityspace.LinearAdditive"]),
        )

    def send_action(self, action: Action):
        self.getConnection().send(action)

    def getDescription(self) -> str:
        return "%s" % self.NAME

    def received_bid(self, action: Action):
        if isinstance(action, Offer):
            if self.opponent_model is None:
                self.opponent_model = OpponentModel(self.domain, self.profile, self.progress, log=self.log)

            if self.bidding_strategy is None:
                self.bidding_strategy = BiddingStrategy(self.profile, self.progress)

            bid = cast(Offer, action).getBid()

            self.opponent_model.update(bid)
            self.bidding_strategy.received_bid(bid)
            if self.learning_model is not None:
                self.learning_model.receive_bid(bid)

            self.last_received_bid = bid

    def run(self):
        bid = self.bidding_strategy.generate(log=self.log, opponent_model=self.opponent_model)

        if self.acceptance_strategy.is_accepted(self.last_received_bid, bid):
            self.log("Accepted - My Bid: %f, Received: %f" % (get_utility(self.profile, bid), get_utility(self.profile, self.last_received_bid)))
            self.getConnection().send(Accept(self.me, self.last_received_bid))
        else:
            self.log("Offered: %f" % get_utility(self.profile, bid))
            self.learning_model.save_bid(bid)
            self.getConnection().send(Offer(self.me, bid))

    def log(self, text: str, will_print: bool = False):
        if will_print:
            print(text)

        self.getReporter().log(logging.INFO, text)
