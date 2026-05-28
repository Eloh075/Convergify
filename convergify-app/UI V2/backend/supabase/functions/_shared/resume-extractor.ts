import { createClient } from 'jsr:@supabase/supabase-js@2';
import { callGemini } from './gemini-client.ts';

/**
 * Extract text content from a PDF file using simple parsing
 * 
 * This function extracts text from PDF files by:
 * 1. Finding text content streams in the PDF structure
 * 2. Decompressing FlateDecode streams using pako
 * 3. Extracting text between BT/ET (Begin Text/End Text) operators
 * 
 * @param pdfBinary - PDF file data as binary string
 * @returns Extracted text content
 */
async function extractPDFText(pdfBinary: string): Promise<string> {
  try {
    console.log(`Parsing PDF structure (${pdfBinary.length} bytes)...`);
    
    // Import pako for zlib decompression
    const pako = await import('npm:pako@2.1.0');
    
    let extractedText = '';
    
    // Find all stream objects with FlateDecode filter
    const streamRegex = /stream\s+([\s\S]*?)\s+endstream/g;
    const flateDecodeRegex = /\/FlateDecode/;
    
    let match;
    let streamCount = 0;
    let decompressedCount = 0;
    
    while ((match = streamRegex.exec(pdfBinary)) !== null) {
      streamCount++;
      const streamData = match[1];
      
      // Check if this stream uses FlateDecode compression
      const beforeStream = pdfBinary.substring(Math.max(0, match.index - 200), match.index);
      
      if (flateDecodeRegex.test(beforeStream)) {
        try {
          // Convert stream data to Uint8Array
          const streamBytes = new Uint8Array(streamData.length);
          for (let i = 0; i < streamData.length; i++) {
            streamBytes[i] = streamData.charCodeAt(i) & 0xFF;
          }
          
          // Decompress using pako
          const decompressed = pako.inflate(streamBytes, { to: 'string' });
          decompressedCount++;
          
          // Extract text content from decompressed stream
          // Look for text between BT (Begin Text) and ET (End Text) operators
          const textMatches = decompressed.match(/\(([^)]+)\)/g);
          if (textMatches) {
            for (const textMatch of textMatches) {
              const text = textMatch.slice(1, -1) // Remove parentheses
                .replace(/\\n/g, '\n')
                .replace(/\\r/g, '\r')
                .replace(/\\t/g, '\t')
                .replace(/\\\\/g, '\\')
                .replace(/\\([()])/g, '$1');
              extractedText += text + ' ';
            }
          }
        } catch (decompressError) {
          // Skip streams that fail to decompress
          console.log(`Failed to decompress stream ${streamCount}:`, decompressError.message);
        }
      }
    }
    
    console.log(`Processed ${streamCount} streams, decompressed ${decompressedCount}`);
    console.log(`Extracted ${extractedText.length} characters from PDF`);
    
    if (extractedText.length === 0) {
      throw new Error('No text content found in PDF. The PDF may be image-based or use unsupported encoding.');
    }
    
    return extractedText.trim();
  } catch (error) {
    console.error('PDF text extraction failed:', error);
    throw new Error(`Failed to extract text from PDF: ${error.message}`);
  }
}

export async function extractResumeSkills(
  resumeBase64: string,
  supabaseUrl: string,
  supabaseKey: string
): Promise<string[]> {
  try {
    // Step 1: Decode base64 and extract text
    const resumeText = await decodeBase64Text(resumeBase64);
    
    // Sanitize text to prevent JSON parsing issues
    // Remove control characters and normalize whitespace
    const sanitizedText = resumeText
      .replace(/[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]/g, '') // Remove control chars except \t, \n, \r
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();
    
    // Truncate if too long (Gemini has token limits)
    const maxLength = 8000; // ~2000 tokens
    const truncatedText = sanitizedText.length > maxLength 
      ? sanitizedText.substring(0, maxLength) + '\n... (truncated)'
      : sanitizedText;
    
    console.log(`Resume text length: ${sanitizedText.length}, truncated: ${truncatedText.length}`);
    
    // Step 2: Extract skills using Gemini
    const prompt = `You are a resume parser. Extract all technical and soft skills from this resume text.

Return ONLY a simple list of skills, one per line. No numbering, no bullets, no explanations.

Resume Text:
${truncatedText}

Example output format:
Python
JavaScript
Leadership
Communication

Skills to extract:
- Programming languages
- Frameworks and libraries
- Tools and platforms
- Databases
- Cloud services
- Soft skills
- Domain knowledge

IMPORTANT: Return ONLY skill names, one per line. Nothing else.`;

    const response = await callGemini(prompt);
    
    // Parse line-by-line response
    const extractedSkills = response
      .trim()
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0 && line.length < 100) // Filter out empty lines and overly long lines
      .filter(line => !line.startsWith('#') && !line.startsWith('-') && !line.startsWith('*')) // Remove markdown
      .map(line => line.replace(/^\d+\.\s*/, '')) // Remove numbering
      .filter((skill, index, self) => self.indexOf(skill) === index); // Remove duplicates
    
    console.log(`Extracted ${extractedSkills.length} skills from resume`);
    
    // Step 3: Normalize against canonical skills
    const supabase = createClient(supabaseUrl, supabaseKey);
    const { data: canonicalSkills } = await supabase
      .from('canonical_skills')
      .select('canonical_name');
    
    if (!canonicalSkills) {
      return extractedSkills;
    }
    
    const canonicalMap = new Map<string, string>();
    canonicalSkills.forEach(s => {
      canonicalMap.set(s.canonical_name.toLowerCase(), s.canonical_name);
    });
    
    // Normalize extracted skills
    const normalizedSkills = extractedSkills
      .map(skill => {
        const lowerSkill = skill.toLowerCase().trim();
        
        // Exact match
        if (canonicalMap.has(lowerSkill)) {
          return canonicalMap.get(lowerSkill)!;
        }
        
        // Fuzzy match (check if canonical skill contains the extracted skill or vice versa)
        for (const [canonical, originalName] of canonicalMap.entries()) {
          if (canonical.includes(lowerSkill) || lowerSkill.includes(canonical)) {
            return originalName;
          }
        }
        
        // No match found, return original
        return skill;
      })
      .filter((skill, index, self) => self.indexOf(skill) === index); // Remove duplicates
    
    console.log(`Normalized to ${normalizedSkills.length} skills`);
    return normalizedSkills;
  } catch (error) {
    console.error('Error extracting resume skills:', error);
    throw new Error(`Failed to extract resume skills: ${error.message}`);
  }
}

export async function decodeBase64Text(base64: string): Promise<string> {
  try {
    // Remove data URL prefix if present
    const base64Data = base64.replace(/^data:.*?;base64,/, '');
    
    // Decode base64
    const decoded = atob(base64Data);
    
    // Check if it's a PDF (starts with %PDF)
    if (decoded.startsWith('%PDF')) {
      console.log('Detected PDF file - using pako for FlateDecode decompression');
      
      // Use custom PDF text extraction with pako decompression
      const textContent = await extractPDFText(decoded);
      
      console.log(`Extracted ${textContent.length} characters from PDF`);
      return textContent;
    }
    
    // For non-PDF files, try UTF-8 decoding
    return decodeURIComponent(escape(decoded));
  } catch (error) {
    console.error('Failed to decode base64:', error);
    // If decoding fails, try to extract printable characters
    try {
      const base64Data = base64.replace(/^data:.*?;base64,/, '');
      const decoded = atob(base64Data);
      const textContent = decoded
        .split('')
        .filter(char => {
          const code = char.charCodeAt(0);
          return (code >= 32 && code <= 126) || code === 10 || code === 13;
        })
        .join('')
        .replace(/\s+/g, ' ')
        .trim();
      return textContent;
    } catch (fallbackError) {
      console.error('Fallback extraction also failed:', fallbackError);
      return base64; // Last resort
    }
  }
}
