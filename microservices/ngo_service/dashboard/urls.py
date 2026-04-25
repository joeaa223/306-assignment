from django.urls import path
from . import views

urlpatterns = [
    path('accounts-info/', views.accounts_info_view, name='accounts_info'),
    path('notifications/', views.notifications_view, name='admin_notifications'),
    path('notification-history/', views.notification_history_view, name='notification_history'),
    path('', views.ngo_list_view, name='ngo_list'),
    path('create/', views.create_activity_view, name='create_activity'),
    path('update/<int:pk>/', views.update_activity_view, name='update_activity'),
    path('toggle/<int:pk>/', views.toggle_activity_status_view, name='toggle_activity'),
    path('delete/<int:pk>/', views.delete_activity_view, name='delete_activity'),
    path('dashboard/', views.ngo_list_view, name='dashboard'),
    path('monitoring/', views.monitoring_view, name='monitoring'),
    path('qr-code/<int:pk>/', views.qr_generator_view, name='qr_generator'),
    path('virtual-scan/<int:pk>/', views.virtual_scanner_view, name='virtual_scan'),
    path('activity/<int:pk>/', views.activity_detail_view, name='activity_detail'),
]
