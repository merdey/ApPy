from django.db import models

class Application(models.Model):
    company = models.TextField()
    position = models.TextField()

    status = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)