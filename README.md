# PlanMyItinerary

PlanMyItinerary is a web application that helps users generate travel itineraries based on their prefences.

## Features

- User registration and authentication
- Itinerary generation based on user preferences
- Integration with Gemini to generate itinerary and TripAdvisor API for location details and images
- Timeline view of itineraries
- Recent itineraries display

## Tech Stack

### Backend
- Django
- Django REST Framework
- PostgreSQL

### Frontend
- React
- React Router
- Tailwind CSS

### APIs
- Gemini API for itinerary generation
- TripAdvisor API for location details and images

## Setup

1. Clone the repository
2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```
3. Set up the frontend:
   ```
   cd frontend
   npm install
   npm run dev
   ```

## Environment Variables

Use `.env.template` to Create a `.env` file in the backend and frontend directory with the appropriate  values.
