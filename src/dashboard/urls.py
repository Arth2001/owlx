from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('agents/', views.AgentListView.as_view(), name='agent_list'),
    path('agents/<int:agent_id>/', views.AgentDetailView.as_view(), name='agent_detail'),
    path('alerts/', views.AlertsView.as_view(), name='alerts'),
    path('rules/', views.MonitoringRulesView.as_view(), name='rules'),
    
    # API endpoints
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='dashboard_api'),
    path('api/agents/<int:agent_id>/metrics/', views.AgentMetricsAPIView.as_view(), name='agent_metrics_api'),
    path('api/agents/<int:agent_id>/details/', views.AgentDetailAPIView.as_view(), name='agent_detail_api'),
] 