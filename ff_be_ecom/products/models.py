from django.db import models
from uuid import uuid4
from categories.models import Category
class ProductStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    DRAFT = "draft", "Draft"
    ARCHIVED = "archived", "Archived"

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    images = models.JSONField(default=list, blank=True)  # list of image URLs
    attributes = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=ProductStatus.choices, default=ProductStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name