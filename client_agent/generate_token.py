import os
import secrets
import string
import json
from datetime import datetime

def generate_token(length=32):
    """Generate a random token string"""
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token

def main():
    """Create and save an API token"""
    token = generate_token()
    
    # Create a token file
    token_data = {
        'token': token,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    # Save to file
    with open('api_token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print(f"API Token generated: {token}")
    print("Token saved to api_token.json")
    print("\nAdd this token to your agent client command:")
    print(f"python agent_client.py --name \"Test Agent\" --interval 5 --token \"{token}\"")

if __name__ == "__main__":
    main() 