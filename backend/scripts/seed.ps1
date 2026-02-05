param(
  [string]$BaseUrl = "http://localhost:8000"
)

$register = @{
  email = "demo@example.com"
  password = "ChangeMe123"
} | ConvertTo-Json -Depth 5

$tokenResponse = $null
try {
  $tokenResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/auth/register" -ContentType "application/json" -Body $register
} catch {
  $tokenResponse = $null
}

if (-not $tokenResponse) {
  $tokenResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/auth/token" -ContentType "application/x-www-form-urlencoded" -Body "username=demo@example.com&password=ChangeMe123"
}

$token = $tokenResponse.access_token
$headers = @{ Authorization = "Bearer $token" }

1..3 | ForEach-Object {
  $payload = @{
    client_id = "client-001"
    workflow_type = "invoice_processing"
    payload = @{ invoice_id = 100 + $_ }
  } | ConvertTo-Json -Depth 5
  $response = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/tasks" -ContentType "application/json" -Headers $headers -Body $payload
  Write-Host "Created task: $($response.task_id)"
}
