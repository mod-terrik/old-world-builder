# Composition Notes - Quick Reference

A quick cheat sheet for using the composition notes feature.

## Quick Start (3 Steps)

### 1. Add comp notes to your rules:

```javascript
// In rules-map.js or rules-index-export.json
{
  "unit-name": {
    "url": "unit/unit-name",
    "compNote": "Your note here"  // <-- Add this
  }
}
```

### 2. Import in your print file:

```javascript
import { addCompNotesToPrint } from '../utils/comp-notes-handler';
import { rulesMap } from '../components/rules-index/rules-map';
import '../styles/comp-notes.css';
```

### 3. Add to your unit render:

```javascript
// After Special Rules section:
${addCompNotesToPrint(unit, rulesMap)}
```

## Common Comp Note Examples

```javascript
// Quantity limits
compNote: "Max 1 per army"
compNote: "0-1 per army"
compNote: "Max 2 per 1000 points"

// Slot restrictions
compNote: "Counts as Rare choice"
compNote: "Occupies 2 Rare slots"
compNote: "Does not count toward Core minimum"

// Requirements
compNote: "Requires [unit] to be in army"
compNote: "General must be [faction]"

// Ruleset specific
compNote: "Renegade ruleset only"
compNote: "Combined Arms composition"
compNote: "Grand Melee restricted"

// Equipment
compNote: "No duplicate magic items"
compNote: "One per army"
compNote: "Dwarfs only"
```

## File Locations

| File | Purpose |
|------|--------|
| `src/utils/comp-notes-handler.js` | Core functionality |
| `src/styles/comp-notes.css` | Styling |
| `src/components/rules-index/rules-map.js` | Add comp notes here |
| `src/components/rules-index/rules-index-export.json` | Or add comp notes here |
| `docs/COMP-NOTES.md` | Full documentation |
| `docs/INTEGRATION-GUIDE.md` | Integration help |
| `examples/comp-notes-examples.js` | Usage examples |
| `tests/comp-notes.test.js` | Test suite |

## Function Reference

### `addCompNotesToPrint(unit, rulesMap)`
Main function - returns HTML string to add after Special Rules

```javascript
const html = addCompNotesToPrint(unit, rulesMap);
// Returns: '<div class="comp-notes-section">...</div>' or ''
```

### `getUnitCompNotes(unit, rulesMap)`
Get array of comp notes for a unit

```javascript
const notes = getUnitCompNotes(unit, rulesMap);
// Returns: ["Max 1 per army", "No duplicates"]
```

### `getArmyCompNotes(army, rulesMap)`
Get comp notes for all units in army

```javascript
const armyNotes = getArmyCompNotes(armyList, rulesMap);
// Returns: { unitId: { compNotes: [...], html: '...' } }
```

### `getAllArmyCompNotes(army, rulesMap)`
Get all unique comp notes in entire army

```javascript
const allNotes = getAllArmyCompNotes(armyList, rulesMap);
// Returns: ["Max 1 per army", "Rare choice", ...]
```

## What Gets Checked

The system automatically checks these unit fields for comp notes:

- ✅ `unit.name`
- ✅ `unit.mount`
- ✅ `unit.specialRules[]`
- ✅ `unit.weapons[]`
- ✅ `unit.equipment[]`
- ✅ `unit.magicItems[]`
- ✅ `unit.armor`
- ✅ `unit.options[]`

## CSS Classes

```css
.comp-notes-section          /* Default blue styling */
.comp-notes-section.compact  /* Tighter spacing */
.comp-notes-section.warning  /* Yellow/orange for warnings */
.comp-notes-section.error    /* Red for restrictions */
```

## Testing

```javascript
// Run all tests
import { runAllTests } from './tests/comp-notes.test.js';
runAllTests();
```

## Troubleshooting Checklist

- [ ] CSS file imported?
- [ ] Functions imported correctly?
- [ ] rulesMap passed to function?
- [ ] compNote field added to rules?
- [ ] Unit structure matches expected format?
- [ ] Check browser console for errors
- [ ] Test with simple example first

## Example Integration

```javascript
// Complete minimal example
import { addCompNotesToPrint } from './utils/comp-notes-handler';
import { rulesMap } from './components/rules-index/rules-map';
import './styles/comp-notes.css';

function printUnit(unit) {
  const html = `
    <div class="unit-card">
      <h3>${unit.name}</h3>
      
      <div class="special-rules">
        <h4>Special Rules</h4>
        <ul>
          ${unit.specialRules.map(r => `<li>${r}</li>`).join('')}
        </ul>
        
        ${addCompNotesToPrint(unit, rulesMap)}
      </div>
    </div>
  `;
  
  document.getElementById('print-area').innerHTML = html;
  window.print();
}
```

## Before/After Example

### Before:
```
High Elf Prince

Special Rules
- Martial Prowess
- Valour of Ages
```

### After:
```
High Elf Prince on Griffon

Special Rules
- Martial Prowess
- Valour of Ages

Comp Notes
Max 1 per 1000 points, Counts as Rare choice
```

## Tips

- Keep comp notes **short and clear**
- Use **consistent phrasing** across similar restrictions
- Notes are **comma-separated** automatically
- Notes are **deduplicated** automatically
- Case is **normalized** ("High Elf" → "high elf")
- Works with **strings or objects** in arrays

## Need More Help?

See the full documentation:
- [Full Feature Docs](./COMP-NOTES.md)
- [Integration Guide](./INTEGRATION-GUIDE.md)
- [Examples](../examples/comp-notes-examples.js)
