from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from CabBookingService.driver.models import Driver, DriverRidesHistory
from .models import Rider, TravelHistory


class RiderRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = '__all__'

class RiderLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email and password:
            raise ValidationError("Username and Password is required")
        try:
            rider = Rider.objects.get(email=email)
        except Rider.DoesNotExist:
            raise ValidationError("This email address does not exist")
        if rider.password == password:
            data["rider_id"] = rider.id
            return data
        else:
            raise ValidationError("Invalid credentials")


class GetAvailableCabSerializer(serializers.Serializer):
    Source_address = serializers.CharField()
    Destination_address = serializers.CharField()

    def validate(self, data):
        return data


class RiderTravelHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = TravelHistory
        fields = ['source_address',
                  'destination_address',
                  'booked_time',
                  'car_no']


class BookCabSerializer(serializers.Serializer):
    car_no = serializers.CharField()

    def validate(self, data):
        car_no = data.get("car_no")

        if not car_no:
            raise ValidationError("Car Number is required")
        try:
            driver = Driver.objects.get(car_no=car_no)
        except Driver.DoesNotExist:
            raise ValidationError("Car with this number does not exist")


    def create(self, validated_data):
        car_no = validated_data.pop('car_no')
        rider_id = self.context.get("rider_id")
        source = self.context.get("source_address")
        destination = self.context.get("destination_address")
        rider = Rider.objects.get(pk=rider_id)
        driver = Driver.objects.get(car_no=car_no)
        obj1 = TravelHistory()
        obj1.rider_id = rider
        obj1.driver_id = driver
        obj1.car_no = driver.car_no
        obj1.source_address = source
        obj1.destination_address = destination
        obj1.save()
        obj = DriverRidesHistory()
        obj.driver_id = driver
        obj.car_no = car_no
        obj.rider_id = rider
        obj.source_address = source
        obj.rider_name = rider.first_name + rider.last_name
        obj.destination_address = destination
        obj.save()
        return obj
