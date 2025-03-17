from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

class ActionCheckSufficientFunds(Action):
    def name(self) -> Text:
        return "action_check_sufficient_funds"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # hard-coded balance for tutorial purposes. in production this
        # would be retrieved from a database or an API
        logger = logging.getLogger(__name__)
        metadata = tracker.get_slot("session_started_metadata")
        user_id = metadata.get("userId")
        logger.info("xxxxxxxxxxxxxxxxxxxxxxxxxxx user_id: %s", user_id)
        logger.info(metadata)
        balance =  int(metadata.get("balance"))
        transfer_amount = tracker.get_slot("amount")
        has_sufficient_funds = transfer_amount <= balance

        return [SlotSet("has_sufficient_funds", has_sufficient_funds)]
