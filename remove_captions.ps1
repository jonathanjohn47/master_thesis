$sourceDoc = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\Empirical Analysis of Accuracy.docx"
$backupDoc = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\Empirical Analysis of Accuracy_PreRemoval.docx"

try {
    Write-Host "Creating Word application..."
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false # Keep invisible for speed, less interference
    
    if (-not (Test-Path $sourceDoc)) {
        Write-Host "Error: Source document not found at $sourceDoc"
        exit
    }

    # Create Backup
    Write-Host "Creating backup..."
    Copy-Item $sourceDoc -Destination $backupDoc -Force
    Write-Host "Backup created at $backupDoc"

    Write-Host "Opening document..."
    $doc = $word.Documents.Open($sourceDoc)
    Write-Host "Document opened."

    # 1. Remove Caption Paragraphs
    Write-Host "Removing Caption paragraphs..."
    $paragraphsToRemove = @()
    foreach ($para in $doc.Paragraphs) {
        if ($para.Style.NameLocal -eq "Caption") {
            $text = $para.Range.Text.Trim()
            if ($text -match "^Figure") {
                $paragraphsToRemove += $para
            }
        }
    }
    
    foreach ($para in $paragraphsToRemove) {
        # Check again in case range is invalidated? Usually fine if we collected objects.
        # But deleting modifies collection. That's why we collected first.
        # Check if it still exists?
        try {
            $para.Range.Delete()
        }
        catch {
            Write-Host "Warning: Could not delete a caption paragraph. It might have been deleted already."
        }
    }
    Write-Host "Removed $($paragraphsToRemove.Count) caption paragraphs."

    # 2. Remove Textual References
    Write-Host "Removing text references..."
    $rng = $doc.Content
    $find = $rng.Find
    $find.ClearFormatting()
    $find.Text = "Figure [0-9]{1,2}"
    $find.MatchWildcards = $true
    $find.Replacement.Text = "" 
    
    # Execute Replace All
    # Execute(FindText, MatchCase, MatchWholeWord, MatchWildcards, MatchSoundsLike, MatchAllWordForms, Forward, Wrap, Format, ReplaceWith, Replace)
    # Wrap = 1 (wdFindContinue), Replace = 2 (wdReplaceAll)
    
    $result = $find.Execute("Figure [0-9]{1,2}", $false, $false, $true, $false, $false, $true, 1, $false, "", 2)
    
    Write-Host "References removed."

    # 3. Save and Close
    $doc.Save()
    Write-Host "Document saved."
    $doc.Close()
    $word.Quit()
    
    Write-Host "Done."
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Stack Trace: $($_.Exception.StackTrace)"
    if ($word) { $word.Quit() }
}
