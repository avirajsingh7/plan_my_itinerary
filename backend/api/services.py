import requests
import json
from django.conf import settings
from fuzzywuzzy import fuzz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GeminiAPIClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    def __init__(self, api_key):
        self.api_key = api_key

    def get_places_to_visit(self, destination, num_of_days, must_includes):
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
    def _create_prompt(destination, num_of_days, must_includes):
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
    BASE_SEARCH_URL = "https://api.content.tripadvisor.com/api/v1/location/search"
    BASE_DETAILS_URL = "https://api.content.tripadvisor.com/api/v1/location/{place_id}/details"
    BASE_IMAGE_URL = "https://api.content.tripadvisor.com/api/v1/location/{place_id}/photos"

    def __init__(self, api_key):
        self.api_key = api_key
        
    @staticmethod
    def is_match_place_name(query, result, threshold=50):
        return fuzz.ratio(query.lower(), result.lower()) >= threshold

    def get_tourist_place_id(self, place_name, destination):
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

    def get_place_details(self, place_id):
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
    def _parse_place_details(data):
        address_obj = data.get('address_obj', {})
        return {
            "id": data.get('location_id'),
            "name": data.get('name'),
            "street1": address_obj.get('street1',None),
            "street2": address_obj.get('street2',None),
            "city": address_obj.get('city',None),
            "state": address_obj.get('state',None),
            "country": address_obj.get('country',None),
            "postalcode": address_obj.get('postalcode',None),
            "address_string": address_obj.get('address_string',None),
            "latitude": data.get('latitude',None),
            "longitude": data.get('longitude',None),
            "ranking": (data.get('ranking_data', {}).get('ranking_string')
                               if data.get('ranking_data') else None),
            "rating": data.get('rating',None),
        }

    def get_place_images(self, place_id):
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
    def _parse_image(image,place_id):
        parsed_image = {}
        
        for size in ['thumbnail', 'small', 'medium', 'large', 'original']:
            if size in image['images'] and image['images'][size] is not None:
                parsed_image[size] = image['images'][size].get('url')
            else:
                parsed_image[size] = None
            parsed_image['location'] = place_id

        return parsed_image


class EmailService:
    @staticmethod
    def send_verification_email(email_to, token):
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

gemini_client = GeminiAPIClient(settings.GEMINI_API_KEY)
trip_advisor_client = TripAdvisorAPIClient(settings.TRIPADVISOR_API_KEY)