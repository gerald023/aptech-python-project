from django.db import models
from django.conf import settings

# Create your models here.
class Contact(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="contact"
    )
    restaurant()