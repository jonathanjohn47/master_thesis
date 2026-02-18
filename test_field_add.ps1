
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    
    if (-not (Test-Path $docPath)) {
        Write-Host "Doc not found"
        exit
    }
    
    $doc = $word.Documents.Open($docPath)
    Write-Host "Opened."

    $rng = $doc.Content
    $find = $rng.Find
    $find.MatchWildcards = $false 
    # Search specific text
    $find.Text = "Figure 13"
    
    if ($find.Execute()) {
        Write-Host "Found 'Figure 13'."
        
        # Check if already field
        if ($rng.Fields.Count -gt 0) {
            Write-Host "Already a field."
        }
        else {
            Write-Host "Not a field. Attempting replacement..."
            
            # Bookmark name
            $bm = "Ref_Figure_13"
            
            # Insert Field
            # wdFieldRef = 3
            try {
                $f = $doc.Fields.Add($rng, 3, "$bm \h", $true)
                Write-Host "Field added? $($f -ne $null)"
                if ($f) {
                    Write-Host "Field Code: $($f.Code.Text)"
                }
            }
            catch {
                Write-Host "Error adding field: $($_.Exception.Message)"
            }
        }
    }
    else {
        Write-Host "Figure 13 not found."
    }
    
    # Don't save for test, just verify logic works without hanging
    $doc.Close($false)
    $word.Quit()
    
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($word) { $word.Quit() }
}
