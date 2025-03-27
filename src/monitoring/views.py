from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import MonitoringRule, Alert
from .serializers import MonitoringRuleSerializer, AlertSerializer
from agents.models import AgentMetric
from rest_framework.permissions import AllowAny

# Create your views here.

class MonitoringRuleViewSet(viewsets.ModelViewSet):
    queryset = MonitoringRule.objects.all()
    serializer_class = MonitoringRuleSerializer

    @action(detail=True, methods=['post'])
    def evaluate(self, request, pk=None):
        """Evaluate a specific rule against all agents' metrics"""
        rule = self.get_object()
        
        # Get the most recent metrics for the specified metric name
        metrics = AgentMetric.objects.filter(
            metric_name=rule.metric_name
        ).order_by('agent', '-timestamp').distinct('agent')
        
        alerts_created = []
        
        for metric in metrics:
            # Check if the metric value triggers an alert based on rule condition
            should_alert = False
            
            if rule.condition == 'gt' and metric.metric_value > rule.threshold:
                should_alert = True
            elif rule.condition == 'lt' and metric.metric_value < rule.threshold:
                should_alert = True
            elif rule.condition == 'eq' and metric.metric_value == rule.threshold:
                should_alert = True
            elif rule.condition == 'ne' and metric.metric_value != rule.threshold:
                should_alert = True
                
            if should_alert:
                message = f"Metric {rule.metric_name} with value {metric.metric_value} "
                message += f"triggered rule '{rule.name}' ({rule.get_condition_display()} {rule.threshold})"
                
                # Check if there's already an open alert for this agent and rule
                existing_alert = Alert.objects.filter(
                    agent=metric.agent,
                    rule=rule,
                    status__in=['new', 'acknowledged']
                ).first()
                
                if existing_alert:
                    # Update existing alert
                    existing_alert.value = metric.metric_value
                    existing_alert.message = message
                    existing_alert.updated_at = timezone.now()
                    existing_alert.save()
                    alerts_created.append(existing_alert)
                else:
                    # Create new alert
                    alert = Alert.objects.create(
                        agent=metric.agent,
                        rule=rule,
                        status='new',
                        value=metric.metric_value,
                        message=message
                    )
                    alerts_created.append(alert)
        
        serializer = AlertSerializer(alerts_created, many=True)
        return Response(serializer.data)

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer
    permission_classes = [AllowAny]  # Allow anyone to access this endpoint
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by agent_id if provided
        agent_id = self.request.query_params.get('agent_id')
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
            
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by severity if provided
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(rule__severity=severity)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new alert with optional notes"""
        # If the status is 'resolved', add resolved_at timestamp
        data = request.data.copy()
        if data.get('status') == 'resolved' and not data.get('resolved_at'):
            data['resolved_at'] = timezone.now()
            
        # Create serializer with the data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
