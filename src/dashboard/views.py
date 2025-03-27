from django.shortcuts import render
from django.views.generic import TemplateView
from agents.models import Agent
from monitoring.models import Alert
import json
from itertools import groupby
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from agents.serializers import AgentSerializer

# Create your views here.

class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AgentListView(TemplateView):
    """
    View for displaying all agents
    """
    template_name = 'dashboard/agent_list.html'

class AgentDetailView(TemplateView):
    template_name = 'dashboard/agent_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent_id = self.kwargs.get('agent_id')
        
        try:
            agent = Agent.objects.get(id=agent_id)
            context['agent'] = agent
            context['is_online'] = agent.is_online()
            
            # Get latest metrics for this agent
            metrics = agent.metrics.order_by('-timestamp')[:50]
            context['metrics'] = metrics
            
            # Prepare metrics data for chart
            metric_times = {}
            metric_values = {}
            
            for metric in metrics:
                time_key = metric.timestamp.strftime('%H:%M')
                metric_name = metric.metric_name
                
                if time_key not in metric_times:
                    metric_times[time_key] = True
                
                if metric_name not in metric_values:
                    metric_values[metric_name] = []
                
                metric_values[metric_name].append(metric.metric_value)
            
            # Prepare chart data
            metrics_data = {
                "labels": list(metric_times.keys()),
                "metrics": metric_values
            }
            
            context['metrics_data_json'] = mark_safe(json.dumps(metrics_data))
            
            # Get alerts for this agent
            context['alerts'] = agent.alerts.order_by('-created_at')[:20]
            
            return context
        except Agent.DoesNotExist:
            context['error'] = f"Agent with ID {agent_id} does not exist."
            return context

class DashboardAPIView(APIView):
    """
    API view that returns dashboard data in JSON format
    """
    def get(self, request):
        # Agent statistics
        agents = Agent.objects.all()
        total_agents = agents.count()
        active_agents = agents.filter(status='active').count()
        inactive_agents = agents.filter(status='inactive').count()
        error_agents = agents.filter(status='error').count()
        
        # Agent that are online based on last heartbeat
        online_agents = sum(1 for agent in agents if agent.is_online())
        
        # Alert statistics
        total_alerts = Alert.objects.all().count()
        new_alerts = Alert.objects.filter(status='new').count()
        acknowledged_alerts = Alert.objects.filter(status='acknowledged').count()
        resolved_alerts = Alert.objects.filter(status='resolved').count()
        
        # Get latest alerts
        latest_alerts = []
        for alert in Alert.objects.all().order_by('-created_at')[:10]:
            latest_alerts.append({
                'id': alert.id,  # Include ID for edit functionality
                'agent': alert.agent.name,
                'rule': alert.rule.name,
                'severity': alert.rule.severity,
                'value': alert.value,
                'status': alert.status,
                'created_at': alert.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        dashboard_data = {
            'agents': {
                'total': total_agents,
                'online': online_agents,
                'active': active_agents,
                'inactive': inactive_agents,
                'error': error_agents
            },
            'alerts': {
                'total': total_alerts,
                'new': new_alerts,
                'acknowledged': acknowledged_alerts,
                'resolved': resolved_alerts,
                'latest': latest_alerts
            }
        }
        
        return Response(dashboard_data)

class AlertsView(TemplateView):
    """
    View for displaying and managing alerts without admin panel
    """
    template_name = 'dashboard/alerts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if we should show the create form
        create_alert = self.request.GET.get('create', False)
        if create_alert:
            context['show_create_modal'] = True
        
        # Check if we should show the edit form for a specific alert
        edit_alert_id = self.request.GET.get('edit')
        if edit_alert_id:
            try:
                alert = Alert.objects.get(id=edit_alert_id)
                context['show_edit_modal'] = True
                context['edit_alert'] = alert
            except Alert.DoesNotExist:
                pass
        
        return context

class MonitoringRulesView(TemplateView):
    """
    View for displaying and managing monitoring rules
    """
    template_name = 'dashboard/rules.html'

class AgentMetricsAPIView(APIView):
    """
    API view that returns metrics data for a specific agent
    """
    def get(self, request, agent_id):
        try:
            agent = Agent.objects.get(id=agent_id)
            
            # Get metric type from query params
            metric_type = request.query_params.get('metric', None)
            # Get last N hours from query params (default to 1 hour)
            hours = int(request.query_params.get('hours', 1))
            
            # Calculate time threshold
            time_threshold = timezone.now() - timezone.timedelta(hours=hours)
            
            # Query for metrics
            metrics_query = agent.metrics.filter(timestamp__gte=time_threshold).order_by('timestamp')
            
            # Filter by metric type if specified
            if metric_type:
                metrics_query = metrics_query.filter(metric_name=metric_type)
                
            # Group by metric name
            metrics_by_name = {}
            timestamps = []
            
            # Process metrics data
            for metric in metrics_query:
                # Add timestamp to list of timestamps if not already there
                timestamp_str = metric.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                if timestamp_str not in timestamps:
                    timestamps.append(timestamp_str)
                
                # Initialize metric name entry if it doesn't exist
                if metric.metric_name not in metrics_by_name:
                    metrics_by_name[metric.metric_name] = {
                        'values': [],
                        'timestamps': []
                    }
                
                # Add metric value and timestamp
                metrics_by_name[metric.metric_name]['values'].append(metric.metric_value)
                metrics_by_name[metric.metric_name]['timestamps'].append(timestamp_str)
            
            # Prepare response data
            response_data = {
                'agent': {
                    'id': agent.id,
                    'name': agent.name,
                    'status': agent.status,
                    'is_online': agent.is_online()
                },
                'metrics': metrics_by_name,
                'timestamps': timestamps,
                'timeframe': f"{hours} hour(s)"
            }
            
            return Response(response_data)
        except Agent.DoesNotExist:
            return Response(
                {'error': f"Agent with ID {agent_id} does not exist."},
                status=404
            )

class AgentDetailAPIView(APIView):
    """
    API view to fetch detailed information about a specific agent
    """
    def get(self, request, agent_id):
        try:
            agent = Agent.objects.get(id=agent_id)
            
            # Serialize the agent data
            agent_data = AgentSerializer(agent).data
            
            # Add additional information
            agent_data['is_online'] = agent.is_online()
            
            # Get alert counts
            agent_data['alerts'] = {
                'total': agent.alerts.count(),
                'new': agent.alerts.filter(status='new').count(),
                'acknowledged': agent.alerts.filter(status='acknowledged').count(),
                'resolved': agent.alerts.filter(status='resolved').count()
            }
            
            # Get latest metrics summary
            latest_metrics = {}
            metrics = agent.metrics.order_by('metric_name', '-timestamp').distinct('metric_name')
            
            for metric in metrics:
                latest_metrics[metric.metric_name] = {
                    'value': metric.metric_value,
                    'timestamp': metric.timestamp
                }
            
            agent_data['latest_metrics'] = latest_metrics
            
            return Response(agent_data)
            
        except Agent.DoesNotExist:
            return Response(
                {'error': f'Agent with ID {agent_id} does not exist'},
                status=404
            )
