Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$deadline = (Get-Date).AddSeconds(60)

while ((Get-Date) -lt $deadline) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient("127.0.0.1", 9091)
        $client.Close()
        exit 0
    }
    catch {
        Start-Sleep -Milliseconds 300
    }
}

Write-Error "Timed out waiting for debugpy on 9091"
exit 1
