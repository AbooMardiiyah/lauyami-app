/**
 * Robust parser for legal analysis text
 * Handles various formats from the LLM and creates structured sections
 */

export interface ParsedSection {
  type: 'intro' | 'right' | 'warning' | 'predatory' | 'text';
  content: string;
}


export function parseAnalysisText(text: string): ParsedSection[] {
  if (!text || !text.trim()) {
    return [];
  }

  console.log("[Parser] Input text length:", text.length);
  
  const sections: ParsedSection[] = [];
  
  const splitPattern = /(✅\s*Your Right:|⚠️\s*Warning Found:|🚨\s*Predatory [Cc]lause [Dd]etected:)/g;
  const parts = text.split(splitPattern);
  
  console.log("[Parser] Split into", parts.length, "parts");
  
  let currentType: 'intro' | 'right' | 'warning' | 'predatory' | 'text' = 'text';
  
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i]?.trim();
    if (!part) continue;
    
    if (part.match(/✅\s*Your Right:/)) {
      currentType = 'right';
      continue;
    } else if (part.match(/⚠️\s*Warning Found:/)) {
      currentType = 'warning';
      continue; 
    } else if (part.match(/🚨\s*Predatory [Cc]lause/)) {
      currentType = 'predatory';
      continue;
 
    const content = part.trim();
    
    if (content.length < 10 || content.toLowerCase().includes('starting analysis')) {
      continue;
    }
    
    if (sections.length === 0 && currentType === 'text') {
      if (content.toLowerCase().includes('based on your tenancy agreement') ||
          content.toLowerCase().includes('based on the tenancy agreement')) {
        sections.push({
          type: 'intro',
          content: content
        });
        continue;
      }
    }
    
    sections.push({
      type: currentType,
      content: content
    });
    
    console.log(`[Parser] Added ${currentType}: ${content.substring(0, 50)}...`);
  }

  console.log("[Parser] Total sections:", sections.length);
  return sections;
}

