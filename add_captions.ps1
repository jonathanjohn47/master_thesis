
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $true # Visible to see progress/errors
    
    if (-not (Test-Path $docPath)) {
        Write-Host "Error: Document not found."
        exit
    }

    $doc = $word.Documents.Open($docPath)
    Write-Host "Document opened."

    # ---------------------------------------------------------
    # PART 1: CONVERT MANUAL CAPTIONS TO WORD CAPTIONS
    # ---------------------------------------------------------
    
    # We collect paragraphs first so we don't mess up iteration while modifying
    $paragraphsToCheck = @()
    foreach ($para in $doc.Paragraphs) {
        $text = $para.Range.Text.Trim()
        if ($text -match "^Figure (\d+)[:\.]?\s*(.*)") {
            $paragraphsToCheck += $para
        }
    }

    Write-Host "Found $($paragraphsToCheck.Count) manual captions to convert."

    # Sort checks to process? Order in document typically matters for numbering.
    # $doc.Paragraphs is already in order.

    $captionsMap = @{} # Map number to Caption Range/Object for linking later

    foreach ($para in $paragraphsToCheck) {
        $text = $para.Range.Text.Trim()
        if ($text -match "^Figure (\d+)[:\.]?\s*(.*)") {
            $figNum = $matches[1]
            $desc = $matches[2]
            
            Write-Host "Converting: $text"
            
            # Select the paragraph range
            $rng = $para.Range
            $rng.Select()
            
            # Delete the manual "Figure X..." text
            # We want to keep the description though. 
            # Strategy: Delete content, InsertCaption, Type Description.
            # But InsertCaption usually adds the label number.
            
            # Better strategy: 
            # 1. Delete "Figure X[:.]" prefix.
            # 2. Collapse to start.
            # 3. InsertCaption (Label="Figure", Title=": " + desc?)
            # Word's InsertCaption takes Title argument which is appended.
            
            # Clean description: Remove leading colon/space
            if ($desc.StartsWith(":")) { $desc = $desc.Substring(1) }
            if ($desc.StartsWith(".")) { $desc = $desc.Substring(1) }
            $desc = $desc.Trim()
            
            # Replace paragraph text with just description (temp)
            $rng.Text = " " + $desc
            
            # Collapse to start to insert caption before description
            $rng.Collapse(1) # wdCollapseStart
            $rng.Select()
            
            # Insert Caption
            # wdCaptionFigure = -1
            $word.Selection.InsertCaption(-1, "", $null, 0) 
            
            # Apply Style "Caption" to the whole paragraph
            $para.Style = "Caption"
            
            # Store this paragraph/range for referencing later?
            # Actually, for CrossReference, we need the item index in the caption list.
            # If we process in order, Figure 1 is index 1, Figure 2 is index 2.
        }
    }
    
    # Update fields to ensure numbering is correct
    $doc.Fields.Update()
    
    # ---------------------------------------------------------
    # PART 2: LINK IN-TEXT REFERENCES
    # ---------------------------------------------------------
    
    Write-Host "Linking references..."
    
    # We need to find "Figure X" in the text and replace with CrossRef.
    # Logic: Search pattern "Figure [0-9]+".
    # If found, check if it's inside a Caption style (skip).
    # If text, get number. Map number to Caption Index.
    # Insert CrossRef.
    
    $rng = $doc.Content
    $find = $rng.Find
    $find.ClearFormatting()
    
    # We need a wildcard search to catch variations? 
    # Let's stick to strict "Figure [0-9]+"
    
    $find.Text = "Figure [0-9]{1,2}"
    $find.MatchWildcards = $true
    $find.Wrap = 1 # wdFindContinue
    
    # We can't use 'Replace' because we need logic per match.
    # So we loop .Execute()
    
    # Be careful of infinite loops if we replace "Figure 1" with a field that displays "Figure 1".
    # We must skip if it's already a field or if we just processed it.
    
    # Standard approach: Iterate all occurrences. 
    # Use distinct Range object for searching to avoid Selection mess.
    
    $searchRng = $doc.Content
    
    while ($searchRng.Find.Execute("Figure [0-9]{1,2}", $true, $true, $false, $false, $false, $true, 1, $false, $null, 0)) {
        # Checking if match is within a caption style
        if ($searchRng.Paragraphs[1].Style.NameLocal -eq "Caption") {
            # Skip captions
            continue
        }
        
        # Check if it's already a field (Cross Ref)
        if ($searchRng.Fields.Count -gt 0) {
            continue
        }
        
        $matchText = $searchRng.Text
        if ($matchText -match "Figure (\d+)") {
            $refNum = [int]$matches[1]
            
            # Check if this figure number exists as a caption
            # We assume sequential 1..N mapping. 
            # Figure 1 -> Caption 1.
            # GetCrossReferenceItems(ReferenceType) returns array of strings.
            # wdRefTypeFigure = 2
            
            $captions = $doc.GetCrossReferenceItems(2) 
            # Note: $captions is 1-based array in VBA, likely 1-based or 0-based in PS?
            # It returns strings like "Figure 1: Desc".
            
            # We need to find the item that starts with "Figure $refNum"
            $targetIndex = -1
            for ($i = 1; $i -le $captions.Count; $i++) {
                if ($captions[$i] -match "^Figure $refNum\b") {
                    $targetIndex = $i
                    break
                }
            }
            
            if ($targetIndex -gt 0) {
                Write-Host "Linking '$matchText' to Caption $targetIndex"
                
                # Insert Cross Ref
                # ReferenceType=2 (Figure)
                # ReferenceKind=3 (wdRefKindLabelAndNumber - "Figure 1")
                # ReferenceItem=Index
                # InsertAsHyperlink=True
                # IncludePosition=False
                
                $searchRng.InsertCrossReference(2, 3, $targetIndex, $true, $false)
            }
            else {
                Write-Host "Warning: Could not find caption for $matchText"
            }
        }
        
        # Move range forward to avoid infinite loop on same text
        $searchRng.Collapse(0) # wdCollapseEnd
    }

    $doc.Save()
    Write-Host "Document saved."
    $doc.Close()
    $word.Quit()
    
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($word) { $word.Quit() }
}
