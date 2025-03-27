from django.contrib import admin
from .models import MonitoringRule, Alert

@admin.register(MonitoringRule)
class MonitoringRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'metric_name', 'condition', 'threshold', 'severity', 'enabled')
    list_filter = ('severity', 'enabled', 'condition')
    search_fields = ('name', 'description', 'metric_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('agent', 'rule', 'status', 'value', 'created_at')
    list_filter = ('status', 'rule__severity', 'agent')
    search_fields = ('agent__name', 'rule__name', 'message')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('agent', 'rule')
    
    actions = ['acknowledge_alerts', 'resolve_alerts']
    
    def acknowledge_alerts(self, request, queryset):
        updated = queryset.filter(status='new').update(
            status='acknowledged',
            acknowledged_by=request.user
        )
        self.message_user(request, f"{updated} alerts have been acknowledged.")
    acknowledge_alerts.short_description = "Mark selected alerts as acknowledged"
    
    def resolve_alerts(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status__in=['new', 'acknowledged']).update(
            status='resolved',
            resolved_at=timezone.now()
        )
        self.message_user(request, f"{updated} alerts have been resolved.")
    resolve_alerts.short_description = "Mark selected alerts as resolved"
