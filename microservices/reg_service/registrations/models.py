from django.db import models

class Registration(models.Model):
    user_id = models.IntegerField()
    activity_id = models.IntegerField()
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='REGISTERED') # e.g., REGISTERED, WITHDRAWN

    class Meta:
        unique_together = ('user_id', 'activity_id')
        verbose_name = 'Activity Registration'

    def __str__(self):
        return f"User {self.user_id} - Activity {self.activity_id}"
