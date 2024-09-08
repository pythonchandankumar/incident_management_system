from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime
import requests
import random
import json


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12)
    address = models.CharField(max_length=200)
    pincode = models.CharField(max_length=6)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

   
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.pincode and (not self.city or not self.state or not self.country):
            self.city, self.state, self.country = self.get_location_from_pincode(self.pincode)
        super().save(*args, **kwargs)

    def get_location_from_pincode(self, pincode):
        try:
            response = requests.get(f'https://api.postalpincode.in/pincode/{pincode}')
            data= json.loads(response.text)
            city = data[0].get('PostOffice', [])[0].get('District', '')
            state = data[0].get('PostOffice', [])[0].get('State', '')
            country = data[0].get('PostOffice', [])[0].get('Country', '')
            return city, state, country
        except Exception as e:
            print(f"Error fetching location: {e}")
            return "", "", ""


class IncidentModel(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Closed', 'Closed'),
    ]

    INCIDENT_TYPE = [
        ('enterprise','Enterprise'),
        ('individual','Individual'),
        ('government','Government'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPE, default='individual')
    reporter_name = models.CharField(max_length=255)
    incident_details = models.TextField()
    reported_date = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES,default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    incident_id = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.incident_id:
            self.incident_id = self.generate_incident_id()
        # uniqueness of incident_id
        if IncidentModel.objects.exclude(id=self.id).filter(incident_id=self.incident_id).exists():
            raise ValidationError('Incident ID must be unique.')
        if self.incident_id:
            self.incident_id = self.generate_incident_id()
        super().save(*args, **kwargs)

    def generate_incident_id(self):
        random_number = random.randint(10000, 99999)
        current_year = datetime.now().year
        return f'RMG{random_number}{current_year}'

    def __str__(self):
        return self.incident_id 