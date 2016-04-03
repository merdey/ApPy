import datetime
import pytz

from django.core.management.base import BaseCommand

from appy.models import Application
from appy.models import Reminder


class Command(BaseCommand):
    def handle(self, *args, **options):
        utc=pytz.UTC
        reminders = Reminder.objects.all()
        for rem in reminders:
            td = Reminder.duration_to_timedelta(rem.duration)
            date_to_check = datetime.datetime.now() - td
            date_to_check = utc.localize(date_to_check)

            applications = Application.objects.filter(user=rem.user, status=rem.status)
            for app in applications:
                if app.updated_at < date_to_check:
                    send_reminder(rem)


def send_reminder(reminder):
    pass