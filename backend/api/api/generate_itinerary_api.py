from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services import ItineraryBuilder
from ..serializers import ItineraryRequestSerializer


@api_view(['GET'])
def generate_itinerary(request):
    
    query_params = request.query_params.copy()
    must_includes = request.query_params.get('must_includes', '').split(',')
    query_params.setlist('must_includes', must_includes)
    serializer = ItineraryRequestSerializer(data=query_params)

    if serializer.is_valid():
        num_of_days = serializer.validated_data['num_of_days']
        must_includes = serializer.validated_data['must_includes']
        destination = serializer.validated_data['destination']

        itinerary_builder = ItineraryBuilder(destination, num_of_days, must_includes)
        itinerary = itinerary_builder.generate_itinerary()

        return Response({"itinerary": itinerary}, status=200)
    else:
        return Response(serializer.errors, status=400)