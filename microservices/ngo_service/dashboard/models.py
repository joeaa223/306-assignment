from django.db import models
from django.core.validators import MinValueValidator

class NGOActivity(models.Model):
    # NGO name & details
    ngo_name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)

    # Service details 
    service_type = models.CharField(max_length=100)
    date_time = models.DateTimeField()

    # Slot details
    max_employees = models.IntegerField(validators=[MinValueValidator(0)])
    current_slots_taken = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    cut_off_date = models.DateTimeField()

    # Status control
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ngo_name} - {self.service_type}"

    @property
    def remaining_slots(self):
        return self.max_employees - self.current_slots_taken