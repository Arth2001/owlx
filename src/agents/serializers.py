from rest_framework import serializers
from .models import Agent, AgentMetric

class AgentSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Agent
        fields = ['id', 'name', 'status', 'ip_address', 'last_heartbeat', 
                 'version', 'config', 'created_at', 'updated_at', 'is_online']
        read_only_fields = ['created_at', 'updated_at', 'last_heartbeat']

class AgentMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentMetric
        fields = ['id', 'agent', 'metric_name', 'metric_value', 'timestamp']
        read_only_fields = ['timestamp'] 