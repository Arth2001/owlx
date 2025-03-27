#!/usr/bin/env python
"""
Sample Agent Client for OwlX Monitoring Platform

This script simulates an agent that collects system metrics and sends them to the
OwlX monitoring platform API.
"""

import os
import sys
import time
import json
import random
import socket
import argparse
import platform
import requests
from datetime import datetime
from urllib.parse import urljoin

class OwlXAgent:
    def __init__(self, api_url, agent_id=None, agent_name=None, api_token=None, interval=60):
        self.api_url = api_url
        self.agent_id = agent_id
        self.agent_name = agent_name or socket.gethostname()
        self.api_token = api_token
        self.interval = interval
        self.version = "1.0.0"
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        # Add API token to headers if provided
        if self.api_token:
            self.headers['Authorization'] = f'Token {self.api_token}'
        
        # Number of times to retry failed API calls
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    def _make_api_request(self, method, endpoint, data=None, timeout=10):
        """Make API request with retries"""
        url = urljoin(self.api_url, endpoint)
        retries = 0
        
        while retries < self.max_retries:
            try:
                if method.lower() == 'get':
                    response = requests.get(url, headers=self.headers, timeout=timeout)
                elif method.lower() == 'post':
                    response = requests.post(url, headers=self.headers, json=data, timeout=timeout)
                elif method.lower() == 'put':
                    response = requests.put(url, headers=self.headers, json=data, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # If successful, return response
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"API request failed: {e}")
                retries += 1
                if retries < self.max_retries:
                    print(f"Retrying in {self.retry_delay} seconds... (Attempt {retries + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                else:
                    print(f"Max retries reached. Giving up.")
                    return None
    
    def test_connection(self):
        """Test connection to the server"""
        try:
            response = self._make_api_request('get', 'api/agent-check/')
            if response and response.status_code == 200:
                print(f"Connection successful: {response.json()}")
                return True
            return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def register(self):
        """Register this agent with the monitoring platform if not already registered"""
        if self.agent_id:
            print(f"Agent already has ID: {self.agent_id}")
            return self.agent_id
            
        data = {
            'name': self.agent_name,
            'status': 'active',
            'ip_address': self._get_ip_address(),
            'version': self.version,
            'config': {
                'os': platform.platform(),
                'python_version': platform.python_version(),
                'interval': self.interval
            }
        }
        
        response = self._make_api_request('post', 'api/agents/', data)
        
        if response and response.status_code == 201:
            self.agent_id = response.json()['id']
            print(f"Agent registered with ID: {self.agent_id}")
            return self.agent_id
        else:
            print(f"Failed to register agent: {getattr(response, 'status_code', 'N/A')} - {getattr(response, 'text', 'No response')}")
            return None
    
    def send_heartbeat(self):
        """Send a heartbeat to the monitoring platform"""
        if not self.agent_id:
            print("Agent is not registered. Cannot send heartbeat.")
            return False
            
        response = self._make_api_request('post', f'api/agents/{self.agent_id}/heartbeat/')
        
        if response and response.status_code == 200:
            print(f"Heartbeat sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"Failed to send heartbeat: {getattr(response, 'status_code', 'N/A')} - {getattr(response, 'text', 'No response')}")
            return False
            
    def collect_metrics(self):
        """Collect system metrics. In a real agent, this would use psutil or similar."""
        metrics = [
            {
                'name': 'cpu_usage',
                'value': random.uniform(0.0, 100.0)
            },
            {
                'name': 'memory_usage',
                'value': random.uniform(20.0, 80.0)
            },
            {
                'name': 'disk_usage',
                'value': random.uniform(10.0, 90.0)
            },
            {
                'name': 'network_in',
                'value': random.uniform(0.0, 10000.0)
            },
            {
                'name': 'network_out',
                'value': random.uniform(0.0, 5000.0)
            }
        ]
        return metrics
    
    def send_metrics(self, metrics=None):
        """Send collected metrics to the monitoring platform"""
        if not self.agent_id:
            print("Agent is not registered. Cannot send metrics.")
            return False
            
        if metrics is None:
            metrics = self.collect_metrics()
            
        data = {
            'metrics': metrics
        }
        
        response = self._make_api_request('post', f'api/agents/{self.agent_id}/report_metrics/', data)
        
        if response and response.status_code == 201:
            print(f"Metrics sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"Failed to send metrics: {getattr(response, 'status_code', 'N/A')} - {getattr(response, 'text', 'No response')}")
            return False
    
    def run(self):
        """Run the agent in a loop, collecting and sending metrics at regular intervals"""
        print(f"Attempting to connect to server at {self.api_url}...")
        
        # Test connection first
        if not self.test_connection():
            print("Failed to connect to the server. Please check the URL and network connection.")
            return
        
        # Register if not already registered
        if not self.agent_id and not self.register():
            print("Failed to register agent. Please check the API token and server configuration.")
            return
        
        print(f"Agent {self.agent_name} (ID: {self.agent_id}) starting with {self.interval}s interval")
        
        try:
            # Calculate heartbeat interval - send heartbeats 4x more frequently than metrics
            heartbeat_interval = max(5, self.interval // 4)
            metrics_counter = 0
            
            print(f"Sending heartbeats every {heartbeat_interval}s and metrics every {self.interval}s")
            
            consecutive_failures = 0
            max_consecutive_failures = 5
            
            while True:
                success = False
                
                # Always send a heartbeat
                heartbeat_success = self.send_heartbeat()
                
                # Send metrics only on the main interval
                if metrics_counter == 0:
                    metrics_success = self.send_metrics()
                    success = heartbeat_success or metrics_success
                else:
                    success = heartbeat_success
                
                # Check for consecutive failures
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    print(f"Warning: {consecutive_failures} consecutive communication failures")
                    
                    if consecutive_failures >= max_consecutive_failures:
                        print(f"Error: Reached {max_consecutive_failures} consecutive failures. Attempting to reconnect...")
                        if self.test_connection():
                            consecutive_failures = 0
                            print("Successfully reconnected to server.")
                        else:
                            print("Failed to reconnect. Continuing to retry...")
                
                # Increment counter and reset when it reaches the ratio
                metrics_counter = (metrics_counter + 1) % 4
                
                # Sleep for the shorter heartbeat interval
                time.sleep(heartbeat_interval)
        except KeyboardInterrupt:
            print("Agent stopped by user")
        except Exception as e:
            print(f"Agent encountered an error: {e}")
            # Log the full traceback for debugging
            import traceback
            traceback.print_exc()
    
    def _get_ip_address(self):
        """Get the local IP address of this machine"""
        try:
            # Create a socket connection to get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

def main():
    parser = argparse.ArgumentParser(description='OwlX Monitoring Agent')
    parser.add_argument('--url', default='http://localhost:8000/', help='API URL of the monitoring platform')
    parser.add_argument('--agent-id', help='Agent ID if already registered')
    parser.add_argument('--name', help='Agent name (defaults to hostname)')
    parser.add_argument('--token', help='API token for authentication')
    parser.add_argument('--interval', type=int, default=60, help='Reporting interval in seconds')
    parser.add_argument('--test-only', action='store_true', help='Only test the connection and exit')
    
    args = parser.parse_args()
    
    # Ensure the URL has a trailing slash
    if not args.url.endswith('/'):
        args.url = args.url + '/'
    
    print(f"OwlX Monitoring Agent v1.0.0")
    print(f"Connecting to: {args.url}")
    print(f"Agent name: {args.name or socket.gethostname()}")
    print(f"Using authentication token: {'Yes' if args.token else 'No'}")
    
    agent = OwlXAgent(
        api_url=args.url,
        agent_id=args.agent_id,
        agent_name=args.name,
        api_token=args.token,
        interval=args.interval
    )
    
    if args.test_only:
        # Just test the connection and exit
        success = agent.test_connection()
        if success:
            print("Connection test successful!")
            return 0
        else:
            print("Connection test failed!")
            return 1
    
    # Run the agent
    agent.run()
    return 0

if __name__ == "__main__":
    sys.exit(main()) 