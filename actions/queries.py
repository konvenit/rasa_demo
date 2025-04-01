from pydantic import BaseModel
from typing import List, Optional
import requests
from datetime import datetime
import json
import os

BACKEND_URL = "http://host.docker.internal:3002/api/rasa/v1"
API_URL = "https://api.yourgptservice.com/v1/chat/completions"


class ValidityExtensionRequest(BaseModel):
    person_id: str
    tender_id: str
    offer_valid_until: str
    negotiation_ids: List[str]

class TenderResponse(BaseModel):
    tender_id: int
    service_type_name: str
    offer_valid_until: str
    new_offer_valid_until: Optional[str] = None
    validity_expired: bool
    project_name: str
    negotiations: List[dict]

def get_tenders(project_id: str) -> TenderResponse:
    """
    Retrieve tenders for a specific project.
    
    Args:
        project_id: The ID of the project to retrieve validity extensions for
        
    Returns:
        TenderResponse: Information about the validity extensions
        
    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    url = f"{BACKEND_URL}/validity_extensions?project_id={project_id}"
    response = requests.get(url)
    
    return TenderResponse(**response.json())

def create_validity_extension(
    person_id: str,
    tender_id: str,
    offer_valid_until: str,
    negotiation_ids: List[str]
) -> dict:
    """
    Create a validity extension for a tender.
    
    Args:
        person_id: The ID of the person creating the extension
        tender_id: The ID of the tender to extend
        offer_valid_until: New validity date in format DD.MM.YYYY
        negotiation_ids: List of negotiation IDs to include in the extension
        
    Returns:
        dict: Response from the API
        
    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    url = f"{BACKEND_URL}/validity_extensions"
    
    data = ValidityExtensionRequest(
        person_id=str(person_id),
        tender_id=str(tender_id),
        offer_valid_until=offer_valid_until,
        negotiation_ids=negotiation_ids
    )
    
    response = requests.post(url, json=data.dict())
    response.raise_for_status()
    
    return response.json()

def format_date(date_obj: datetime) -> str:
    """
    Format a datetime object to DD.MM.YYYY format.
    
    Args:
        date_obj: The datetime object to format
        
    Returns:
        str: Formatted date string
    """
    return date_obj.strftime("%d.%m.%Y")

def parse_hotel_selection(user_input: str, hotel_count: int) -> List[int]:
    """
    Use GPT-4o-mini to parse user input and return hotel indices.
    
    Args:
        user_input: The user's input text about which hotels they want to select
        hotel_count: The total number of hotels available
        
    Returns:
        List[int]: List of hotel indices (1-based)
        
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
        
    prompt = f"""
    Based on the user's input: "{user_input}", determine which hotel indices they want to select.
    
    Context:
    - There are {hotel_count} hotels available, numbered from 1 to {hotel_count}
    - The user's input could be in formats like: "all", "1,2,3", "only 1", "1 and 2"
    - If the input is "all", return all indices from 1 to {hotel_count}
    - Return only valid indices between 1 and {hotel_count}
    
    Return only a JSON array of integers representing the selected hotel indices. For example: [1, 3, 5]
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,  # Low temperature for more deterministic responses
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        indices = json.loads(result["choices"][0]["message"]["content"])
        
        # Ensure the result is a list of integers
        if isinstance(indices, list):
            return [int(idx) for idx in indices if isinstance(idx, (int, str)) and str(idx).isdigit() and 1 <= int(idx) <= hotel_count]
        return []
    
    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error parsing hotel selection: {str(e)}")
        # Fall back to simple parsing if the API call fails
        if user_input.lower() == "all":
            return list(range(1, hotel_count + 1))
        else:
            import re
            return [int(d) for d in re.findall(r'\d+', user_input) if d.isdigit() and 1 <= int(d) <= hotel_count]
