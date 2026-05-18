from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from SSP.models import DocumentType, DocumentApplication
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import DocumentForm
from django.views import View
from SSP.models import Review

class StaffDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'account/staff_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        staff_documents = DocumentType.objects.filter(created_by=self.request.user)
        document_applications = DocumentApplication.objects.filter(
            document__created_by=self.request.user
        )

        context['total_documents'] = staff_documents.count()
        context['total_applications'] = document_applications.count()

        context['pending_count'] = document_applications.filter(status='Pending').count()
        context['approved_count'] = document_applications.filter(status='Approved').count()
        context['rejected_count'] = document_applications.filter(status='Rejected').count()

        context['recent_applications'] = document_applications.order_by('-requested_at')[:10]

        # Activity Feed
        feed = []

        # Documents
        for doc in staff_documents.order_by('-created_at'):
            feed.append({
                'type': 'document',
                'title': doc.title,
                'date': doc.created_at,
            })

        # Applications
        for app in context['recent_applications']:
            feed.append({
                'type': 'application',
                'applicant': app.applicant.username,
                'title': app.document.title,
                'date': app.requested_at,
            })

        context['activity_feed'] = sorted(feed, key=lambda x: x['date'], reverse=True)

        return context

@login_required
def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.created_by = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()

    return render(request, 'staff/add_document.html', {'form': form})

class ManageApplication(LoginRequiredMixin, ListView):
    model = DocumentType
    template_name = "staff/manage_document.html"
    context_object_name = "documents"

    def get_queryset(self):
        return DocumentType.objects.filter(created_by=self.request.user)

class ViewDocumentApplication(LoginRequiredMixin, ListView):
    model = DocumentApplication
    template_name = "staff/view_document_application.html"
    context_object_name = "applications"

    def get_document(self):
        return get_object_or_404(DocumentType, id=self.kwargs['document_id'], created_by=self.request.user)

    def get_queryset(self):
        documents = self.get_document()

        queryset = DocumentApplication.objects.select_related("document", "applicant").filter(document=documents)

        queryset = self.search(queryset)
        queryset = self.filter_status(queryset)
        queryset = self.filter_date(queryset)

        return queryset.order_by("-requested_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["document"] = self.get_document()
        return context

    def search(self, queryset):
        q = self.request.GET.get('search')

        if q:
            queryset = queryset.filter(
                Q(applicant__username__icontains=q) |
                Q(full_name__icontains=q) |
                Q(email__icontains=q) |
                Q(document__title__icontains=q)
            )

        return queryset

    def filter_status(self, queryset):
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def filter_date(self, queryset):
        date = self.request.GET.get('date')
        if date:
            parsed = parse_date(date)
            queryset = queryset.filter(requested_at__date=parsed)
        return queryset

class UpdateApplicationStatus(LoginRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(DocumentApplication, id=pk)

        status = request.POST.get("status")

        if status in ["Pending", "Approved", "Rejected"]:
            application.status = status
            application.save()

        return redirect(request.META.get("HTTP_REFERER"))

@login_required
def manage_review(request):
    user = request.user

    # 1. If SUPERUSER → see all reviews
    if user.is_superuser:
        reviews = Review.objects.select_related("document", "user") \
                                .order_by("-created_at")

    # 2. If STAFF → see reviews only on documents THEY created
    elif user.is_staff_user():
        reviews = Review.objects.select_related("document", "user") \
                                .filter(document__created_by=user) \
                                .order_by("-created_at")

    # 3. Everyone else → Not authorized
    else:
        return HttpResponseForbidden("Not authorized")

    return render(request, "staff/manage_review.html", {"reviews": reviews})

@login_required
def reply_review(request, review_id):

    if request.method != "POST":
        return HttpResponseForbidden("Invalid request")

    review = get_object_or_404(Review, pk=review_id)
    user = request.user

    if not (
        user.is_superuser or
        (
            user.is_staff_user() and
            review.document.created_by == user
        )
    ):
        return HttpResponseForbidden("Not authorized")

    reply = request.POST.get("reply")

    if reply:
        review.reply = reply
        review.replied_by = user
        review.save()

        messages.success(request, "Reply sent successfully")

    return redirect("manage_review")

@login_required
def delete_review(request, review_id):
    if request.method == "POST":
        return HttpResponseForbidden()

    review = get_object_or_404(Review, id=review_id)
    user = request.user

    if not(
        user.is_superuser or
        (
            user.is_staff_user() and
            review.document.created_by == user
        )
    ):
        return HttpResponseForbidden("Not authorized")

    review.delete()
    messages.success(request, "Review deleted successfully")

    return redirect("manage_review")

@login_required
def manage_application(request):
    user = request.user

    if user.is_superuser:
        applications = (DocumentApplication.objects.select_related(
            "document", "applicant")
                    .order_by("-requested_at")
        )

    elif user.is_staff_user:
        applications = (
            DocumentApplication.objects.select_related("document", "applicant")
            .filter(document__created_by=user)
            .order_by("-requested_at")
        )
    else:
        return HttpResponseForbidden("Not authorized")

    return render(request, "staff/manage_application.html", {"applications": applications})

@login_required
def delete_application(request, application_id):
    application = get_object_or_404(
        DocumentApplication,
        id=application_id
    )

    application.delete()

    messages.success(
        request,
        'Application deleted.'
    )

    return redirect('manage_application')

