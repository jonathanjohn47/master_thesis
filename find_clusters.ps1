
$jsonPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\citations_to_verify.json"

if (-not (Test-Path $jsonPath)) {
    Write-Host "Error: File not found at $jsonPath"
    exit
}

$citations = Get-Content $jsonPath -Raw | ConvertFrom-Json

# Group by context
$clusters = $citations | Group-Object -Property context

# Filter for clusters with >= 5 citations
$stuffedClusters = $clusters | Where-Object { $_.Count -ge 5 } | Sort-Object Count -Descending

Write-Host "Found $($stuffedClusters.Count) citation blocks with >= 5 citations."

$i = 1
foreach ($cluster in $stuffedClusters) {
    Write-Host "--- Block $i (Count: $($cluster.Count)) ---"
    
    # Get the context text, handle potential nulls
    $contextText = $cluster.Name
    if ($contextText.Length -gt 200) {
        $contextText = $contextText.Substring(0, 200) + "..."
    }
    Write-Host "Paragraph Start: $contextText"
    
    # List first few citations
    $citationsInBlock = $cluster.Group | ForEach-Object {
        $auth = if ($_.author) { $_.author[0] } else { "Unknown" }
        "$auth ($($_.year))"
    }
    
    $firstFew = $citationsInBlock | Select-Object -First 5
    Write-Host "Citations: $($firstFew -join ', ')... and ($($cluster.Count - 5)) more"
    Write-Host ""
    $i++
}
