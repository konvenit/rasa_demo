from pydantic import BaseModel
from typing import List, Optional
import requests
from datetime import datetime

BACKEND_URL = "http://host.docker.internal:3002/api/rasa/v1"

class ValidityExtensionRequest(BaseModel):
    person_id: str
    tender_id: str
    offer_valid_until: str
    negotiation_ids: List[str]

class TenderResponse(BaseModel):
    tender_id: int
    service_type_name: str
    offer_valid_until: str
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
        person_id=person_id,
        tender_id=tender_id,
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