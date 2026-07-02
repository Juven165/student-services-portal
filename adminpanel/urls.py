from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('application-overtime/', views.application_overtime, name='application_overtime'),
    path('user-list/', views.user_list, name='user_list'),
    path('activate/<int:user_id>/', views.activate_user, name='activate'),
    path('deactivate/<int:user_id>/', views.deactivate_user, name='deactivate'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('staff-overview/', views.staff_overview, name='staff_overview'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('staff-detail/<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('application-overview/', views.application_overview, name='application_overview'),
    path(
        'application-detail/<int:application_id>/',
        views.application_detail,
        name='application_detail'
    ),
    path('delete-application/<int:application_id>/', views.delete_application, name='delete_application'),
    path('notification/', views.notification, name='notification'),
    path('mark-as-read/<int:notif_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
]