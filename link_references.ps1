
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$logPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\link_log.txt"

function Log-Msg($msg) {
    Write-Host $msg
    Add-Content $logPath -Value $msg
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $true
    
    if (-not (Test-Path $docPath)) {
        Log-Msg "Error: Document not found."
        exit
    }

    Log-Msg "Opening document..."
    $doc = $word.Documents.Open($docPath)
    
    # Force update fields to ensure SEQ fields are numbered 1, 2, 3...
    Log-Msg "Updating fields..."
    $doc.Fields.Update()
    
    # Get items
    $crItems = $doc.GetCrossReferenceItems(2) # wdRefTypeFigure
    Log-Msg "Caption Items Found: $($crItems.Count)"
    
    if ($crItems.Count -eq 0) {
        Log-Msg "Still 0 items. Checking if 'Figure' label exists..."
        # Maybe the label is different context? 
        # wdRefTypeFigure implies the built-in label.
        # But InsertCaption("Figure") creates a label named "Figure".
        # If it's custom, we might need a different type?
        # Actually, wdRefTypeFigure is usually just for the label "Figure".
    }
    else {
        # Valid items found, proceed to link
        $rng = $doc.Content
        $find = $rng.Find
        $find.ClearFormatting()
        $find.Text = "Figure [0-9]{1,2}"
        $find.MatchWildcards = $true
        $find.Wrap = 0 
        
        while ($find.Execute()) {
            # Skip if inside Caption style
            $styleName = try { $rng.Paragraphs.Item(1).Style.NameLocal } catch { "Unknown" }
            if ($styleName -eq "Caption") { continue }
            
            # Skip if already a field
            if ($rng.Fields.Count -gt 0) { continue }
            
            $matchText = $rng.Text
            if ($matchText -match "Figure (\d+)") {
                $refNum = [int]$matches[1]
                
                # Match to caption item "Figure N"
                $targetIndex = -1
                for ($i = 1; $i -le $crItems.Count; $i++) {
                    # Strip non-breaking spaces etc
                    $itemText = $crItems[$i] -replace '\s+', ' '
                    if ($itemText -match "^Figure $refNum\b") {
                        $targetIndex = $i
                        break
                    }
                }
                
                if ($targetIndex -gt 0) {
                    Log-Msg "Linking '$matchText' to Caption $targetIndex"
                    try {
                        # wdRefTypeFigure=2, wdRefKindLabelAndNumber=3, InsertLink=True
                        $rng.InsertCrossReference(2, 3, $targetIndex, $true, $false)
                    }
                    catch {
                        Log-Msg "Error inserting ref: $($_.Exception.Message)"
                    }
                }
                else {
                    Log-Msg "No caption found for number $refNum"
                }
            }
        }
        $doc.Save()
        Log-Msg "Saved."
    }
    
    $doc.Close()
    $word.Quit()
    
}
catch {
    Log-Msg "Error: $($_.Exception.Message)"
    if ($word) { $word.Quit() }
}
