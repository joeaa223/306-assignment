from django.urls import path
from . import views

urlpatterns = [
    path('register/<int:activity_id>/', views.register_activity_view, name='register_activity'),
    path('withdraw/<int:activity_id>/', views.withdraw_activity_view, name='withdraw_activity'),
    path('my-schedule/', views.my_registrations_view, name='my_schedule'),
]
