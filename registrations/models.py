from django.db import models
from django.contrib.auth.models import User
from dashboard.models import NGOActivity

class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    activity = models.ForeignKey(NGOActivity, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='REGISTERED') # e.g., REGISTERED, WITHDRAWN

    class Meta:
        unique_together = ('user', 'activity')
        verbose_name = 'Activity Registration'

    def __str__(self):
        return f"{self.user.username} - {self.activity.ngo_name}"
