from django.urls import path
from . import views
from .views import StudentDashboard

app_name = "SSP"

urlpatterns = [
    path('document-list/', views.document_list, name='document_list'),
    path('document-detail/<int:document_id>/', views.document_detail, name='document_detail'),
    path('request/<int:document_id>/', views.add_document, name='request_document'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('save-document-list/', views.save_document_list, name='save_document_list'),
    path('save-document/<int:document_id>/', views.save_document, name='save_document'),
    path('unsave-document/<int:document_id>/', views.unsave_document, name='unsave_document'),
    path('document-applications-detail/<int:pk>/', views.document_applications_detail, name='document_applications_detail'),
    path('profile/', views.profile, name='profile'),
    path('student-dashboard', StudentDashboard.as_view(), name='student_dashboard'),
    path('about/', views.about, name='about'),
    path('notification/', views.notification, name='notification'),
    path('mark-as-read/<int:notif_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
]
