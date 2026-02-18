
try {
    $word = New-Object -ComObject Word.Application
    Write-Host "Word COM Object created successfully."
    $word.Visible = $false
    
    $docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
    
    if (-not (Test-Path $docPath)) {
        Write-Host "Document not found at $docPath"
        $word.Quit()
        exit
    }
    
    $doc = $word.Documents.Open($docPath)
    Write-Host "Document opened."
    
    $images = $doc.InlineShapes.Count
    Write-Host "Found $images InlineShapes (images)."
    
    $shapes = $doc.Shapes.Count
    Write-Host "Found $shapes Shapes (floating images/textboxes)."
    
    # Look for paragraphs that look like captions
    Write-Host "`nChecking for paragraphs starting with 'Figure'..."
    $doc.Paragraphs | ForEach-Object {
        $text = $_.Range.Text.Trim()
        if ($text -match "^Figure\s+\d+") {
            Write-Host "Potential Caption Found: $text"
        }
    }
    
    $doc.Close($false)
    $word.Quit()
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($word) { $word.Quit() }
}
