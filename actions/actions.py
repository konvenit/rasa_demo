from typing import Any, Dict, List, Text
from datetime import datetime, timedelta

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .queries import get_tenders, create_validity_extension, format_date, parse_hotel_selection


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
        metadata = tracker.get_slot("session_started_metadata")
        project_id = metadata["projectId"]
        user_id = metadata.get("userId")

        try:
            tender_response = get_tenders(project_id)
            
            hotels = []
            for negotiation in tender_response.negotiations:
                hotels.append({
                    "id": str(negotiation.get("negotiation_id")),
                    "name": negotiation.get("supplier_name"),
                    "phone": negotiation.get("phone_number")
                })

            all_hotels_numbered_list = "\n" + "".join([f"- {i+1} - {h['name']} \n" for i, h in enumerate(hotels)]) + "\n"
            if not tender_response.new_offer_valid_until:
                tender_response.new_offer_valid_until = tender_response.offer_valid_until

            return [
                SlotSet("project_name", tender_response.project_name),
                SlotSet("tender_id", str(tender_response.tender_id)),
                SlotSet("tender_type", tender_response.service_type_name),
                SlotSet("validity_expired", tender_response.validity_expired),
                SlotSet("validity_extension_offer", tender_response.new_offer_valid_until),
                SlotSet("offer_valid_until", tender_response.offer_valid_until),
                SlotSet("hotel_list", hotels),
                SlotSet("hotels_string", all_hotels_numbered_list)
            ]
            
        except Exception as e:
            print(f"Error retrieving tender details: {str(e)}")
            return []
        
class ActionGetSelectedHotels(Action):
    def name(self):
        return "action_get_selected_hotels"

    def run(self, dispatcher, tracker, domain):
        hotels = tracker.get_slot("hotel_list")
        user_input = tracker.get_slot("selected_hotels")

        if not hotels:
            dispatcher.utter_message(text="No hotels are available.")
            return []
            
        # Handle empty input
        if not user_input:
            dispatcher.utter_message(text="No hotels were selected. Please provide a valid input.")
            return []
            
        # Use GPT-4o-mini to parse user input and get hotel indices
        try:
            hotel_indices = parse_hotel_selection(user_input, len(hotels))
            
            # Convert 1-based indices to hotels
            selected_hotels = [hotels[i - 1] for i in hotel_indices if 0 < i <= len(hotels)]
            
            if not selected_hotels:
                dispatcher.utter_message(text="No valid hotels were selected. Please try again.")
                return []
                
        except Exception as e:
            print(f"Error in hotel selection: {str(e)}")
            dispatcher.utter_message(text="There was an error processing your selection. Please try again.")
            return []

        selected_hotels_contacts = "\n".join([f"- {i + 1} - {hotel['name']} - {hotel['phone']}" for i, hotel in enumerate(selected_hotels)])

        return [
            SlotSet("selected_hotels", selected_hotels),
            SlotSet("selected_hotels_contacts", selected_hotels_contacts),
            SlotSet("select_hotels_ids", [h['id'] for h in selected_hotels])
        ]


class ActionExtendValidity(Action):
    """
    Action to extend the validity date.
    Reads from slots and sends the API request.
    """
    def name(self) -> Text:
        return "action_update_validity_extension"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]
    ) -> List[Dict[Text, Any]]:

        tender_id = tracker.get_slot("tender_id")
        validity_extension_offer = tracker.get_slot("validity_extension_offer")
        selected_hotels = tracker.get_slot("select_hotels_ids")

        metadata = tracker.get_slot("session_started_metadata")
        person_id = metadata.get("userId")

        
        if not all([tender_id, validity_extension_offer]):
            return [SlotSet("finalized_with_success", False)]
        
        try:
            # Call the API to extend validity
            response = create_validity_extension(
                person_id=person_id,
                tender_id=tender_id,
                offer_valid_until=validity_extension_offer,
                negotiation_ids=selected_hotels
            )
            
            # Return success slot
            if response.status_code == 200:
                return [SlotSet("finalized_with_success", True)]
            else:
                return [SlotSet("finalized_with_success", False)]
            
        except Exception as e:
            # Log the error but don't send messages
            print(f"Error extending validity: {str(e)}")
            return [SlotSet("finalized_with_success", False)]
        
