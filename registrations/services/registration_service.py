from django.db import transaction
from django.db.models import F
from django.utils import timezone
from registrations.models import Registration
from dashboard.models import NGOActivity
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from registrations.tasks import send_registration_confirmation_email

class RegistrationService:
    @staticmethod
    def register_user(user, activity_id):
        """
        Handle user registration for an activity with concurrency safety.
        Returns (success, message)
        """
        try:
            with transaction.atomic():
                # Lock the activity row for update
                activity = NGOActivity.objects.select_for_update().get(id=activity_id)

                # 1. Check if activity is active
                if not activity.is_active:
                    return False, "This activity is no longer active."

                # 2. Check cut-off date
                if timezone.now() > activity.cut_off_date:
                    return False, "Registration deadline has passed."

                # 3. Check if user already registered
                if Registration.objects.filter(user=user, activity=activity, status='REGISTERED').exists():
                    return False, "You are already registered for this activity."

                # 4. Check slot availability
                if activity.current_slots_taken >= activity.max_employees:
                    return False, "No slots available. This activity is full."

                # 5. Create registration and update slot count
                Registration.objects.update_or_create(
                    user=user, 
                    activity=activity, 
                    defaults={'status': 'REGISTERED'}
                )
                
                # Increment slot count using F() to prevent race conditions
                activity.current_slots_taken = F('current_slots_taken') + 1
                activity.save()

                # --- Topic 11.2: Background Task (Email) ---
                send_registration_confirmation_email.delay(
                    user.email, 
                    activity.ngo_name, 
                    user.username
                )
                print(f"DEBUG: [Celery] Task queued for {user.email}")

                # --- Topic 11.3: Real-time Notification (Bonus) ---
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "notifications",
                    {
                        "type": "send_notification",
                        "message": f"New Registration: {user.username} joined {activity.ngo_name}!"
                    }
                )
                print("DEBUG: [Channels] Real-time notification broadcasted.")

            return True, "Successfully registered for the activity!"
        except NGOActivity.DoesNotExist:
            return False, "Activity not found."
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    @staticmethod
    def withdraw_user(user, activity_id):
        """
        Handle user withdrawal from an activity.
        Returns (success, message)
        """
        try:
            with transaction.atomic():
                activity = NGOActivity.objects.select_for_update().get(id=activity_id)

                # 1. Check cut-off date (cannot withdraw after deadline)
                if timezone.now() > activity.cut_off_date:
                    return False, "Deadline has passed. Withdrawal is no longer allowed."

                # 2. Check if registration exists
                reg = Registration.objects.filter(user=user, activity=activity, status='REGISTERED').first()
                if not reg:
                    return False, "You are not registered for this activity."

                # 3. Update registration status and slot count
                reg.status = 'WITHDRAWN'
                reg.save()

                # Decrement slot count
                activity.current_slots_taken = F('current_slots_taken') - 1
                activity.save()

            return True, "Successfully withdrawn from the activity."
        except NGOActivity.DoesNotExist:
            return False, "Activity not found."
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    @staticmethod
    def get_user_registrations(user):
        """Get all active registrations for a user"""
        return Registration.objects.filter(user=user, status='REGISTERED').select_related('activity')

    @staticmethod
    def is_user_registered(user, activity_id):
        """Check if user is registered for a specific activity"""
        return Registration.objects.filter(user=user, activity_id=activity_id, status='REGISTERED').exists()

    @staticmethod
    def get_activity_participants(activity_id):
        """
        Get all users currently registered for an activity.
        Used for Use Case 4: Admin Monitoring.
        """
        registrations = Registration.objects.filter(
            activity_id=activity_id, 
            status='REGISTERED'
        ).select_related('user')
        return [reg.user for reg in registrations]

        return [reg.user for reg in registrations]
    
    @staticmethod
    def get_overall_stats():
        """
        Calculate overall participation statistics.
        Uses low-level Cache API (Topic 9.2b).
        """
        from django.core.cache import cache
        from django.db.models import Sum
        
        cache_key = 'overall_participation_stats'
        stats = cache.get(cache_key)
        
        if stats is None:
            # Stats not in cache, calculate and store
            result = NGOActivity.objects.aggregate(
                total_slots=Sum('max_employees'),
                taken_slots=Sum('current_slots_taken')
            )
            
            total_slots = result['total_slots'] or 0
            taken_slots = result['taken_slots'] or 0
            remaining_slots = total_slots - taken_slots
            
            utilization_percentage = 0
            if total_slots > 0:
                utilization_percentage = round((taken_slots / total_slots) * 100, 1)

            stats = {
                'total_slots': total_slots,
                'taken_slots': taken_slots,
                'remaining_slots': remaining_slots,
                'utilization_percentage': utilization_percentage
            }
            # Cache for 5 minutes
            cache.set(cache_key, stats, 300)
            print("DEBUG: [Cache] Stats CACHE MISS. Computed from DB.")
        else:
            print("DEBUG: [Cache] Stats CACHE HIT.")

        return stats
