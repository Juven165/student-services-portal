from django.contrib import admin
from .models import DocumentType, DocumentApplication

# Register your models here.
admin.site.register(DocumentType)
admin.site.register(DocumentApplication)