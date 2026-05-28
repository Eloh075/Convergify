# Available Gemini Models

**Last Updated:** 2026-03-06

## Current Available Models (v1 API)

| Model Name | Display Name | Best For |
|------------|--------------|----------|
| `gemini-2.5-flash` | Gemini 2.5 Flash | **RECOMMENDED** - Fast, efficient, latest version |
| `gemini-2.5-pro` | Gemini 2.5 Pro | Complex reasoning, longer context |
| `gemini-2.0-flash` | Gemini 2.0 Flash | Previous generation flash |
| `gemini-2.0-flash-001` | Gemini 2.0 Flash 001 | Specific version |
| `gemini-2.0-flash-lite-001` | Gemini 2.0 Flash-Lite 001 | Lightweight tasks |
| `gemini-2.0-flash-lite` | Gemini 2.0 Flash-Lite | Lightweight tasks |
| `gemini-2.5-flash-lite` | Gemini 2.5 Flash-Lite | Lightweight, latest |

## Deprecated Models

- ❌ `gemini-1.5-flash` - NO LONGER AVAILABLE
- ❌ `gemini-1.5-pro` - NO LONGER AVAILABLE
- ❌ `gemini-1.0-pro` - NO LONGER AVAILABLE

## API Endpoint

```
https://generativelanguage.googleapis.com/v1/models/{model-name}:generateContent?key={api-key}
```

**Note:** Use `v1` API, NOT `v1beta`

## Current Usage in Project

- **Resume Parsing:** `gemini-2.5-flash` (fast, efficient for text extraction)
- **Skill Extraction:** `gemini-2.5-flash` (good balance of speed and accuracy)
- **Gap Analysis:** No LLM needed (pure logic)

## How to Check Available Models

```bash
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"
```

## IMPORTANT: Always Check Before Updating

Before changing any Gemini model references in code:
1. Read this file first
2. Verify the model is still available
3. Update this file if models have changed
4. Use `gemini-2.5-flash` as default unless you need pro features
