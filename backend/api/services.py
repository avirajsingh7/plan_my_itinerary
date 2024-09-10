import requests
import json
from django.conf import settings
from fuzzywuzzy import fuzz
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GeminiAPIClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    def __init__(self, api_key):
        self.api_key = api_key

    def get_places_to_visit(self, destination, num_of_days, must_includes):
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
        request_body = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": self.api_key}
        response = requests.post(self.BASE_URL, params=params, json=request_body)
        
        text_with_json = response.json()['candidates'][0]['content']['parts'][0]['text']
        json_string = text_with_json.replace('```json\n', '').replace('\n```', '')
        return json.loads(json_string)


class TripAdvisorAPIClient:
    BASE_SEARCH_URL = "https://api.content.tripadvisor.com/api/v1/location/search"
    BASE_DETAILS_URL = "https://api.content.tripadvisor.com/api/v1/location/{place_id}/details"
    BASE_IMAGE_URL = "https://api.content.tripadvisor.com/api/v1/location/{place_id}/photos"

    def __init__(self, api_key):
        self.api_key = api_key
        
    @staticmethod
    def is_match_place_name(query, result, threshold=50):
        similarity = fuzz.ratio(query.lower(), result.lower())
        return similarity >= threshold

    def get_tourist_place_id(self, place_name, destination):
        params = {"key": self.api_key, "searchQuery": f"{place_name}, {destination}"}
        response = requests.get(self.BASE_SEARCH_URL, params=params)
        if response.status_code == 200:
            results = response.json().get('data', [])
            for result in results:
                if self.is_match_place_name(place_name, result['name']):
                    return result['location_id']
        return None

    def get_place_details(self, place_id):
        trip_adv_details_url = f"https://api.content.tripadvisor.com/api/v1/location/{place_id}/details"
        params = {"key": self.api_key}
        details_response = requests.get(trip_adv_details_url, params=params)

        if details_response.status_code == 200:
            data = details_response.json()
            address_obj = data.get('address_obj', {})
            return {
                "location_id": data.get('location_id'),
                "name": data.get('name'),
                "street1": address_obj.get('street1', None),
                "street2": address_obj.get('street2', None),
                "city": address_obj.get('city', None),
                "state": address_obj.get('state', None),
                "country": address_obj.get('country', None),
                "postalcode": address_obj.get('postalcode', None),
                "address_string": address_obj.get('address_string', None),
                "latitude": data.get('latitude'),
                "longitude": data.get('longitude'),
                "ranking_string": data.get('ranking_data', None),
                "rating": data.get('rating',None),
            }
        return None

    def get_place_images(self, place_id):
        trip_adv_image_url = f"https://api.content.tripadvisor.com/api/v1/location/{place_id}/photos"
        params = {"key": self.api_key}
        image_response = requests.get(trip_adv_image_url, params=params)

        if image_response.status_code == 200:
            data = image_response.json().get('data', [])
            image_list = []
            for image in data:
                image_list.append({
                    'thumbnail': image['images'].get('thumbnail', None),
                    'small': image['images'].get('small', None),
                    'medium': image['images'].get('medium', None),
                    'large': image['images'].get('large', None),
                    'original': image['images'].get('original', None)
                })
            return image_list
        return None


class EmailService:
    @staticmethod
    def send_verification_email(email_to, token):
        smtp_server = settings.EMAIL_HOST
        smtp_port = settings.EMAIL_PORT

        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = email_to
        msg['Subject'] = "Email Verification for PlanMyItinerary"

        # Update the body to include a clickable link
        verification_link = f"{settings.BACKEND_URL}/api/user/verify-email/{token}"
        body = f'Click the link below to verify your email:\n\n{verification_link}'
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)

            print("Verification email sent successfully!")
            return True

        except smtplib.SMTPException as e:
            print(f"Failed to send verification email: {e}")
            return False
        
        
gemini_client = GeminiAPIClient(settings.GEMINI_API_KEY)
trip_advisor_client = TripAdvisorAPIClient(settings.TRIPADVISOR_API_KEY)