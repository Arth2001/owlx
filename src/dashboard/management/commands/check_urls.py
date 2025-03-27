from django.core.management.base import BaseCommand
from django.urls import get_resolver, get_urlconf

class Command(BaseCommand):
    help = 'Check URL patterns and routing in the project'

    def handle(self, *args, **options):
        urlconf = get_urlconf()
        self.stdout.write(f"Using URLconf: {urlconf}")
        
        resolver = get_resolver(urlconf)
        
        # Display URL patterns
        self.stdout.write("\nAll URL patterns:")
        self.stdout.write("=" * 50)
        
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'app_name') and pattern.app_name == 'dashboard':
                self.stdout.write("\nDashboard URL patterns:")
                self.stdout.write("-" * 50)
                for url_pattern in pattern.url_patterns:
                    self.stdout.write(f"{url_pattern.pattern} -> {url_pattern.callback}")
            else:
                self.stdout.write(f"{pattern.pattern} -> {getattr(pattern, 'callback', 'include')}")
        
        # Try resolving the specific URL
        self.stdout.write("\nChecking specific URL: /dashboard/agents/5/")
        try:
            match = resolver.resolve('/dashboard/agents/5/')
            self.stdout.write(f"Match found: {match.func.__name__} from {match.func.__module__}")
            self.stdout.write(f"View kwargs: {match.kwargs}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to resolve URL: {e}")) 