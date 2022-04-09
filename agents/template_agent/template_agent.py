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
from agents.template_agent.utils import *
from agents.template_agent.opponent_model import OpponentModel
from agents.template_agent.acceptance_strategy import AcceptanceStrategy
from agents.template_agent.bidding_strategy import BiddingStrategy
from agents.template_agent.learning_model import LearningModel


class TemplateAgent(DefaultParty):
    """
        Template Agent
    """
    NAME: str = "Template Agent"

    def __init__(self):
        super(TemplateAgent, self).__init__()

        # Initiate attributes
        self.domain: Domain = None
        self.parameters: Parameters = None
        self.profile: LinearAdditiveUtilitySpace = None
        self.progress: ProgressTime = None
        self.me: PartyId = None
        self.other: str = None
        self.settings: Settings = None
        self.storage_dir: str = None

        self.last_received_bid: Bid = None
        self.last_generated_bid: Bid = None

        # Modules
        self.opponent_model: OpponentModel = None
        self.acceptance_strategy: AcceptanceStrategy = None
        self.bidding_strategy: BiddingStrategy = None
        self.learning_model: LearningModel = None

        self.log("%s is initialized." % self.NAME)

    def notifyChange(self, data: Inform):
        """
            This method will be called when an information received.
        @param data: Information
        @return: None
        """
        # a Settings message is the first message that will be sent to your
        # agent containing all the information about the negotiation session.
        if isinstance(data, Settings):
            self.settings = cast(Settings, data)
            self.me = self.settings.getID()

            # progress towards the deadline has to be tracked manually through the use of the Progress object
            self.progress = self.settings.getProgress()

            self.parameters = self.settings.getParameters()
            self.storage_dir = self.parameters.get("storage_dir")

            self.parameters.get("")

            if str(self.settings.getProtocol().getURI()) == "Learn":
                self.getConnection().send(LearningDone(self.me))
                return

            # the profile contains the preferences of the agent over the domain
            profile_connection = ProfileConnectionFactory.create(
                data.getProfile().getURI(), self.getReporter()
            )
            self.profile = profile_connection.getProfile()
            self.domain = self.profile.getDomain()
            profile_connection.close()

            # Initiate Agent
            self.initiate()

        # ActionDone informs you of an action (an offer or an accept)
        # that is performed by one of the agents (including yourself).
        elif isinstance(data, ActionDone):
            action = cast(ActionDone, data).getAction()
            actor = action.getActor()

            # ignore action if it is our action
            if actor != self.me:
                # If the first offer is received, initiate learn model
                if self.other is None:
                    self.other = str(actor).rsplit("_", 1)[0]
                    self.learning_model.load_data(self.storage_dir, self.other)

                    self.log("Data loaded.")

                self.other = str(actor).rsplit("_", 1)[0]
                # process action done by opponent
                self.received_bid(action)
        # YourTurn notifies you that it is your turn to act
        elif isinstance(data, YourTurn):
            # execute a turn
            self.run()

        # Finished will be send if the negotiation has ended (through agreement or deadline)
        elif isinstance(data, Finished):
            # Save data
            if self.learning_model is not None:
                self.learning_model.save_data(self.storage_dir, self.other)
                self.log("%s data is saved." % self.other)

            # terminate the agent MUST BE CALLED
            self.log("%s is terminating." % self.NAME)
            super().terminate()
        else:
            self.getReporter().log(logging.WARNING, "Ignoring unknown info " + str(data))

    def initiate(self):
        # Initiate Components
        self.opponent_model = OpponentModel(self.domain, self.profile, self.progress)
        self.bidding_strategy = BiddingStrategy(self.profile, self.progress)
        self.acceptance_strategy = AcceptanceStrategy(self.profile, self.progress)
        self.learning_model = LearningModel(self.profile, self.progress)

        # Load data if other agent is known
        if self.other is not None:
            self.learning_model.load_data(self.storage_dir, self.other)

            self.log("Data loaded.")

        self.log("%s is ready." % self.NAME)

    def getCapabilities(self) -> Capabilities:
        """
            Capabilities of Agent
        @return: Capabilities
        """
        return Capabilities(
            set(["SAOP", "Learn"]),
            set(["geniusweb.profile.utilityspace.LinearAdditive"]),
        )

    def send_action(self, action: Action):
        """
            Send an action
        @param action: Action can be Offer or Accept.
        @return: None
        """
        self.getConnection().send(action)

    def getDescription(self) -> str:
        """
            Description of your agent.
        @return: Description as String
        """
        return "%s" % self.NAME

    def received_bid(self, action: Action):
        """
            This method will be called when an Action received.
        @param action: Action can be Offer or Accept
        @return: None
        """
        if isinstance(action, Offer):
            # If an offer received.
            # create opponent model if it was not yet initialised
            if self.opponent_model is None:
                self.opponent_model = OpponentModel(self.domain, self.profile, self.progress)

            # create bidding strategy if it was not yet initialised
            if self.bidding_strategy is None:
                self.bidding_strategy = BiddingStrategy(self.profile, self.progress)

            # Received bid
            bid = cast(Offer, action).getBid()

            # update opponent model with bid
            self.opponent_model.update(bid)
            # update bidding strategy with bid
            self.bidding_strategy.received_bid(bid)
            # update learn model with bid
            if self.learning_model is not None:
                self.learning_model.receive_bid(bid)
            # set bid as last received
            self.last_received_bid = bid

            self.log("Received Bid: %f" % get_utility(self.profile, self.last_received_bid))

        elif isinstance(action, Accept):  # If opponent agent accepts my offer.
            self.log("Opponent Accepted - Utility: %f" % get_utility(self.profile, self.last_generated_bid))

    def run(self):
        """
            Generate agent's action (Offer or Accept)
        @return: None
        """
        # Generated bid by bidding strategy if the agent will not accept.
        bid = self.bidding_strategy.generate()
        self.last_generated_bid = bid

        if bid is None:
            return

        # Check acceptance
        if self.acceptance_strategy.is_accepted(self.last_received_bid, bid):
            self.log("Accepted - My Bid: %f, Received: %f" % (get_utility(self.profile, bid), get_utility(self.profile, self.last_received_bid)))
            self.getConnection().send(Accept(self.me, self.last_received_bid))
        else:
            self.log("Offered: %f" % get_utility(self.profile, bid))
            self.learning_model.save_bid(bid)
            self.getConnection().send(Offer(self.me, bid))

    def log(self, text: str, will_print: bool = True):
        """
            Log information.
        @param text: Log Text as String
        @param will_print: Log text will be printed on console.
        @return: None
        """
        if will_print:
            print(text)

        self.getReporter().log(logging.INFO, text)
