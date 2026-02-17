
import re

def extract_citations_with_context(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Regex for citations like (Author, Year) or (Author et al., Year)
    # Handling multiple citations in one block: (Author, Year; Author2, Year)
    citation_pattern = r'\((?:[A-Za-z\s\&\.\-]+,\s\d{4}[a-z]?(?:;\s)?)+\)'
    
    # Split by paragraphs
    paragraphs = text.split('\n')
    
    citations_found = []
    
    for i, para in enumerate(paragraphs):
        if not para.strip():
            continue
            
        matches = re.findall(citation_pattern, para)
        if matches:
            for match in matches:
                # Clean up the citation string
                clean_match = match.strip('()')
                # Split multiple citations
                individual_citations = [c.strip() for c in clean_match.split(';')]
                
                for cit in individual_citations:
                    citations_found.append({
                        "citation": cit,
                        "paragraph_sample": para[:200] + "...", # First 200 chars for context
                        "full_paragraph": para
                    })

    # Deduplicate based on citation string, but keep one context
    unique_citations = {}
    for item in citations_found:
        if item['citation'] not in unique_citations:
            unique_citations[item['citation']] = item

    return list(unique_citations.values())

if __name__ == "__main__":
    results = extract_citations_with_context("thesis_content.txt")
    print(f"Found {len(results)} unique citations.")
    
    # Print a few samples to check
    for i, res in enumerate(results[:5]):
        print(f"--- Citation {i+1} ---")
        print(f"Cit: {res['citation']}")
        print(f"Context: {res['paragraph_sample']}")
        print("-" * 20)
