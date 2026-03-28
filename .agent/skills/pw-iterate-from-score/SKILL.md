---
name: pw-iterate-from-score
description: Use this skill when the user has received a submission score and wants to improve it. Takes the score breakdown and tells the agent exactly what to fix next to maximize the next attempt's score.
---

# pw-iterate-from-score

## Goal
Given a score breakdown from a PromptWars submission, identify the single highest-impact fix and implement it precisely. This is the winner's loop — read score, target lowest, fix it, resubmit.

## Scoring Criteria (from real Hyderabad event)
The six scored axes are:
1. **Code Quality** — modular architecture, clean functions, docstrings, Pydantic models
2. **Security** — no hardcoded secrets, CORS, CSP, input validation, rate limiting
3. **Efficiency** — response time, async operations, lazy loading, caching
4. **Testing** — number of tests, coverage, edge cases. 50+ tests = full marks
5. **Accessibility** — ARIA labels, keyboard nav, contrast, screen reader support
6. **Google Services** — count AND depth of GCP integrations

## Instructions

### Step 1: Parse the Score
When the user provides scores, format them:
```
Code Quality:    [score]
Security:        [score]
Efficiency:      [score]
Testing:         [score]
Accessibility:   [score]
Google Services: [score]
```

### Step 2: Prioritise the Fix
Pick the LOWEST score. If tied, use this tiebreaker order:
1. Google Services (highest ceiling gain)
2. Security (most achievable quick wins)
3. Testing (pure volume — generate more tests)
4. Code Quality (refactor to modular structure)
5. Efficiency (add async, caching)
6. Accessibility (ARIA sweep)

### Step 3: Execute the Fix

#### If Google Services is lowest:
- Check which services are already integrated (scan imports)
- Add the next highest-value service not yet used:
  - Not using Cloud Logging? → Add it (10 mins, massive signal)
  - Not using Firestore? → Add results persistence
  - Not using Cloud Translation? → Add if app handles text
  - Not using Cloud Storage? → Add file export/upload
- Show the exact import + initialization code to add
- Update `requirements.txt`

#### If Security is lowest:
- Run a full security sweep:
  1. Scan for hardcoded secrets: `grep -rn "AIza\|sk-\|password\s*=\|api_key\s*=" src/`
  2. Check CORS middleware exists in `main.py`
  3. Check CSP header is set
  4. Check all endpoints validate inputs with Pydantic
  5. Check `.env` is in `.gitignore`
  6. Add rate limiting: `pip install slowapi`
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter

  @app.post("/process")
  @limiter.limit("10/minute")
  async def process(request: Request, data: InputModel):
      ...
  ```

#### If Testing is lowest:
Immediately run `pw-test-generator` skill to generate 50+ tests.
Target test count = current_count + (50 - current_count) minimum.

Key test patterns to generate:
```python
# Happy path
def test_valid_input_returns_200():
def test_response_has_required_fields():

# Edge cases  
def test_empty_input_returns_400():
def test_oversized_input_returns_400():
def test_special_characters_handled():
def test_unicode_input_handled():

# Error cases
def test_gemini_failure_returns_500():
def test_firestore_failure_handled_gracefully():

# Security
def test_input_too_long_rejected():
def test_null_input_rejected():
def test_injection_attempt_sanitized():
```

#### If Code Quality is lowest:
- Audit file structure — is it modular?
- Move any logic from `main.py` into `src/services/`
- Add docstrings to every function missing them:
  ```python
  def process_text(text: str, language: str) -> dict:
      """
      Process multilingual disaster text and return structured emergency card.
      
      Args:
          text: Raw input text in any supported language
          language: ISO 639-1 language code (e.g., 'te', 'hi', 'en')
          
      Returns:
          dict with keys: severity, action, evacuate, contacts, translated_text
          
      Raises:
          HTTPException: On invalid input or AI service failure
      """
  ```
- Ensure no function exceeds 40 lines (extract helpers)
- Add Pydantic models for all request/response shapes

#### If Efficiency is lowest:
- Add async to all I/O operations
- Add simple in-memory cache for repeated inputs:
  ```python
  from functools import lru_cache
  import hashlib
  
  _cache = {}
  
  async def cached_gemini_call(prompt: str) -> str:
      key = hashlib.md5(prompt.encode()).hexdigest()
      if key in _cache:
          return _cache[key]
      result = await call_gemini(prompt)
      _cache[key] = result
      return result
  ```
- Add response compression: `pip install brotli`
  ```python
  from fastapi.middleware.gzip import GZipMiddleware
  app.add_middleware(GZipMiddleware, minimum_size=1000)
  ```

#### If Accessibility is lowest:
Immediately run `pw-accessibility` skill.

### Step 4: After Fixing
1. Run `pytest tests/ -v` — must pass 0 failures
2. Run `pw-security-hardening` skill — quick final check
3. `git commit -m "attempt [N]: improve [criterion] from [old]% to target"`
4. Run `pw-deploy-cloud-run` skill
5. Submit and record new score

## Output Format
```
📊 Current Scores:
  Code Quality:    [X]%
  Security:        [X]%  
  Efficiency:      [X]%
  Testing:         [X]%
  Accessibility:   [X]%
  Google Services: [X]%

🎯 Target: [criterion] ([X]% → ~100%)
⚡ Fix: [specific action]
📝 Estimated time: [N] minutes
```
