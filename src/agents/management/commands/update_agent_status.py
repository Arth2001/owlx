from django.core.management.base import BaseCommand
from django.utils import timezone
from agents.models import Agent


class Command(BaseCommand):
    help = 'Update agent statuses based on heartbeat timestamps'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Number of seconds after which an agent is considered inactive (default: 300)'
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        threshold = timezone.now() - timezone.timedelta(seconds=timeout)
        
        # Update agents with outdated heartbeats to inactive
        updated_count = Agent.objects.filter(
            last_heartbeat__lt=threshold,
            status='active'
        ).update(status='inactive')
        
        # Log results
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} agents to inactive status')
        ) 