import json
import os
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework import exceptions

class APITokenAuthentication(authentication.BaseAuthentication):
    """
    Simple token based authentication.
    
    Clients should authenticate by passing the token in the "Authorization"
    HTTP header, prefixed with the string "Token ".  For example:
    
        Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    """
    
    keyword = 'Token'
    
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth or not auth.startswith(self.keyword):
            return None
            
        token = auth.split(' ', 1)[1].strip() if len(auth.split(' ', 1)) > 1 else ''
        
        return self.authenticate_credentials(token, request)
        
    def authenticate_credentials(self, key, request):
        """
        Validate the token against the stored one.
        """
        token_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api_token.json')
        
        try:
            if not os.path.exists(token_file):
                raise exceptions.AuthenticationFailed(_('Invalid token. Token file not found.'))
                
            with open(token_file, 'r') as f:
                token_data = json.load(f)
                
            if key != token_data.get('token'):
                raise exceptions.AuthenticationFailed(_('Invalid token.'))
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
            
        # For simplicity, use a default user. In production, you'd 
        # associate tokens with specific users
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            # Create default superuser if none exists
            user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            
        return (user, key)
        
    def authenticate_header(self, request):
        return self.keyword 