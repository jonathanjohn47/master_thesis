
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $true # Visible to fail fast if dialogs
    
    if (-not (Test-Path $docPath)) {
        Write-Host "Doc not found"
        exit
    }
    
    $doc = $word.Documents.Open($docPath)
    Write-Host "Opened."

    $word.Selection.Find.ClearFormatting()
    $word.Selection.Find.Text = "Figure 13"
    
    if ($word.Selection.Find.Execute()) {
        Write-Host "Found Figure 13. Selection: '$($word.Selection.Text)'"
        
        # Check if already field
        if ($word.Selection.Fields.Count -gt 0) {
            Write-Host "Already a field."
        }
        else {
            Write-Host "Replacing..."
            # Bookmark name
            $bm = "Ref_Figure_13"
             
            # Fields.Add(Range, Type, Text, PreserveFormatting)
            # Word.Selection.Range
             
            try {
                # wdFieldRef = 3
                $f = $word.Selection.Fields.Add($word.Selection.Range, 3, "$bm \h", $true)
                Write-Host "Field Added."
            }
            catch {
                Write-Host "Error adding field: $($_.Exception.Message)"
            }
        }
    }
    else {
        Write-Host "Figure 13 not found via Selection.Find"
    }
    
    # Save if successful
    # $doc.Save()
    $doc.Close($false)
    $word.Quit()
    
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($word) { $word.Quit() }
}
