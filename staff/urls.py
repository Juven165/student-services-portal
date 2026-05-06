from django import urls
from django.urls import path
from . import views

urlpatterns = [
    path('staff/staff-dashboard/', views.StaffDashboard.as_view(), name='staff_dashboard'),
    path('staff/add-document/', views.add_document, name='add_document'),
    path('staff/manage-application/', views.ManageApplication.as_view(), name='manage_application'),
    path('staff/view-application/<int:document_id>/', views.ViewDocumentApplication.as_view(), name='view_application'),
    path(
        "update-status/<int:pk>/",
        views.UpdateApplicationStatus.as_view(),
        name="update_application_status"
    ),
]