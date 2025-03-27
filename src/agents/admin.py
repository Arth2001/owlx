from django.contrib import admin
from .models import Agent, AgentMetric

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'ip_address', 'last_heartbeat', 'version')
    list_filter = ('status',)
    search_fields = ('name', 'ip_address')
    readonly_fields = ('last_heartbeat', 'created_at', 'updated_at')
    
    def is_online(self, obj):
        return obj.is_online()
    is_online.boolean = True
    is_online.short_description = "Online"

@admin.register(AgentMetric)
class AgentMetricAdmin(admin.ModelAdmin):
    list_display = ('agent', 'metric_name', 'metric_value', 'timestamp')
    list_filter = ('agent', 'metric_name')
    date_hierarchy = 'timestamp'
    list_select_related = ('agent',)
