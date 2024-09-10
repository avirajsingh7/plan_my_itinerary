from django.db import models
from django.contrib.auth.models import User
import uuid


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification token for {self.user.email}"


class Itinerary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Itinerary {self.id} for {self.user}"

# Activity model
class Activity(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.ForeignKey('LocationDetails', on_delete=models.CASCADE,null=True)
    duration = models.CharField(max_length=50)
    day = models.CharField(max_length=50)
    time_of_day = models.CharField(max_length=50)
    createdAt = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.description

# LocationDetails model
class LocationDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    street1 = models.CharField(max_length=255, null=True)
    street2 = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255,null=True)
    state = models.CharField(max_length=255,null=True)
    country = models.CharField(max_length=255,null=True)
    postalcode = models.CharField(max_length=50,null=True)
    address_string = models.TextField(null=True)
    latitude = models.CharField(max_length=50, null=True)
    longitude = models.CharField(max_length=50,null=True)
    ranking = models.CharField(max_length=50, null=True)
    rating = models.CharField(max_length=10, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Images model
class Image(models.Model):
    location = models.ForeignKey(LocationDetails, on_delete=models.CASCADE)
    thumbnail = models.URLField(null=True)
    small = models.URLField(null=True)
    medium = models.URLField(null=True)
    large = models.URLField(null=True)
    original = models.URLField(null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original
