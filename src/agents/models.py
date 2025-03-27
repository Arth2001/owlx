from django.db import models
from django.utils import timezone

class Agent(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]

    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.CharField(max_length=50)
    config = models.JSONField(default=dict)

    def __str__(self):
        return self.name

    def update_heartbeat(self):
        self.last_heartbeat = timezone.now()
        self.save()

    def is_online(self):
        if not self.last_heartbeat:
            return False
        return (timezone.now() - self.last_heartbeat).total_seconds() < 300  # 5 minutes threshold

class AgentMetric(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='metrics')
    metric_name = models.CharField(max_length=255)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['agent', 'metric_name', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.agent.name} - {self.metric_name}"
