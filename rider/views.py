from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from functools import partial
import geopy.distance
import googlemaps

from CabBookingService.driver.models import DriverLocation
from CabBookingService.driver.serializers import DriverInfoSerializer

from .models import Rider, TravelHistory
from .serializers import RiderRegistrationSerializer
from .serializers import RiderLoginSerializer
from .serializers import GetAvailableCabSerializer, BookCabSerializer
from .serializers import RiderTravelHistorySerializer


class CustomPermissionsForRider(permissions.BasePermission):

    def __init__(self, allowed_methods):
        self.allowed_methods = allowed_methods

    def has_permission(self, request, view):
        if 'rider_id' in request.session.keys():
            return request.method in self.allowed_methods


class RiderRegistration(APIView):

    serializer_class = RiderRegistrationSerializer

    def get(self, request, format=None):
        customers = Rider.objects.all()
        serializer = RiderRegistrationSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RiderRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RiderLogin(APIView):

    serializer_class = RiderLoginSerializer

    def post(self, request, format=None):
        serializer = RiderLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.data
            request.session['rider_id'] = serializer.validated_data["rider_id"]
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetListOfAvailableCab(APIView):

    serializer_class = GetAvailableCabSerializer
    permission_classes = (
        partial(CustomPermissionsForRider, ['GET', 'HEAD', 'POST']),)

    def post(self, request, format=None):
        serializer = GetAvailableCabSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            gmaps = googlemaps.Client(
                key='AIzaSyCDVjQAnnX2Y4hAmU_OiFfkiw0AR1lpZGo')
            request.session['source_address'] = request.data['Source_address']
            request.session['destination_address'] = request.data['Destination_address']
            geocode_result = gmaps.geocode(request.data['Source_address'])
            lat = geocode_result[0]["geometry"]["location"]["lat"]
            lon = geocode_result[0]["geometry"]["location"]["lng"]

            driver_locations = DriverLocation.objects.all()
            available_drivers_list = []
            for location in driver_locations:
                coords_1 = (lat, lon)
                coords_2 = (location.latitude, location.longitude)
                distance = geopy.distance.vincenty(coords_1, coords_2).km
                if distance < 4:
                    driver = location.driver_id
                    available_drivers_list.append(driver)
            if available_drivers_list:
                serializer = DriverInfoSerializer(
                    available_drivers_list, many=True)
                return Response(serializer.data)
            else:
                data = {"Unavailable": "Sorry, no cabs are available at this time"}
                return Response(data)
            # return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookCab(APIView):

    serializer_class = BookCabSerializer
    permission_classes = (
        partial(CustomPermissionsForRider, ['GET', 'HEAD', 'POST']),)

    def post(self, request, format=None):
        context = {
            'rider_id': request.session['rider_id'],
            'source_address': request.session['source_address'],
            'destination_address': request.session['destination_address']
        }
        serializer = BookCabSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            data = {
                "Success": "Cab booked successfully"
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TravelHistoryList(APIView):

    serializer_class = RiderTravelHistorySerializer
    permission_classes = (
        partial(CustomPermissionsForRider, ['GET', 'HEAD', 'POST']),)

    def get(self, request, format=None):
        rider_id = request.session['rider_id']
        Rider = Rider.objects.get(pk=rider_id)
        travel_history = TravelHistory.objects.filter(rider_id=Rider)
        if len(travel_history) > 0:
            serializer = RiderTravelHistorySerializer(
                travel_history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            data = {"No history": "You do not have any history of travelling"}
            return Response(data)


class Logout(APIView):

    def get(self, request, format=None):
        del request.session['rider_id']
        data = {'Logout': 'logged out successfully'}
        return Response(data, status=status.HTTP_200_OK)
