from urllib import request
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import DocumentApplicationForm, ProfileForm, ReviewForm
from .models import DocumentType, DocumentApplication, SaveDocument,  Profile, Review
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


def document_list(request):
    query = request.GET.get('q')

    documents = DocumentType.objects.filter(is_active=True)

    if query:
        documents = documents.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    documents = documents.order_by('-created_at')

    return render(request, 'SSP/document_list.html', {
        'documents': documents,
        'query': query
    })

@login_required
def add_document(request, document_id):
    document = get_object_or_404(DocumentType, id=document_id)

    if request.method == "POST":
        form = DocumentApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.document = document
            application.save()
            messages.success(request, 'Your requested document was submitted successfully!')
            return redirect('my_applications')
    else:
        form = DocumentApplicationForm()

    return render(request, 'SSP/add_document.html', {
        'form': form,
        'document': document
    })


def document_detail(request, document_id):
    document = get_object_or_404(DocumentType, id=document_id)

    if not document.is_active and document.created_by != request.user:
        messages.warning(request, 'You are not authorized to view this document!')
        return redirect('document_list')

    is_saved = False

    if request.user.is_authenticated:
        is_saved = SaveDocument.objects.filter(
            user=request.user,
            document=document
        ).exists()

    reviews = Review.objects.filter(document=document)
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    existing_review = None
    can_review = False
    can_reply = False

    if request.user.is_authenticated:
        existing_review = Review.objects.filter(
            document=document,
            user=request.user
        ).first()

    # IMPORTANT: define form BEFORE POST
    form = ReviewForm()

    if request.method == "POST":
        if existing_review:
            messages.warning(request, 'You already reviewed this document!')
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.document = document
                review.user = request.user
                review.save()
                messages.success(request, "Thanks for feedback. Reviews submitted successfully")
                return redirect("document_detail", document_id=document.id)

    # ALWAYS available
    context = {
        'document': document,
        'is_saved': is_saved,
        'reviews': reviews,
        'average_rating': average_rating,
        'can_review': can_review,
        'can_reply': can_reply,
        'form': form,
    }

    return render(request, 'SSP/document_detail.html', context)

@login_required
def my_applications(request):
    applications = DocumentApplication.objects.filter(applicant=request.user).order_by('-requested_at')

    applications.update(has_seen=True)
    return render(request, 'SSP/my_document.html', {'applications': applications})

@login_required
def save_document_list(request):
    documents = SaveDocument.objects.filter(user=request.user).order_by('-saved_at')
    return render(request, 'SSP/save_document_list.html', {'saved': documents})

@login_required
def save_document(request, document_id):
    document = get_object_or_404(DocumentType, id=document_id)

    saved, created = SaveDocument.objects.get_or_create(user=request.user, document=document)

    if created:
        messages.success(request, f"{document.title} was saved successfully!")
    else:
        messages.warning(request, f"You already saved this document {document.title}")
    return redirect('document_detail', document_id=document.id)

@login_required
def unsave_document(request, document_id):
    document = get_object_or_404(DocumentType, id=document_id)
    SaveDocument.objects.filter(user=request.user, document=document).delete()
    messages.info(request, f"{document.title} was unsaved successfully!")
    return redirect('save_document_list')

def document_applications_detail(request, pk):
    document = get_object_or_404(DocumentType, pk=pk)
    applications = DocumentApplication.objects.filter(document=document)

    context = {
        "document": document,
        "applications": applications,
    }
    return render(request, "SSP/document_application_detail.html", context)

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile was saved or updated successfully!')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'SSP/profile.html', {"form": form})

class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = "account/student_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        applications = DocumentApplication.objects.filter(applicant=self.request.user).order_by('-requested_at')
        saved = SaveDocument.objects.filter(user=self.request.user).order_by('-saved_at')

        feed = []

        for application in applications:
            feed.append({
                "type": "application",
                "document": application.document,
                "status": application.status,
                "date": application.requested_at,
            })

        for s in saved:
            feed.append({
                "type": "saved",
                "document": s.document,
                "date": s.saved_at,
            })

        feed = sorted(feed, key=lambda x: x["date"], reverse=True)
        context["activity_feed"] = feed[:10]

        request_ids = applications.values_list('document_id', flat=True)
        saved_ids = saved.values_list('document_id', flat=True)

        recommended = DocumentType.objects.filter(
            is_active=True
        ).exclude(
            id__in=request_ids
        ).exclude(
            id__in=saved_ids
        ).exclude(
            created_by=self.request.user
        )

        context["recommended_document"] = recommended[:6]
        context["saved_document"] = saved.count()


        return context
