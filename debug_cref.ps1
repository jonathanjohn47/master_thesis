
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open($docPath)

try {
    Write-Host "Getting items..."
    $items = $doc.GetCrossReferenceItems(2) # wdRefTypeFigure = 2
    Write-Host "Got items."
    Write-Host "Count: $($items.Count)"
    
    foreach ($item in $items) {
        Write-Host "Item: $item"
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
}

$doc.Close($false)
$word.Quit()
