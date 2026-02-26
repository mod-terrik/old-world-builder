# Integration Guide: Composition Notes

This guide will help you integrate the composition notes feature into your existing print functionality.

## Step 1: Import the Required Files

First, import the CSS file in your main application or where you handle printing:

```javascript
// In your main App component or index file
import './styles/comp-notes.css';
```

Or in your HTML:

```html
<link rel="stylesheet" href="/src/styles/comp-notes.css">
```

## Step 2: Import the Comp Notes Functions

In the file where you handle printing (likely where you have the three-dot dropdown menu), add:

```javascript
import { addCompNotesToPrint } from '../utils/comp-notes-handler';
import { rulesMap } from '../components/rules-index/rules-map';
```

## Step 3: Locate Your Print Function

Find where you generate the HTML for printing units. This is likely in a component that:
- Handles the "Print" button click from the three-dot dropdown
- Generates HTML for each unit in the army
- Displays special rules for each unit

It might look something like this:

```javascript
function generateUnitHTML(unit) {
  return `
    <div class="unit-card">
      <h3>${unit.name}</h3>
      <div class="stats">...</div>
      <div class="special-rules">
        <h4>Special Rules</h4>
        ${unit.specialRules.map(rule => `<p>${rule}</p>`).join('')}
      </div>
    </div>
  `;
}
```

## Step 4: Add Comp Notes to the Output

Modify your function to include the comp notes:

```javascript
function generateUnitHTML(unit) {
  return `
    <div class="unit-card">
      <h3>${unit.name}</h3>
      <div class="stats">...</div>
      <div class="special-rules">
        <h4>Special Rules</h4>
        ${unit.specialRules.map(rule => `<p>${rule}</p>`).join('')}
        
        <!-- ADD THIS LINE -->
        ${addCompNotesToPrint(unit, rulesMap)}
      </div>
    </div>
  `;
}
```

## Step 5: Add Comp Notes to Your Rules Files

### Option A: Using rules-index-export.json

Open `src/components/rules-index/rules-index-export.json` and add `compNote` fields:

```json
{
  "murderous renegade": {
    "url": "special-rules/murderous-renegade",
    "page": "TRLP, p. 18",
    "compNote": "Renegade ruleset only"
  }
}
```

### Option B: Using rules-map.js

Open `src/components/rules-index/rules-map.js` and add `compNote` fields:

```javascript
const additionalOWBRules = {
  "high elf prince": {
    url: "unit/high-elf-prince",
    compNote: "Max 1 per 1000 points",
    stats: [/*...*/]
  }
};
```

## Common Integration Patterns

### Pattern 1: React Component

```jsx
import React from 'react';
import { addCompNotesToPrint } from '../utils/comp-notes-handler';
import { rulesMap } from '../components/rules-index/rules-map';
import '../styles/comp-notes.css';

function UnitCard({ unit }) {
  return (
    <div className="unit-card">
      <h3>{unit.name}</h3>
      
      <div className="special-rules">
        <h4>Special Rules</h4>
        {unit.specialRules.map(rule => <p key={rule}>{rule}</p>)}
        
        {/* Comp notes rendered as HTML */}
        <div dangerouslySetInnerHTML={{ 
          __html: addCompNotesToPrint(unit, rulesMap) 
        }} />
      </div>
    </div>
  );
}
```

### Pattern 2: Vanilla JavaScript

```javascript
import { addCompNotesToPrint } from './utils/comp-notes-handler.js';
import { rulesMap } from './components/rules-index/rules-map.js';

function renderUnit(unit) {
  const unitElement = document.createElement('div');
  unitElement.className = 'unit-card';
  
  // ... other rendering code ...
  
  const specialRulesDiv = document.createElement('div');
  specialRulesDiv.className = 'special-rules';
  specialRulesDiv.innerHTML = `
    <h4>Special Rules</h4>
    ${renderSpecialRules(unit)}
    ${addCompNotesToPrint(unit, rulesMap)}
  `;
  
  unitElement.appendChild(specialRulesDiv);
  return unitElement;
}
```

### Pattern 3: Template String with Print Window

```javascript
import { addCompNotesToPrint } from './utils/comp-notes-handler.js';
import { rulesMap } from './components/rules-index/rules-map.js';

function printArmy(army) {
  const printWindow = window.open('', '', 'width=800,height=600');
  
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Army Sheet</title>
      <link rel="stylesheet" href="/src/styles/comp-notes.css">
    </head>
    <body>
      ${army.map(unit => `
        <div class="unit-card">
          <h3>${unit.name}</h3>
          <div class="special-rules">
            <h4>Special Rules</h4>
            ${renderSpecialRules(unit)}
            ${addCompNotesToPrint(unit, rulesMap)}
          </div>
        </div>
      `).join('')}
    </body>
    </html>
  `;
  
  printWindow.document.write(htmlContent);
  printWindow.document.close();
  printWindow.print();
}
```

## Step 6: Test Your Integration

1. **Add a test comp note** to one of your units in `rules-map.js` or `rules-index-export.json`
2. **Create an army** with that unit
3. **Click the Print button** from the three-dot dropdown
4. **Verify** the comp notes appear under the Special Rules section

### Example Test Unit:

```json
{
  "high elf prince": {
    "url": "unit/high-elf-prince",
    "compNote": "TEST: This is a comp note!"
  }
}
```

## Troubleshooting

### Comp Notes Not Appearing

1. **Check CSS import**: Make sure `comp-notes.css` is imported
2. **Check function import**: Verify `addCompNotesToPrint` is imported correctly
3. **Check rulesMap**: Ensure the rulesMap is being passed to the function
4. **Console log**: Add `console.log(addCompNotesToPrint(unit, rulesMap))` to see if HTML is generated
5. **Check unit structure**: Verify your unit object has the expected fields (name, mount, weapons, etc.)

### Styling Issues

1. **CSS not loading**: Check browser console for CSS loading errors
2. **Wrong order**: Make sure comp notes CSS is loaded after your main styles
3. **Print preview**: Use browser print preview to check print-specific styles

### Comp Notes Not Found

1. **Case sensitivity**: Rule names are converted to lowercase - ensure your compNote keys match
2. **Trimming**: Extra spaces are trimmed - "High Elf Prince" matches "high elf prince"
3. **Check the example file**: See `examples/comp-notes-examples.js` for reference

## Advanced: Finding Your Print Function

If you're not sure where your print function is, search for:

```bash
# Search for print-related code
grep -r "print" src/
grep -r "Print" src/
grep -r ".print()" src/

# Search for dropdown menus
grep -r "dropdown" src/
grep -r "three-dot" src/
grep -r "menu" src/

# Search for army sheet generation
grep -r "army" src/
grep -r "unit-card" src/
grep -r "special-rules" src/
```

Look for files that might contain:
- `UnitCard` component
- `ArmyList` component
- `PrintView` component
- `exportToPDF` function
- `generateHTML` function

## Next Steps

Once you've integrated the basic functionality:

1. **Add comp notes** to all relevant units, weapons, and special rules
2. **Test with different army compositions** to ensure all notes display correctly
3. **Customize styling** if needed (edit `src/styles/comp-notes.css`)
4. **Consider adding** validation based on comp notes (future enhancement)

## Need Help?

If you're stuck, check:

1. `docs/COMP-NOTES.md` - Full feature documentation
2. `examples/comp-notes-examples.js` - Example implementations
3. `tests/comp-notes.test.js` - Test cases showing expected behavior

You can also run the tests to verify the core functionality works:

```javascript
import { runAllTests } from './tests/comp-notes.test.js';
runAllTests();
```
