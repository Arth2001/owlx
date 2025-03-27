#!/bin/bash
# Script to update agent statuses

# Navigate to the project directory
cd "$(dirname "$0")/.."

# Run the Django management command
python manage.py update_agent_status --timeout=300

echo "Agent statuses updated at $(date)" 