import datetime

from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    description = models.TextField()

    def __str__(self):
        return self.description


class Position(models.Model):
    company = models.TextField()
    job_title = models.TextField()
    description = models.TextField()
    tags = models.ManyToManyField(Tag)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s at %s' % (self.job_title, self.company)


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


class Reminder(models.Model):
    user = models.ForeignKey(User)

    status = models.CharField(max_length=3, choices=Application.STATUS_CHOICES)
    duration = models.CharField(max_length=64)

    EMAIL = 'EM'
    PHONE = 'PH'
    CONTACT_METHOD_CHOICES = (
        (EMAIL, 'Email'),
        (PHONE, 'Phone'),
    )
    contact_method = models.CharField(max_length=2, choices=CONTACT_METHOD_CHOICES)
    contact_info = models.CharField(max_length=64)

    @classmethod
    def is_valid_duration(cls, duration):
        try:
            cls.duration_to_timedelta(duration)
            return True
        except Exception:
            return False

    @classmethod
    def duration_to_timedelta(cls, duration):
        from_end = None
        if 'day' in duration:
            from_end = 4
            unit = 'day'
        if 'days' in duration:
            from_end = 5
            unit = 'day'
        if 'week' in duration:
            from_end = 5
            unit = 'week'
        if 'weeks' in duration:
            from_end = 6
            unit = 'week'

        if from_end:
            num_units = int(duration[:-from_end])
        else:
            raise NotImplemented

        if unit == 'day':
            return datetime.timedelta(days=num_units)
        elif unit == 'week':
            num_units *= 7
            return datetime.timedelta(days=num_units)
