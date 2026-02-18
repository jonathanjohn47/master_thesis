
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$logPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\caption_log.txt"

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
    
    # ---------------------------------------------------------
    # PART 1: CONVERT MANUAL CAPTIONS
    # ---------------------------------------------------------
    Log-Msg "Scanning for manual captions..."
    
    $paragraphsToConvert = @()
    foreach ($para in $doc.Paragraphs) {
        $text = $para.Range.Text.Trim()
        # Look for "Figure X: Description" or "Figure X. Description"
        if ($text -match "^Figure (\d+)[:\.]?\s*(.*)") {
            $paragraphsToConvert += $para
        }
    }
    
    Log-Msg "Found $($paragraphsToConvert.Count) manual captions."
    
    foreach ($para in $paragraphsToConvert) {
        $text = $para.Range.Text.Trim()
        if ($text -match "^Figure (\d+)[:\.]?\s*(.*)") {
            $desc = $matches[2]
            Log-Msg "Processing: $text"
            
            # Select paragraph
            $para.Range.Select()
            
            # Clean description
            if ($desc.StartsWith(":") -or $desc.StartsWith(".")) { $desc = $desc.Substring(1) }
            $desc = $desc.Trim()
            
            # Set text to just description (removes "Figure X")
            $word.Selection.Text = " " + $desc
            
            # Collapse to start
            $word.Selection.Collapse(1) # wdCollapseStart
            
            # Insert Caption
            # Label="Figure", Title=": Description"
            # We insert caption with label "Figure".
            $word.Selection.InsertCaption("Figure", "", $null, 0)
            
            # Style should be Caption automatically, but ensure it.
            $word.Selection.ParagraphFormat.Style = "Caption"
        }
    }
    
    Log-Msg "Updating fields..."
    $doc.Fields.Update()
    
    # Save intermediate state
    $doc.Save()
    Log-Msg "Saved after caption conversion."

    # ---------------------------------------------------------
    # PART 2: LINK REFERENCES
    # ---------------------------------------------------------
    Log-Msg "Starting cross-reference linking..."
    
    # Reload cross-reference items
    # wdRefTypeFigure = 2
    $crItems = $doc.GetCrossReferenceItems(2)
    Log-Msg "Available Caption Items: $($crItems.Count)"
    if ($crItems.Count -eq 0) {
        Log-Msg "No captions found to link! Exiting Part 2."
    }
    else {
    
        # Map "Figure X" to Item Index
        # Build a map for faster lookup?
        # Actually brute force lookup is fine for small N.
        
        $rng = $doc.Content
        $find = $rng.Find
        $find.ClearFormatting()
        $find.Text = "Figure [0-9]{1,2}"
        $find.MatchWildcards = $true
        $find.Wrap = 0 # wdFindStop - Process linearly
        
        while ($find.Execute()) {
            # $rng is now the found text range
            
            # Check style (skip captions)
            # $rng.Paragraphs.Item(1).Style check. 
            # Note: Style might correspond to an object, we want NameLocal.
            $styleName = try { $rng.Paragraphs.Item(1).Style.NameLocal } catch { "Unknown" }
            
            if ($styleName -eq "Caption") {
                Log-Msg "Skipping matching inside Caption: $($rng.Text)"
                continue
            }
            
            # Check if fields exist in range (already linked)
            if ($rng.Fields.Count -gt 0) {
                # Skip
                continue
            }
            
            $matchText = $rng.Text
            if ($matchText -match "Figure (\d+)") {
                $refNum = [int]$matches[1]
                
                # Find corresponding item
                $targetIndex = -1
                for ($i = 1; $i -le $crItems.Count; $i++) {
                    # Item text like "Figure 1: Desc"
                    # We match "Figure 1 " or "Figure 1:" or "Figure 1$"
                    if ($crItems[$i] -match "^Figure $refNum\b") {
                        $targetIndex = $i
                        break
                    }
                }
                
                if ($targetIndex -gt 0) {
                    Log-Msg "Linking '$matchText' -> Index $targetIndex"
                    try {
                        # InsertCrossReference(ReferenceType, ReferenceKind, ReferenceItem, InsertAsHyperlink, IncludePosition)
                        # wdRefTypeFigure=2, wdRefKindLabelAndNumber=3
                        $rng.InsertCrossReference(2, 3, $targetIndex, $true, $false)
                    }
                    catch {
                        Log-Msg "Error linking: $($_.Exception.Message)"
                    }
                }
            }
        }
    }
    
    $doc.Save()
    Log-Msg "Final Save complete."
    $doc.Close()
    $word.Quit()
    Log-Msg "Done."
    
}
catch {
    Log-Msg "CRITICAL ERROR: $($_.Exception.Message)"
    if ($doc) { $doc.Close($false) }
    if ($word) { $word.Quit() }
}
