# PowerShell Script to update agent statuses

# Navigate to the project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Change to the project root directory
Set-Location $projectRoot

# Run the Django management command
python manage.py update_agent_status --timeout=300

Write-Output "Agent statuses updated at $(Get-Date)" 