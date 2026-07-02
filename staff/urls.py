from django import urls
from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [
    path('staff/staff-dashboard/', views.StaffDashboard.as_view(), name='staff_dashboard'),
    path('staff/add-document/', views.add_document, name='add_document'),
    path('staff/manage-application/', views.ManageApplication.as_view(), name='manage_document'),
    path('staff/view-application/<int:document_id>/', views.ViewDocumentApplication.as_view(), name='view_application'),
    path(
        "update-status/<int:pk>/",
        views.UpdateApplicationStatus.as_view(),
        name="update_application_status"
    ),
    path('staff/manage-review/', views.manage_review, name='manage_review'),
    path('staff/reply-review/<int:review_id>/', views.reply_review, name='reply_review'),
    path('staff/delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('staff/manage-aplication/', views.manage_application, name='manage_application'),
    path('staff/delete-application/<int:application_id>', views.delete_application, name='delete_application'),
    path('staff/notification/', views.notification, name='notification'),
    path('staff/mark-as-read/<int:notif_id>/', views.mark_as_read, name='mark_as_read'),
    path('staff/mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
]