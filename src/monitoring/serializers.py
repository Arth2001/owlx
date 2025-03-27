from rest_framework import serializers
from .models import MonitoringRule, Alert
from agents.serializers import AgentSerializer

class MonitoringRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoringRule
        fields = ['id', 'name', 'description', 'metric_name', 'condition', 
                 'threshold', 'severity', 'enabled', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class AlertSerializer(serializers.ModelSerializer):
    agent_detail = AgentSerializer(source='agent', read_only=True)
    rule_detail = MonitoringRuleSerializer(source='rule', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'agent', 'rule', 'status', 'value', 'message', 
                 'created_at', 'updated_at', 'resolved_at', 'acknowledged_by',
                 'agent_detail', 'rule_detail', 'notes']
        read_only_fields = ['created_at', 'updated_at', 'resolved_at'] 