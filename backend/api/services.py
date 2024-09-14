import requests
import json
from django.conf import settings
from fuzzywuzzy import fuzz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GeminiAPIClient:
    """Client for interacting with the Gemini API to generate itinerary content."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    def __init__(self, api_key : str):
        """Initialize the client with the API key."""
        self.api_key = api_key

    def get_places_to_visit(self, destination:str, num_of_days:int, must_includes:list) -> dict:
        """
        Generate a list of places to visit based on the given parameters.

        Args:
            destination (str): The travel destination.
            num_of_days (int): Number of days for the trip.
            must_includes (list): List of places that must be included in the itinerary.

        Returns:
            dict: A dictionary containing the generated itinerary, or None if an error occurs.
        """
        prompt = self._create_prompt(destination, num_of_days, must_includes)
        request_body = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": self.api_key}
        
        try:
            response = requests.post(self.BASE_URL, params=params, json=request_body)
            response.raise_for_status()
            text_with_json = response.json()['candidates'][0]['content']['parts'][0]['text']
            json_string = text_with_json.replace('```json\n', '').replace('\n```', '')
            return json.loads(json_string)
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Error in Gemini API request: {str(e)}")
            return None

    @staticmethod
    def _create_prompt(destination : str, num_of_days : int, must_includes : list) -> str:
        """
        Create a prompt for the Gemini API based on the given parameters.

        Args:
            destination (str): The travel destination.
            num_of_days (int): Number of days for the trip.
            must_includes (list): List of places that must be included in the itinerary.

        Returns:
            str: The generated prompt.
        """
        prompt = f"""
        Provide a JSON response listing top tourist places around {destination} for a {num_of_days}-day trip. 
        For each place, include the recommended duration to spend there and a 60-word description about the place. 
        Ensure it includes {", ".join(must_includes)} if applicable, in the following JSON format:

        {{
        "itinerary": [
            {{
                "day_number": "integer",
                "time_of_day": "morning/afternoon/evening",
                "place_name": "name of the place",
                "duration": "time at the place",
                "description": "60-word description",
                "tourist_place": true/false
            }}
        ]
        }}
        """
        return prompt


class TripAdvisorAPIClient:
    """Client for interacting with the TripAdvisor API to fetch place details and images."""

    BASE_SEARCH_URL = "https://api.content.tripadvisor.com/api/v1/location/search"
    BASE_DETAILS_URL = "https://api.content.tripadvisor.com/api/v1/location/{place_id}/details"
    BASE_IMAGE_URL = "https://api.content.tripadvisor.com/api/v1/location/{place_id}/photos"

    def __init__(self, api_key : str):
        """Initialize the client with the API key."""
        self.api_key = api_key
        
    @staticmethod
    def is_match_place_name(query : str, result : str, threshold : int = 50) -> bool:
        """
        Check if the query matches the result using fuzzy string matching.

        Args:
            query (str): The search query.
            result (str): The result to compare against.
            threshold (int): The minimum similarity score to consider a match.

        Returns:
            bool: True if the strings match, False otherwise.
        """
        return fuzz.ratio(query.lower(), result.lower()) >= threshold

    def get_tourist_place_id(self, place_name : str, destination : str) -> str:
        """
        Get the TripAdvisor location ID for a given place name and destination.

        Args:
            place_name (str): The name of the place to search for.
            destination (str): The destination to search within.

        Returns:
            str: The TripAdvisor location ID if found, None otherwise.
        """
        params = {"key": self.api_key, "searchQuery": f"{place_name}, {destination}"}
        try:
            response = requests.get(self.BASE_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            results = response.json().get('data', [])
            for result in results:
                if self.is_match_place_name(place_name, result['name']):
                    return result['location_id']
        except requests.RequestException as e:
            print(f"Error in TripAdvisor search request: {str(e)}")
        return None

    def get_place_details(self, place_id : str) -> dict:
        """
        Get details for a specific place using its TripAdvisor location ID.

        Args:
            place_id (str): The TripAdvisor location ID.

        Returns:
            dict: A dictionary containing place details, or None if an error occurs.
        """
        url = self.BASE_DETAILS_URL.format(place_id=place_id)
        params = {"key": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self._parse_place_details(data)
        except requests.RequestException as e:
            print(f"Error in TripAdvisor details request: {str(e)}")
        return None

    @staticmethod
    def _parse_place_details(place_details : dict) -> dict:
        """
        Parse the raw place details data into a structured format.

        Args:
            place_details (dict): The raw place details data from TripAdvisor API.

        Returns:
            dict: A dictionary containing parsed place details.
        """
        address_obj = place_details.get('address_obj', {})
        return {
            "id": place_details.get('location_id'),
            "name": place_details.get('name'),
            "street1": address_obj.get('street1',None),
            "street2": address_obj.get('street2',None),
            "city": address_obj.get('city',None),
            "state": address_obj.get('state',None),
            "country": address_obj.get('country',None),
            "postalcode": address_obj.get('postalcode',None),
            "address_string": address_obj.get('address_string',None),
            "latitude": place_details.get('latitude',None),
            "longitude": place_details.get('longitude',None),
            "ranking": (place_details.get('ranking_data', {}).get('ranking_string')
                               if place_details.get('ranking_data') else None),
            "rating": place_details.get('rating',None),
        }

    def get_place_images(self, place_id : str) -> list[dict]:
        """
        Get images for a specific place using its TripAdvisor location ID.

        Args:
            place_id (str): The TripAdvisor location ID.

        Returns:
            list: A list of dictionaries containing image details, or None if an error occurs.
        """
        url = self.BASE_IMAGE_URL.format(place_id=place_id)
        params = {"key": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get('data', [])
            return [self._parse_image(image,place_id) for image in data]
        except requests.RequestException as e:
            print(f"Error in TripAdvisor image request: {str(e)}")
        return None
    
    @staticmethod
    def _parse_image(image : dict, place_id : str) -> dict:
        """
        Parse the raw image data into a structured format.

        Args:
            image (dict): The raw image data from TripAdvisor API.
            place_id (str): The TripAdvisor location ID associated with the image.

        Returns:
            dict: A dictionary containing parsed image details.
        """
        parsed_image = {}
        
        for size in ['thumbnail', 'small', 'medium', 'large', 'original']:
            if size in image['images'] and image['images'][size] is not None:
                parsed_image[size] = image['images'][size].get('url')
            else:
                parsed_image[size] = None
            parsed_image['location'] = place_id

        return parsed_image


class EmailService:
    """Service for sending verification emails."""

    @staticmethod
    def send_verification_email(email_to : str, token : str) -> bool:
        """
        Send a verification email to the user.

        Args:
            email_to (str): The recipient's email address.
            token (str): The verification token.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        smtp_server = settings.EMAIL_HOST
        smtp_port = settings.EMAIL_PORT

        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = email_to
        msg['Subject'] = "Email Verification for PlanMyItinerary"

        verification_link = f"{settings.BACKEND_URL}/api/user/verify-email/{token}"
        body = f'Click the link below to verify your email:\n\n{verification_link}'
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)
            return True
        except smtplib.SMTPException as e:
            print(f"Failed to send verification email to {email_to}: {str(e)}")
            return False
        
        
# Initialize service instances
email_service = EmailService()
gemini_client = GeminiAPIClient(settings.GEMINI_API_KEY)
trip_advisor_client = TripAdvisorAPIClient(settings.TRIPADVISOR_API_KEY)