
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
    
    Write-Host "Bookmarks: $($doc.Bookmarks.Count)"
    if ($doc.Bookmarks.Count -gt 0) {
        Write-Host "Sample BM: $($doc.Bookmarks.Item(1).Name)"
    }
    
    # Check "Figure 13"
    $rng = $doc.Content
    $find = $rng.Find
    $find.ClearFormatting()
    
    # PowerShell sometimes struggles with setting property on Find object directly if implicit.
    # But usually $find.Text = "..." works.
    # The error "Property Text cannot be found" implies $rng.Find returned something unexpected or null?
    # No, it returns a Find object.
    
    # Let's try Execute with arguments directly to be safe.
    # Execute(FindText, MatchCase, MatchWholeWord, MatchWildcards, MatchSoundsLike, MatchAllWordForms, Forward, Wrap, Format, ReplaceWith, Replace, MatchKashida, MatchDiacritics, MatchAlefHamza, MatchControl)
    
    $success = $find.Execute("Figure 13")
    
    if ($success) {
        Write-Host "Found 'Figure 13'."
        Write-Host "Fields in range: $($rng.Fields.Count)"
        if ($rng.Fields.Count -gt 0) {
            foreach ($f in $rng.Fields) {
                Write-Host "Field Code: $($f.Code.Text)"
                Write-Host "Field Result: $($f.Result.Text)"
            }
        }
        else {
            Write-Host "TEXT IS PLAIN. NO FIELDS."
        }
    }
    else {
        Write-Host "Figure 13 NOT FOUND."
    }
    
    $doc.Close($false)
    $word.Quit()
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($word) { $word.Quit() }
}
