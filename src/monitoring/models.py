from django.db import models
from agents.models import Agent

class MonitoringRule(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    CONDITION_CHOICES = [
        ('gt', 'Greater Than'),
        ('lt', 'Less Than'),
        ('eq', 'Equals'),
        ('ne', 'Not Equals'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    metric_name = models.CharField(max_length=255)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    threshold = models.FloatField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Alert(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='alerts')
    rule = models.ForeignKey(MonitoringRule, on_delete=models.CASCADE, related_name='alerts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    value = models.FloatField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or comments about this alert")

    class Meta:
        indexes = [
            models.Index(fields=['agent', 'status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.agent.name} - {self.rule.name} - {self.status}"
