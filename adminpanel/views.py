from django.db.models.functions import TruncDate
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from pyexpat.errors import messages
from django.contrib import messages
from datetime import timedelta
from SSP.models import DocumentApplication, DocumentType
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from account.models import CustomUser
from SSP.models import Notification

User = get_user_model()

@staff_member_required
def admin_dashboard(request):

    if request.user.role != "admin":
        return redirect("student_dashboard")

    documents = DocumentType.objects.all()
    applications = DocumentApplication.objects.all()
    timeframe = request.GET.get('timeframe', '7')
    today = timezone.now().date()

    if timeframe == '30':
        start_date = today - timedelta(days=29)

    elif timeframe == 'all':
        start_date = None

    else:  # default 7 days
        start_date = today - timedelta(days=6)

    total_students = User.objects.filter(role='student').count()
    total_staff = User.objects.filter(role='staff').count()
    total_documents = DocumentType.objects.count()
    total_applications = DocumentApplication.objects.count()

    approved_count = DocumentApplication.objects.filter(
        status='Approved'
    ).count()

    pending_count = DocumentApplication.objects.filter(
        status='Pending'
    ).count()

    rejected_count = DocumentApplication.objects.filter(
        status='Rejected'
    ).count()

    most_requested_documents = (
        DocumentApplication.objects
        .values('document__title')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    document_titles = [
        item['document__title']
        for item in most_requested_documents
    ]

    documents_counts = [
        item['count']
        for item in most_requested_documents
    ]

    application_query = DocumentApplication.objects.all()

    if start_date:
        application_query = application_query.filter(
            requested_at__date__gte=start_date
        )

    application_per_day = (
        application_query.annotate(date=TruncDate('requested_at')).values('date').annotate(total=Count('id')).order_by('date')
    )

    dates = [item['date'].strftime('%Y-%m-%d') for item in application_per_day]
    application_count = [item['total'] for item in application_per_day]

    context = {
        "documents": documents,
        "applications": applications,
        "total_students": total_students,
        "total_staff": total_staff,
        "total_documents": total_documents,
        "total_applications": total_applications,
        "approved_count": approved_count,
        "pending_count": pending_count,
        "rejected_count": rejected_count,
        "document_titles": document_titles,
        "documents_counts": documents_counts,
        "dates": dates,
        "application_count": application_count,
    }
    return render(request, "account/admin_dashboard.html", context)

@staff_member_required
def application_overtime(request):
    timeframe = request.GET.get('timeframe', '7')
    today = timezone.now().date()

    if timeframe == '30':
        start_date = today - timedelta(days=29)

    elif timeframe == 'all':
        first = (
            DocumentApplication.objects
            .order_by('requested_at')
            .first()
        )

        if not first:
            return JsonResponse({
                "dates": [],
                "applications_count": []
            })

        start_date = first.requested_at.date()

    else:
        start_date = today - timedelta(days=6)

    applications = (
        DocumentApplication.objects.filter(requested_at__date__gte=start_date)
        .annotate(date=TruncDate('requested_at'))
        .values('date')
        .annotate(total=Count('id'))
    )

    application_dict = {
        item["date"]: item["total"]
        for item in applications
    }

    dates = []
    application_count = []

    current_date = start_date
    while current_date <= today:
        dates.append(current_date.strftime("%Y-%m-%d"))
        application_count.append(application_dict.get(current_date, 0))
        current_date += timedelta(days=1)

    return JsonResponse({
        "dates": dates,
        "application_count": application_count
    })

@staff_member_required
def user_list(request):
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')

    users = CustomUser.objects.all().select_related('profile')

    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    if role:
        users = users.filter(profile__role=role)

    return render(request, "admin/user_list.html", {"users": users})

@staff_member_required
def activate_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if user.is_superuser:
        messages.error(request, 'Admin User cannot be deactivated')
        return redirect(request.GET.get("next", "user_list"))

    user.is_active = True
    user.save()
    messages.success(request, f"{user.username} has been activated.")
    return redirect(request.GET.get("next", "user_list"))

@staff_member_required
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if user.is_superuser:
        messages.error(request, 'Admin User cannot be deactivated')
        return redirect(request.GET.get("next", "user_list"))

    user.is_active = False
    user.save()
    messages.warning(request, f"{user.username} has been deactivated.")
    return redirect(request.GET.get("next", "user_list"))

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if user.is_superuser:
        messages.error(request, 'Admin User cannot be deactivated')
        return redirect(request.GET.get("next", "user_list"))

    user.delete()
    messages.success(request, f"{user.username} has been deleted successfully.")
    return redirect(request.GET.get("next", "user_list"))

@staff_member_required
def staff_overview(request):
    staff = User.objects.filter(role='staff')

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        staff = staff.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(profile__full_name__icontains=search_query)
        )

    if status_filter == 'active':
        staff = staff.filter(is_active=True)

    elif status_filter == 'inactive':
        staff = staff.filter(is_active=False)

    staff = staff.order_by('id')

    paginator = Paginator(staff, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'staff': staff,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_obj': page_obj,
    }

    return render(request, 'admin/staff_overview.html', context)

@staff_member_required
def delete_staff(request, staff_id):
    staff = get_object_or_404(User, pk=staff_id)

    staff.delete()
    messages.success(request, f"Staff {staff.username} has been deleted.")
    return redirect(request.GET.get("next", "staff_overview"))

@staff_member_required
def staff_detail(request, staff_id):
    staff = get_object_or_404(User, pk=staff_id)

    documents = DocumentType.objects.filter(
        created_by=staff
    )

    applications = DocumentApplication.objects.filter(
        document__created_by=staff
    ).select_related(
        'applicant',
        'document'
    ).order_by('-requested_at')

    return render(
        request,
        "admin/staff_details.html",
        {
            "staff": staff,
            "documents_count": documents.count(),
            "applications_count": applications.count(),
            "documents": documents,
            "applications": applications,
        }
    )

@staff_member_required
def application_overview(request):
    applications = DocumentApplication.objects.select_related('document', 'applicant').all().order_by('requested_at')
    return render(request, "admin/application_overview.html", {
        "applications": applications
    })

@staff_member_required
def application_detail(request, application_id):
    application = get_object_or_404(
        DocumentApplication,
        pk=application_id
    )

    return render(
        request,
        'admin/application_detail.html',
        {
            'application': application
        }
    )

@staff_member_required
def delete_application(request, application_id):
    application = get_object_or_404(
        DocumentApplication,
        pk=application_id
    )

    application.delete()

    messages.success(
        request,
        "Application deleted successfully."
    )

    return redirect('adminpanel:application_overview')

@staff_member_required
def notification(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")

    unread_notif = notifications.filter(is_read=False).count()

    return render(request, "admin/notification.html", {
        "notifications": notifications,
        "unread_notif": unread_notif,
    })

@staff_member_required
def mark_as_read(request, notif_id):
    notification = get_object_or_404(
        Notification,
        id=notif_id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save()

    return redirect("adminpanel:notification")

@staff_member_required
def mark_all_as_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect("adminpanel:notification")