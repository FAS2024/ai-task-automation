param(
  [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"

Write-Host "Smoke test against $BaseUrl"
try {
  $health = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/health" -TimeoutSec 10
  Write-Host "Health:" ($health | ConvertTo-Json -Depth 5)
} catch {
  Write-Error "API not reachable at $BaseUrl. Start Docker or run the API locally."
  Write-Error $_
  exit 1
}

$register = @{
  email = "demo@example.com"
  password = "ChangeMe123"
} | ConvertTo-Json -Depth 5

$tokenResponse = $null
try {
  $tokenResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/auth/register" -ContentType "application/json" -Body $register
  Write-Host "Registered demo user."
} catch {
  $tokenResponse = $null
}
$token = $tokenResponse.access_token
if (-not $token) {
  $tokenResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/auth/token" -ContentType "application/x-www-form-urlencoded" -Body "username=demo@example.com&password=ChangeMe123"
  $token = $tokenResponse.access_token
}

$payload = @{
  client_id = "client-001"
  workflow_type = "invoice_processing"
  payload = @{ invoice_id = 123 }
} | ConvertTo-Json -Depth 5

$headers = @{ Authorization = "Bearer $token" }
$response = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/tasks" -ContentType "application/json" -Headers $headers -Body $payload
$taskId = $response.task_id
Write-Host "Task created: $taskId"

for ($i = 0; $i -lt 10; $i++) {
  Start-Sleep -Seconds 1
  $status = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/tasks/$taskId" -Headers $headers
  Write-Host "Status: $($status.status)"
  if ($status.status -eq "success") {
    Write-Host "Result:" ($status.result | ConvertTo-Json -Depth 5)
    exit 0
  }
}

Write-Error "Task did not complete in time."
exit 1
