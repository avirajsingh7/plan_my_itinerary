import requests
import json
from django.conf import settings
from fuzzywuzzy import fuzz
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


GEMINI_API_KEY = settings.GEMINI_API_KEY
TRIPADVISOR_API_KEY = settings.TRIPADVISOR_API_KEY


class ItineraryBuilder:
    def __init__(self, destination, num_of_days, must_includes):
        self.destination = destination
        self.num_of_days = num_of_days
        self.must_includes = must_includes

    def generate_itinerary(self):
        places_to_visit = self.get_places_to_visit()
        itinerary = {'trip': {}}
        
        for day, day_data in places_to_visit['trip'].items():
            itinerary['trip'][day] = {}
            for time_of_day, place_data in day_data.items():
                place_name = place_data['place_name']
                place_id = self.get_tourist_place_id(place_name)
                
                if place_id:
                    place_details = self.get_tourist_place_details(place_id)
                    place_images = self.get_tourist_place_images(place_id)
                else:
                    place_details = None
                    place_images = None
                
                enriched_place_data = {
                    **place_data,
                    'details': place_details,
                    'images': place_images
                }
                
                itinerary['trip'][day][time_of_day] = enriched_place_data

        return itinerary

    def get_places_to_visit(self):
        must_includes = " ".join(self.must_includes)
        
        prompt = f"""Provide a JSON response listing top tourist places around {self.destination} for a {self.num_of_days}-day trip. 
        For each place, include the recommended duration to spend there and a 60-word description about the place. 
        Create an itinerary based on this, which may include {must_includes}. 
        Ensure no extra text outside of the JSON format. 
        The JSON format should be structured as follows:

        {{
        "trip": {{
            "day_n": {{
            "morning/afternoon/evening": {{
                "place_name": "name of the place",
                "duration": "time to spend at the place",
                "description": "60-word description of the place"
                "tourist_place": "If it is a tourist place, then true else false"
            }}
            }}
        }}
        }}
        """

        base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        request_body = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        params = {
            "key": GEMINI_API_KEY
        }

        response = requests.post(base_url, params=params, json=request_body)

        text_with_json = response.json()['candidates'][0]['content']['parts'][0]['text']

        json_string = text_with_json.replace('```json\n', '').replace('\n```', '')

        extracted_json = json.loads(json_string)

        return extracted_json

    @staticmethod
    def is_match_place_name(query, result, threshold=50):
        similarity = fuzz.ratio(query.lower(), result.lower())
        return similarity >= threshold

    def get_tourist_place_id(self, place_name):
        trip_adv_search_url = "https://api.content.tripadvisor.com/api/v1/location/search"
        params = {
            "key": TRIPADVISOR_API_KEY,
            "searchQuery": f"{place_name},{self.destination}",
        }

        search_response = requests.get(trip_adv_search_url, params=params)
        if search_response.status_code == 200:
            search_results = search_response.json()['data']

            for result in search_results:
                if self.is_match_place_name(place_name, result['name']):
                    return result['location_id']
        return None

    @staticmethod
    def get_tourist_place_details(place_trip_adv_id):
        
        trip_adv_details_url = f"https://api.content.tripadvisor.com/api/v1/location/{place_trip_adv_id}/details"

        params = {
            "key": TRIPADVISOR_API_KEY,
        }

        details_response = requests.get(trip_adv_details_url, params=params)
        
        if details_response.status_code == 200:
            data = details_response.json()
            
            location_id = data.get('location_id', None)
            address_obj = data.get('address_obj', None)
            latitude = data.get('latitude', None)
            longitude = data.get('longitude', None)
            ranking_string = data.get('ranking_data', {}).get('ranking_string', None)
            rating = data.get('rating', None)

            return {
                "location_id": location_id,
                "address_obj": address_obj,
                "latitude": latitude,
                "longitude": longitude,
                "ranking_string": ranking_string,
                "rating": rating
            }
        else:
            return None

    @staticmethod
    def get_tourist_place_images(place_trip_adv_id):
        
        trip_adv_image_url = f"https://api.content.tripadvisor.com/api/v1/location/{place_trip_adv_id}/photos"
        
        params = {
            "key": TRIPADVISOR_API_KEY,
        }

        image_response = requests.get(trip_adv_image_url, params=params)

        if image_response.status_code == 200:
            data = image_response.json()
            images = data.get('data', [])
            image_list = []

            for image in images:
                image_obj = {
                    'thumbnail': image['images'].get('thumbnail', {}).get('url'),
                    'small': image['images'].get('small', {}).get('url'),
                    'medium': image['images'].get('medium', {}).get('url'),
                    'large': image['images'].get('large', {}).get('url'),
                    'original': image['images'].get('original', {}).get('url')
                }
                image_list.append(image_obj)

            return image_list


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