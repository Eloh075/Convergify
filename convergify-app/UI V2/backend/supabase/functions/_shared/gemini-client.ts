// Gemini API client for LLM operations
// Uses multiple API keys with rotation for rate limit handling

const GEMINI_API_KEYS = [
  Deno.env.get('GEMINI_API_KEY') ?? '',
  Deno.env.get('GEMINI_API_KEY1') ?? '',
  Deno.env.get('GEMINI_API_KEY2') ?? '',
  Deno.env.get('GEMINI_API_KEY3') ?? '',
  Deno.env.get('GEMINI_API_KEY4') ?? '',
  Deno.env.get('GEMINI_API_KEY5') ?? '',
  Deno.env.get('GEMINI_API_KEY6') ?? '',
  Deno.env.get('GEMINI_API_KEY7') ?? '',
  Deno.env.get('GEMINI_API_KEY8') ?? '',
  Deno.env.get('GEMINI_API_KEY9') ?? '',
  Deno.env.get('GEMINI_API_KEY10') ?? '',
  Deno.env.get('GEMINI_API_KEY11') ?? '',
  Deno.env.get('GEMINI_API_KEY12') ?? '',
].filter(key => key.length > 0);

let currentKeyIndex = 0;

function getNextApiKey(): string {
  if (GEMINI_API_KEYS.length === 0) {
    throw new Error('No Gemini API keys configured');
  }
  const key = GEMINI_API_KEYS[currentKeyIndex];
  currentKeyIndex = (currentKeyIndex + 1) % GEMINI_API_KEYS.length;
  return key;
}

export interface GeminiResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text: string;
      }>;
    };
  }>;
}

export async function callGemini(
  prompt: string,
  retries = 3
): Promise<string> {
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const apiKey = getNextApiKey();
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            contents: [{
              parts: [{
                text: prompt
              }]
            }],
            generationConfig: {
              temperature: 0.1,
              maxOutputTokens: 2048,
            }
          })
        }
      );

      if (!response.ok) {
        const error = await response.text();
        console.error(`Gemini API error (attempt ${attempt + 1}):`, error);
        
        // If rate limited, try next key
        if (response.status === 429 && attempt < retries - 1) {
          continue;
        }
        
        throw new Error(`Gemini API error: ${response.status} - ${error}`);
      }

      const data: GeminiResponse = await response.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
      
      if (!text) {
        throw new Error('No text in Gemini response');
      }
      
      return text;
    } catch (error) {
      console.error(`Gemini API call failed (attempt ${attempt + 1}):`, error);
      
      if (attempt === retries - 1) {
        throw error;
      }
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
    }
  }
  
  throw new Error('Failed to call Gemini API after all retries');
}

export async function extractJSON<T>(prompt: string): Promise<T> {
  const response = await callGemini(prompt);
  
  // Try to extract JSON from response (handle markdown code blocks)
  let jsonText = response.trim();
  
  // Remove markdown code blocks if present
  if (jsonText.startsWith('```json')) {
    jsonText = jsonText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
  } else if (jsonText.startsWith('```')) {
    jsonText = jsonText.replace(/^```\s*/, '').replace(/\s*```$/, '');
  }
  
  // Remove any text before the first [ or {
  const jsonStart = Math.min(
    jsonText.indexOf('[') >= 0 ? jsonText.indexOf('[') : Infinity,
    jsonText.indexOf('{') >= 0 ? jsonText.indexOf('{') : Infinity
  );
  if (jsonStart !== Infinity && jsonStart > 0) {
    jsonText = jsonText.substring(jsonStart);
  }
  
  // Remove any text after the last ] or }
  const jsonEnd = Math.max(
    jsonText.lastIndexOf(']'),
    jsonText.lastIndexOf('}')
  );
  if (jsonEnd >= 0 && jsonEnd < jsonText.length - 1) {
    jsonText = jsonText.substring(0, jsonEnd + 1);
  }
  
  // Try parsing with multiple strategies
  const strategies = [
    // Strategy 1: Parse as-is
    () => JSON.parse(jsonText),
    
    // Strategy 2: Fix common JSON issues (unescaped quotes, newlines)
    () => {
      const fixed = jsonText
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r')
        .replace(/\t/g, '\\t');
      return JSON.parse(fixed);
    },
    
    // Strategy 3: Try to fix unterminated strings by finding matching brackets
    () => {
      // Find the outermost array/object boundaries
      let depth = 0;
      let inString = false;
      let escape = false;
      let validEnd = -1;
      
      for (let i = 0; i < jsonText.length; i++) {
        const char = jsonText[i];
        
        if (escape) {
          escape = false;
          continue;
        }
        
        if (char === '\\') {
          escape = true;
          continue;
        }
        
        if (char === '"' && !escape) {
          inString = !inString;
          continue;
        }
        
        if (inString) continue;
        
        if (char === '[' || char === '{') {
          depth++;
        } else if (char === ']' || char === '}') {
          depth--;
          if (depth === 0) {
            validEnd = i;
            break;
          }
        }
      }
      
      if (validEnd > 0) {
        const truncated = jsonText.substring(0, validEnd + 1);
        return JSON.parse(truncated);
      }
      
      throw new Error('Could not find valid JSON boundaries');
    },
    
    // Strategy 4: Remove control characters and try again
    () => {
      const cleaned = jsonText.replace(/[\x00-\x1F\x7F]/g, '');
      return JSON.parse(cleaned);
    }
  ];
  
  let lastError: Error | null = null;
  
  for (let i = 0; i < strategies.length; i++) {
    try {
      const result = strategies[i]();
      if (i > 0) {
        console.log(`JSON parsing succeeded with strategy ${i + 1}`);
      }
      return result as T;
    } catch (error) {
      lastError = error as Error;
      console.log(`Strategy ${i + 1} failed:`, error.message);
    }
  }
  
  // All strategies failed
  console.error('All JSON parsing strategies failed');
  console.error('Original response:', response.substring(0, 500));
  console.error('Extracted JSON text:', jsonText.substring(0, 500));
  throw new Error(`Invalid JSON in Gemini response: ${lastError?.message}`);
}
