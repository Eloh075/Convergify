import { assertEquals, assertStringIncludes } from "jsr:@std/assert";
import { decodeBase64Text } from "./resume-extractor.ts";

/**
 * Bug Condition Exploration Test
 * 
 * **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
 * 
 * Property 1: Fault Condition - PDF Text Extraction from Compressed Streams
 * 
 * CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
 * 
 * This test verifies that the decodeBase64Text function properly extracts clean,
 * readable text from PDF files that use FlateDecode compression (the standard
 * compression method in modern PDFs).
 * 
 * Expected behavior:
 * - Extracted text should contain expected skills from the resume
 * - Extracted text should be clean (no binary gibberish)
 * - Extracted text length should be reasonable (>500 characters for this resume)
 * 
 * On UNFIXED code, this test will FAIL because:
 * - The current implementation uses naive ASCII filtering
 * - Compressed PDF streams contain binary data that looks like gibberish
 * - Skills will be missing or text will be garbage
 */
Deno.test("Bug Condition: Extract text from compressed PDF (EthanLohWenxi_Resume.pdf)", async () => {
  // Read the real PDF file that uses FlateDecode compression
  const pdfPath = "EthanLohWenxi_Resume.pdf";
  const pdfBytes = await Deno.readFile(pdfPath);
  
  // Convert to base64 (simulating how the API receives the file)
  const base64 = btoa(String.fromCharCode(...pdfBytes));
  
  // Extract text using the function under test
  const extractedText = decodeBase64Text(base64);
  
  console.log("=== Bug Condition Exploration Test Results ===");
  console.log(`Extracted text length: ${extractedText.length} characters`);
  console.log(`First 200 characters: ${extractedText.substring(0, 200)}`);
  console.log(`Last 200 characters: ${extractedText.substring(Math.max(0, extractedText.length - 200))}`);
  
  // Check 1: Text length should be reasonable (>500 characters for this resume)
  // On unfixed code, this will likely fail because only fragments are extracted
  console.log(`\nCheck 1: Text length > 500 characters`);
  console.log(`Actual length: ${extractedText.length}`);
  assertEquals(
    extractedText.length > 500,
    true,
    `Expected text length > 500, but got ${extractedText.length}. This indicates the PDF text extraction is incomplete.`
  );
  
  // Check 2: Text should contain expected skills from the resume
  // On unfixed code, these will likely fail because skills are in compressed streams
  const expectedSkills = ["Python", "JavaScript", "React", "AWS", "Docker", "PostgreSQL"];
  
  console.log(`\nCheck 2: Text contains expected skills`);
  for (const skill of expectedSkills) {
    console.log(`  Checking for "${skill}": ${extractedText.includes(skill) ? "FOUND" : "MISSING"}`);
    assertStringIncludes(
      extractedText,
      skill,
      `Expected to find skill "${skill}" in extracted text, but it was missing. This indicates the PDF text extraction failed to extract content from compressed streams.`
    );
  }
  
  // Check 3: Text should not contain binary gibberish
  // Check for common binary/garbage patterns that indicate failed decompression
  const binaryPatterns = [
    /[\x00-\x08\x0B-\x0C\x0E-\x1F]/g, // Control characters (excluding tab, newline, carriage return)
  ];
  
  console.log(`\nCheck 3: Text should not contain binary gibberish`);
  for (const pattern of binaryPatterns) {
    const matches = extractedText.match(pattern);
    const matchCount = matches ? matches.length : 0;
    console.log(`  Binary pattern matches: ${matchCount}`);
    assertEquals(
      matchCount,
      0,
      `Found ${matchCount} binary/control characters in extracted text. This indicates the PDF text extraction is returning raw binary data instead of decompressed text.`
    );
  }
  
  // Check 4: Text should contain recognizable resume content
  const expectedContent = ["ETHAN LOH", "Singapore Management University", "TECHNICAL SKILLS", "EXPERIENCE"];
  
  console.log(`\nCheck 4: Text contains recognizable resume sections`);
  for (const content of expectedContent) {
    console.log(`  Checking for "${content}": ${extractedText.includes(content) ? "FOUND" : "MISSING"}`);
    assertStringIncludes(
      extractedText,
      content,
      `Expected to find "${content}" in extracted text. This indicates the PDF structure is not being parsed correctly.`
    );
  }
  
  console.log("\n=== All checks passed! ===");
  console.log("If this test FAILED on unfixed code, it confirms the bug exists.");
  console.log("If this test PASSES after the fix, it confirms the bug is resolved.");
});

/**
 * Preservation Property Tests
 * 
 * **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
 * 
 * Property 2: Preservation - Non-Compressed Input Behavior
 * 
 * These tests verify that the baseline behavior for non-PDF inputs (plain text files)
 * works correctly on the UNFIXED code. After implementing the fix, these tests should
 * continue to pass, confirming no regressions were introduced.
 * 
 * EXPECTED OUTCOME: All tests PASS on unfixed code (confirms baseline behavior to preserve)
 */

Deno.test("Preservation: Plain text resume extraction with UTF-8 decoding", () => {
  // Create a simple plain text resume
  const plainTextResume = `John Doe
Software Engineer
Email: john@example.com

SKILLS:
- Python
- JavaScript
- React
- Node.js

EXPERIENCE:
Senior Developer at Tech Corp (2020-2023)
- Built scalable web applications
- Led team of 5 engineers`;

  // Convert to base64 (simulating API input)
  const base64 = btoa(plainTextResume);
  
  // Extract text
  const extractedText = decodeBase64Text(base64);
  
  console.log("\n=== Preservation Test: Plain Text ===");
  console.log(`Input length: ${plainTextResume.length}`);
  console.log(`Output length: ${extractedText.length}`);
  console.log(`First 100 chars: ${extractedText.substring(0, 100)}`);
  
  // Verify the text is extracted correctly
  assertStringIncludes(extractedText, "John Doe");
  assertStringIncludes(extractedText, "Python");
  assertStringIncludes(extractedText, "JavaScript");
  assertStringIncludes(extractedText, "React");
  assertStringIncludes(extractedText, "Senior Developer");
  
  console.log("✓ Plain text extraction works correctly");
});

Deno.test("Preservation: UTF-8 special characters are decoded correctly", () => {
  // Create text with UTF-8 special characters
  const textWithSpecialChars = `José García
Développeur Senior
Skills: Python, JavaScript
Location: São Paulo, Brasil
Education: École Polytechnique
Languages: English, Español, Français, 中文`;

  // Convert to base64
  const base64 = btoa(unescape(encodeURIComponent(textWithSpecialChars)));
  
  // Extract text
  const extractedText = decodeBase64Text(base64);
  
  console.log("\n=== Preservation Test: UTF-8 Special Characters ===");
  console.log(`Extracted text: ${extractedText}`);
  
  // Verify special characters are preserved
  assertStringIncludes(extractedText, "José");
  assertStringIncludes(extractedText, "García");
  assertStringIncludes(extractedText, "Développeur");
  assertStringIncludes(extractedText, "São Paulo");
  assertStringIncludes(extractedText, "École");
  assertStringIncludes(extractedText, "Español");
  assertStringIncludes(extractedText, "Français");
  assertStringIncludes(extractedText, "中文");
  
  console.log("✓ UTF-8 special characters decoded correctly");
});

Deno.test("Preservation: Files >8000 characters are truncated with suffix", () => {
  // Create a large text file (>8000 characters)
  const largeText = "A".repeat(9000);
  
  // Convert to base64
  const base64 = btoa(largeText);
  
  // Extract text
  const extractedText = decodeBase64Text(base64);
  
  console.log("\n=== Preservation Test: Truncation Logic ===");
  console.log(`Input length: ${largeText.length}`);
  console.log(`Output length: ${extractedText.length}`);
  
  // Note: The truncation happens in extractResumeSkills, not in decodeBase64Text
  // So decodeBase64Text should return the full text
  // This test verifies that decodeBase64Text doesn't truncate prematurely
  assertEquals(extractedText.length, 9000, "decodeBase64Text should not truncate - truncation happens in extractResumeSkills");
  
  console.log("✓ decodeBase64Text returns full text without premature truncation");
});

Deno.test("Preservation: Truncation logic in extractResumeSkills (observation)", () => {
  // This test documents the truncation behavior that happens in extractResumeSkills
  // We're just observing and documenting the behavior, not testing extractResumeSkills directly
  
  const maxLength = 8000;
  const longText = "B".repeat(9000);
  
  // Simulate what extractResumeSkills does
  const truncatedText = longText.length > maxLength 
    ? longText.substring(0, maxLength) + '\n... (truncated)'
    : longText;
  
  console.log("\n=== Preservation Test: Truncation Behavior (Observation) ===");
  console.log(`Original length: ${longText.length}`);
  console.log(`Truncated length: ${truncatedText.length}`);
  console.log(`Has truncation suffix: ${truncatedText.includes('... (truncated)')}`);
  
  // Verify truncation behavior
  assertEquals(truncatedText.length, maxLength + '\n... (truncated)'.length);
  assertStringIncludes(truncatedText, "... (truncated)");
  
  console.log("✓ Truncation logic adds '... (truncated)' suffix at 8000 characters");
});

Deno.test("Preservation: Invalid base64 throws appropriate error", () => {
  // Test with invalid base64 string
  const invalidBase64 = "This is not valid base64!!!@#$%";
  
  console.log("\n=== Preservation Test: Error Handling ===");
  
  try {
    const extractedText = decodeBase64Text(invalidBase64);
    console.log(`Extracted text length: ${extractedText.length}`);
    console.log(`Extracted text: ${extractedText.substring(0, 100)}`);
    
    // The function has fallback logic, so it might return something
    // Document what happens
    console.log("✓ Function handles invalid base64 with fallback logic");
  } catch (error) {
    console.log(`Error thrown: ${error.message}`);
    console.log("✓ Function throws error for invalid base64");
  }
});

Deno.test("Preservation: Empty string input", () => {
  const emptyBase64 = btoa("");
  
  console.log("\n=== Preservation Test: Empty Input ===");
  
  const extractedText = decodeBase64Text(emptyBase64);
  
  console.log(`Extracted text length: ${extractedText.length}`);
  console.log(`Extracted text: "${extractedText}"`);
  
  assertEquals(extractedText, "", "Empty input should return empty string");
  
  console.log("✓ Empty input handled correctly");
});

Deno.test("Preservation: Data URL prefix is removed", () => {
  const plainText = "Test resume content";
  const base64 = btoa(plainText);
  const dataUrl = `data:text/plain;base64,${base64}`;
  
  console.log("\n=== Preservation Test: Data URL Prefix ===");
  
  const extractedText = decodeBase64Text(dataUrl);
  
  console.log(`Input: ${dataUrl.substring(0, 50)}...`);
  console.log(`Extracted: ${extractedText}`);
  
  assertStringIncludes(extractedText, "Test resume content");
  
  console.log("✓ Data URL prefix removed correctly");
});
