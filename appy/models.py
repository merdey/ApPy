from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    description = models.TextField()


class Position(models.Model):
    company = models.TextField()
    job_title = models.TextField()
    description = models.TextField()
    tags = models.ManyToManyField(Tag)


class Application(models.Model):
    user = models.ForeignKey(User)
    position = models.ForeignKey(Position)

    APPLIED = 'APP'
    REJECTED = 'REJ'
    INTERVIEWING = 'INT'
    NEGOTIATING = 'NEG'
    STATUS_CHOICES = (
        (APPLIED, 'Applied'),
        (REJECTED, 'Rejected'),
        (INTERVIEWING, 'Interviewing'),
        (NEGOTIATING, 'Negotiating'),
    )
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=APPLIED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
