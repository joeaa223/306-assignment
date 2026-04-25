from django.db import models

class NGOActivity(models.Model):
    ngo_name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    service_type = models.CharField(max_length=100)
    max_employees = models.IntegerField()
    current_slots_taken = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.ngo_name

    @property
    def remaining_slots(self):
        return self.max_employees - self.current_slots_taken
