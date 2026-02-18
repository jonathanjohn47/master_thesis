
$jsonPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\citations_to_verify.json"
$outputPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\citation_clusters_full.txt"

if (-not (Test-Path $jsonPath)) {
    Write-Host "Error: File not found at $jsonPath"
    exit
}

$citations = Get-Content $jsonPath -Raw | ConvertFrom-Json
$clusters = $citations | Group-Object -Property context
$stuffedClusters = $clusters | Where-Object { $_.Count -ge 5 } | Sort-Object Count -Descending

$output = @()
$i = 1
foreach ($cluster in $stuffedClusters) {
    $output += "--- Block $i (Count: $($cluster.Count)) ---"
    
    # Clean context text
    $contextText = $cluster.Name -replace '[\r\n]+', ' ' -replace '\s+', ' '
    if ($contextText.Length -gt 500) {
        $contextText = $contextText.Substring(0, 500) + "..."
    }
    $output += "Paragraph Start: $contextText"
    
    $citationsInBlock = $cluster.Group | ForEach-Object {
        $auth = if ($_.author) { $_.author[0] } else { "Unknown" }
        "$auth ($($_.year)) - $($_.title)"
    }
    
    $output += "Citations:"
    $output += $citationsInBlock
    $output += ""
    $i++
}

$output | Out-File $outputPath -Encoding utf8
Write-Host "Exported clusters to $outputPath"
