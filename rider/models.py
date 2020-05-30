from django.db import models
from django.db.models import DecimalField

# Create your models here.


class Rider(models.Model):

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    number = models.IntegerField(unique=True)


class TravelHistory(models.Model):

    rider_id = models.ForeignKey(Rider, on_delete=models.CASCADE)
    driver_id = models.ForeignKey('driver.Driver', on_delete=models.CASCADE)
    source_address = models.TextField()
    destination_address = models.TextField()
    booked_time = models.DateTimeField(auto_now_add=True)
    car_no = models.CharField(max_length=50)

