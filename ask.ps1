$lines = @()
Write-Host ""
Write-Host "=== Type your question. Type --- on a new line to submit ===" -ForegroundColor Cyan
Write-Host ""
while ($true) {
    $line = Read-Host
    if ($line -eq "---") { break }
    $lines += $line
}
$input_text = $lines -join "`n"
Write-Host ""
Write-Host "=== Submitted. Wait for answer in chat... ===" -ForegroundColor Yellow
Write-Host ""
Write-Host $input_text
