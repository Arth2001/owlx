from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Agent, AgentMetric
from .serializers import AgentSerializer, AgentMetricSerializer
from rest_framework.permissions import AllowAny

# Create your views here.

class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        agent = self.get_object()
        agent.update_heartbeat()
        return Response({'status': 'heartbeat updated'})

    @action(detail=True, methods=['post'])
    def report_metrics(self, request, pk=None):
        agent = self.get_object()
        metrics_data = request.data.get('metrics', [])
        
        created_metrics = []
        for metric in metrics_data:
            metric_obj = AgentMetric.objects.create(
                agent=agent,
                metric_name=metric['name'],
                metric_value=metric['value']
            )
            created_metrics.append(metric_obj)

        serializer = AgentMetricSerializer(created_metrics, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AgentMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentMetric.objects.all()
    serializer_class = AgentMetricSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        agent_id = self.request.query_params.get('agent_id', None)
        metric_name = self.request.query_params.get('metric_name', None)
        
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        if metric_name:
            queryset = queryset.filter(metric_name=metric_name)
            
        return queryset.order_by('-timestamp')

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def agent_status_check(request):
    """
    Simple endpoint to test agent connectivity
    """
    if request.method == 'POST':
        # If it's a POST request with agent data, log but don't save
        agent_data = request.data
        print(f"Received agent check-in: {agent_data}")
        
    return Response({
        'status': 'ok',
        'message': 'Agent connectivity check successful',
        'server_time': timezone.now().isoformat(),
        'request_method': request.method,
        'received_headers': dict(request.headers),
    })
