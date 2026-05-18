from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class DocumentType(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='documents', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_types')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

class DocumentApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    document = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='document_applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    letter = models.FileField(upload_to='documents/', null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    has_seen = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.document.title} ({self.status})"

class SaveDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_saves')
    document = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'document'),)

    def __str__(self):
        return f"{self.user.username} saved {self.document.title}"

class Profile(models.Model):
    ROLE_CHOICES = (
        ("Student", "Student"),
        ("Staff", "Staff"),
        ("Admin", "Admin"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    prof_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True
    )
    address = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Review(models.Model):
    document = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='review_documents')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='replied_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        unique_together = (('document', 'user'),)

    def __str__(self):
        return f"{self.user.username} {self.document.title} {self.rating}"

