from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Registration
from django.core.mail import send_mail
from datetime import timedelta

class Command(BaseCommand):
    help = 'Sends email reminders for upcoming events'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Get registrations with reminders set but not yet sent
        registrations = Registration.objects.filter(
            reminder_set=True,
            reminder_sent=False,
            event__date__gte=now
        )
        
        for reg in registrations:
            try:
                # Calculate when to send the reminder
                if reg.reminder_time.endswith('h'):
                    hours = int(reg.reminder_time[:-1])
                    reminder_time = reg.event.date - timedelta(hours=hours)
                elif reg.reminder_time.endswith('m'):
                    minutes = int(reg.reminder_time[:-1])
                    reminder_time = reg.event.date - timedelta(minutes=minutes)
                else:
                    days = int(reg.reminder_time)
                    reminder_time = reg.event.date - timedelta(days=days)
                
                # If it's time to send the reminder
                if now >= reminder_time:
                    send_mail(
                        f'Reminder: {reg.event.title} is coming up!',
                        f'This is a reminder for the event "{reg.event.title}"\n\n'
                        f'Date: {reg.event.date.strftime("%B %d, %Y at %H:%M")}\n'
                        f'Location: {reg.event.location}\n\n'
                        f'We look forward to seeing you there!',
                        'noreply@youreventplatform.com',
                        [reg.user.email],
                        fail_silently=False,
                    )
                    reg.reminder_sent = True
                    reg.save()
                    self.stdout.write(f'Sent reminder for {reg.event.title} to {reg.user.email}')
            
            except Exception as e:
                self.stdout.write(f'Error sending reminder for {reg.event.title}: {str(e)}')