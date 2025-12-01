from django.db import models
from django.conf import settings
from uuid import uuid4

# Create your models here.

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name