from django.urls import path
from .views import ActivityListCreateView, CheckSlotView, DecrementSlotView

urlpatterns = [
    path('', ActivityListCreateView.as_view(), name='activity_list_create'),
    path('<int:pk>/check-slots/', CheckSlotView.as_view(), name='check_slots'),
    path('<int:pk>/update-slots/', DecrementSlotView.as_view(), name='update_slots'),
]
