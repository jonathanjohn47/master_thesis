
import json
import re
import os

def parse_citations(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    citations = []
    current_context = []
    
    # Regex to find the JSON part within the ADDIN ZOTERO_ITEM line
    # The line looks like: ADDIN ZOTERO_ITEM CSL_CITATION {"citationID":...}
    json_pattern = re.compile(r'ADDIN ZOTERO_ITEM CSL_CITATION ({.*})')

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        match = json_pattern.search(line)
        if match:
            json_str = match.group(1)
            try:
                citation_data = json.loads(json_str)
                
                # Get context: the last non-empty text block before this citation
                # We'll look backwards from i-1
                context_text = ""
                for j in range(i - 1, -1, -1):
                    prev_line = lines[j].strip()
                    if prev_line and not prev_line.startswith("ADDIN"):
                        context_text = prev_line
                        # If the previous line is part of the same paragraph, keep going
                        # For now, let's just take the immediate preceding block as the primary claim
                        break
                
                # Also check if there is text *after* the citation on the same line or next line that might be relevant? 
                # Usually citations come at the end of a sentence.
                
                # Extract relevant items
                citation_items = citation_data.get('citationItems', [])
                for item in citation_items:
                    item_data = item.get('itemData', {})
                    citations.append({
                        'context': context_text,
                        'title': item_data.get('title'),
                        'author': item_data.get('author', []),
                        'year': item_data.get('issued', {}).get('date-parts', [[None]])[0][0],
                        'id': item.get('id')
                    })
            except json.JSONDecodeError:
                print(f"Failed to decode JSON on line {i+1}")
        else:
            # Keep track of text potentially?
            pass

    return citations

input_file = r"c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\extracted_citations.txt"
output_file = r"c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\citations_to_verify.json"

parsed_data = parse_citations(input_file)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, indent=2)

print(f"Extracted {len(parsed_data)} citations to {output_file}")
