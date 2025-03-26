from typing import Any, Dict, List, Text
from datetime import datetime, timedelta

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from queries import get_tenders, create_validity_extension, format_date


class ActionFetchTenderDetails(Action):
    """
    Action to retrieve tender details from the API and set slots.
    This only retrieves data and sets slots, no messaging.
    """
    def name(self) -> Text:
        return "action_fetch_tender_details"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]
    ) -> List[Dict[Text, Any]]:
        project_id = tracker.get_slot("project_id")
        
        if not project_id:
            return []
        
        try:
            tender_response = get_tenders(project_id)
            
            hotels = []
            for negotiation in tender_response.negotiations:
                hotels.append({
                    "id": str(negotiation.get("negotiation_id")),
                    "name": negotiation.get("supplier_name"),
                    "phone": negotiation.get("phone_number")
                })
            
            return [
                SlotSet("project_name", tender_response.project_name),
                SlotSet("tender_id", str(tender_response.tender_id)),
                SlotSet("tender_type", tender_response.service_type_name),
                SlotSet("validity_expired", tender_response.validity_expired),
                SlotSet("validity_extension_offer", tender_response.new_offer_valid_until),
                SlotSet("offer_valid_until", tender_response.offer_valid_until),
                SlotSet("hotel_list", hotels)
            ]
            
        except Exception as e:
            print(f"Error retrieving tender details: {str(e)}")
            return []


class ActionExtendValidity(Action):
    """
    Action to extend the validity date.
    Reads from slots and sends the API request.
    """
    def name(self) -> Text:
        return "action_extend_validity"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]
    ) -> List[Dict[Text, Any]]:

        person_id = tracker.sender_id
        tender_id = tracker.get_slot("tender_id")
        validity_extension_offer = tracker.get_slot("validity_extension_offer")
        selected_hotels = tracker.get_slot("selected_hotels")
        
        if not all([tender_id, validity_extension_offer, selected_hotels]):
            return [SlotSet("extension_success", False)]
        
        try:
            # Call the API to extend validity
            response = create_validity_extension(
                person_id=person_id,
                tender_id=tender_id,
                offer_valid_until=validity_extension_offer,
                negotiation_ids=selected_hotels
            )
            
            # Return success slot
            return [SlotSet("extension_success", True)]
            
        except Exception as e:
            # Log the error but don't send messages
            print(f"Error extending validity: {str(e)}")
            return [SlotSet("extension_success", False)]