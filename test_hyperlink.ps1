
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
    $find.Text = "Figure 13"
    
    if ($find.Execute()) {
        Write-Host "Found Figure 13."
        
        # Check if already hyperlink
        if ($rng.Hyperlinks.Count -gt 0) {
            Write-Host "Already a hyperlink."
        }
        else {
            Write-Host "Adding Hyperlink..."
            $bm = "Ref_Figure_13"
             
            try {
                # Hyperlinks.Add(Anchor, Address, SubAddress, ScreenTip, TextToDisplay, Target)
                # Anchor = $rng
                # SubAddress = BookmarkName
                 
                $doc.Hyperlinks.Add($rng, "", $bm)
                Write-Host "Hyperlink Added."
            }
            catch {
                Write-Host "Error adding hyperlink: $($_.Exception.Message)"
            }
        }
    }
    else {
        Write-Host "Figure 13 not found."
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
