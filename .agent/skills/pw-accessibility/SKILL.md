---
name: pw-accessibility
description: Use this skill when the user wants to fix accessibility issues, improve the Accessibility score, add ARIA labels, fix contrast, enable keyboard navigation, or do a pre-submission a11y sweep.
---

# pw-accessibility

## Goal
Fix all accessibility issues that affect the PromptWars Accessibility scoring criterion in under 10 minutes.

## Instructions

### Step 1: HTML Audit Checklist
Scan `static/index.html` and fix each:

**1. lang attribute on html tag:**
```html
<html lang="en">  <!-- REQUIRED -->
```

**2. Every button needs accessible label:**
```html
<!-- BAD -->
<button onclick="submit()">→</button>

<!-- GOOD -->
<button onclick="submit()" aria-label="Submit text for analysis">→</button>
```

**3. Every input needs a label:**
```html
<!-- BAD -->
<input type="text" placeholder="Enter text">

<!-- GOOD -->
<label for="disaster-input">Enter disaster message</label>
<input id="disaster-input" type="text" 
       placeholder="Paste any text in Telugu, Hindi, English..."
       aria-describedby="input-hint">
<small id="input-hint">Supports 6 Indian languages</small>
```

**4. Loading states must be announced:**
```html
<div id="loading" role="status" aria-live="polite" aria-label="Processing...">
  <span class="spinner" aria-hidden="true"></span>
  <span>Analyzing...</span>
</div>
```

**5. Results must be announced:**
```html
<div id="result-card" role="region" aria-label="Emergency response card" aria-live="assertive">
  <!-- results go here -->
</div>
```

**6. Error messages must be associated:**
```html
<input id="disaster-input" aria-describedby="error-msg">
<div id="error-msg" role="alert" aria-live="assertive"></div>
```

**7. Skip navigation link:**
```html
<!-- First element in body -->
<a href="#main-content" class="skip-link">Skip to main content</a>
<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #1a73e8;
  color: white;
  padding: 8px 16px;
  z-index: 1000;
  text-decoration: none;
  border-radius: 0 0 4px 0;
}
.skip-link:focus { top: 0; }
</style>
```

**8. Main content landmark:**
```html
<main id="main-content">
  <!-- all primary content -->
</main>
```

### Step 2: Keyboard Navigation
Add to `app.js`:
```javascript
// Allow Enter key to trigger submit
document.getElementById('disaster-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    document.getElementById('submit-btn').click();
  }
});

// Focus management — move focus to result on completion
async function processText() {
  // ... existing logic
  const result = await callAPI(text);
  renderResult(result);
  // Move focus to result for screen reader
  document.getElementById('result-card').focus();
}
```

### Step 3: Contrast Ratios
Safe colour pairs (all pass 4.5:1):
```css
/* Primary text */
color: #202124;  /* on white — ratio 16.1:1 */
color: #ffffff;  /* on #1a73e8 blue — ratio 4.6:1 */
color: #ffffff;  /* on #34a853 green — ratio 4.5:1 */
color: #202124;  /* on #fef7e0 yellow — ratio 13:1 */

/* Danger/severity */
color: #c62828;  /* on white — ratio 5.9:1 */

/* Muted text — use this minimum */
color: #5f6368;  /* on white — ratio 5.9:1 */

/* AVOID these common failures */
/* color: #9aa0a6 on white — ratio 2.7:1 FAILS */
/* color: #fbbc04 on white — ratio 1.9:1 FAILS */
```

### Step 4: Meta tags for accessibility signals
```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Emergency information card generator — converts disaster text in 6 Indian languages into clear action cards">
  <title>Disaster Response Assistant — PromptWars</title>
</head>
```

### Step 5: Severity Card — accessible colour coding
Don't rely on colour alone — always add text/icon:
```html
<!-- BAD: colour only -->
<div class="card high" style="background: red">Zone 3</div>

<!-- GOOD: colour + text + icon -->
<div class="card" role="status" aria-label="High severity alert">
  <span class="severity-badge high" aria-hidden="true">⚠</span>
  <span class="severity-text">HIGH SEVERITY</span>
  Zone 3 — Immediate evacuation required
</div>
```

### Step 6: Responsive / Mobile
```css
@media (max-width: 600px) {
  .container { padding: 16px; }
  button { width: 100%; padding: 14px; font-size: 16px; }
  input { font-size: 16px; } /* prevents iOS zoom */
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Output Format
```
♿ Accessibility Audit Results:
  ✅ lang attribute on <html>
  ✅ All buttons have aria-label
  ✅ All inputs have associated <label>
  ✅ Loading state uses role="status"
  ✅ Results use aria-live="assertive"
  ✅ Skip navigation link present
  ✅ <main> landmark present
  ✅ Keyboard navigation works (Enter to submit)
  ✅ Focus moves to result on completion
  ✅ All contrast ratios pass 4.5:1
  ✅ Meta description present
  ✅ prefers-reduced-motion respected

Accessibility: READY FOR SUBMISSION
```
