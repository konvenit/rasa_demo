from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

class ActionFetchTenderDetails(Action):
    def name(self):
        return "action_fetch_tender_details"

    def run(self, dispatcher, tracker, domain):
        
        # Define the API endpoint and parameters
        api_url = f"http://localhost:3002/api/rasa/v1/validity_extensions?project_id=309717"
        params = {"tender ID": "tender_id", "Date": "offer_valid_until"}  # Example parameters, modify based on your needs
        
        # Send GET request to the external API
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            # Assuming the response is a list of hotels
            hotels_data = response.json()  # Parse the JSON response
            hotels_dict = {hotel['supplier_name']: hotel['hotel_id'] for hotel in hotels_data}

            # Save the list of hotels into a slot for future use
            return [SlotSet("tender_hotels", hotels_dict)]
        
        else:
            # Handle error response
            dispatcher.utter_message(text="Sorry, I couldn't fetch the hotel details right now.")
            return []


class ActionCollectSelectedHotels(Action):
    def name(self):
        return "action_collect_selected_hotels"

    def run(self, dispatcher, tracker, domain):
        user_input = tracker.latest_message.get('text').lower()  # Capture user input
        
        # Get the list of selected hotels from the slot
        tender_hotels = tracker.get_slot('tender_hotels')
        
        if user_input == "all":
            selected_hotel_ids = list(tender_hotels.values())
        elif user_input in tender_hotels:
            selected_hotel_ids = [tender_hotels[user_input]]  # Get the specific hotel ID as a list
        else:
            # If the input is invalid, ask the user again
            dispatcher.utter_message(text="Sorry, I didn't understand that. Please select a hotel from the list.")
            return []

        # Store the selected hotel in the slot
        return [SlotSet("selected_hotel", selected_hotel_ids)]

class ActionUpdateValidityExtension(Action):

    def name(self):
        return "action_update_validity_extension"

    def run(self, dispatcher, tracker, domain) :
    # Get the selected hotels and their extension dates from the slots
        selected_hotels = tracker.get_slot('selected_hotels')
        extension_dates = tracker.get_slot('validity_extension_offer')
        
        if not selected_hotels or not extension_dates:
            dispatcher.utter_message(text="I couldn't find the hotel or extension date details.")
            return []

        # Prepare the data to send in the POST request
        hotels_data = dict()
        hotels_data['person_id']            = '5555'
        hotels_data['tender_id']            =  tracker.get_slot('tender_id')
        hotels_data['offer_valid_until']    =  tracker.get_slot('validity_extension_offer')
        hotels_data['negotiation_ids']      =  tracker.get_slot('selected_hotel')
        # Define the API endpoint for the POST request
        api_url = "http://localhost:3002/api/rasa/v1/validity_extensions"  # Replace with your API URL
        
        # Send the POST request with the hotel details
        response = requests.post(api_url, json={"hotels": hotels_data})

        if response.status_code == 200:
            dispatcher.utter_message(text="The hotel details have been successfully sent.")
        else:
            dispatcher.utter_message(text="There was an error sending the hotel details.")

        return []