from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
import requests

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
        # because its running inside docker, we need to use the host.docker.internal
        # to access the host machine
        # if you are not running inside docker, you can use localhost
        api_url = "http://host.docker.internal:3002/api/rasa/v1/ping.json"
        params = {"person_id": user_id, "amount": transfer_amount}
        try:
          logger.info("xxxxxxxxxxxxxxxxxxxxxxxxxxx api_url: %s", api_url)
          response = requests.get(api_url, params=params)
          # Raise an exception if the request was unsuccessful
          response.raise_for_status()
          # Parse the response as JSON
          data = response.json()
          print("Response from API:", data)
          logger.info("xxxxxxxxxxxxxxxxxxxxxxxxxxx data: %s", data)
          # direct message to the user

          dispatcher.utter_message(text=data["message"])
          return [SlotSet("has_sufficient_funds", has_sufficient_funds)]

        except requests.exceptions.RequestException as e:
           logger.error("Request failed: %s", e)
           print("An error occurred:", e)
