@echo off
REM Script to update agent statuses

REM Navigate to the project directory
cd /d "%~dp0\.."

REM Run the Django management command
python manage.py update_agent_status --timeout=300

echo Agent statuses updated at %date% %time% 