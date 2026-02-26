# Composition Notes Feature

This feature allows you to add special composition ruleset notes to units, weapons, special rules, and equipment that will be displayed when printing army sheets.

## Overview

When users print their army sheets, any items (units, mounts, weapons, special rules, magic items, etc.) that have composition notes will display those notes in a "Comp Notes" section under the Special Rules for each unit.

## Adding Composition Notes

### In rules-index-export.json

Add a `compNote` field to any entry:

```json
{
  "murderous renegade": {
    "url": "special-rules/murderous-renegade",
    "page": "TRLP, p. 18",
    "compNote": "Renegade ruleset only"
  },
  "high elf prince": {
    "url": "unit/high-elf-prince",
    "page": "FoF, p. 156",
    "compNote": "Max 1 per 1000 points"
  },
  "griffon": {
    "url": "unit/griffon",
    "page": "FoF, p. 173",
    "compNote": "Counts as Rare choice"
  }
}
```

### In rules-map.js

Add a `compNote` field to entries in the `additionalOWBRules` object:

```javascript
const additionalOWBRules = {
  "saurus scar veteran": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/saurus-scar-veteran.html?minimal=true",
    compNote: "Max 2 per army",
    stats: [
      { Name: "Saurus Scar-Veteran", M: "4", WS: "5", BS: "0", S: "5", T: "5", W: "2", I: "3", A: "4", Ld: "8" }
    ]
  },
  "sword of might": {
    url: "magic-items/sword-of-might",
    compNote: "No duplicate magic items allowed"
  }
};
```

## Usage in Code

### Import the functions

```javascript
import { 
  addCompNotesToPrint, 
  getUnitCompNotes, 
  getArmyCompNotes,
  getAllArmyCompNotes 
} from '../utils/comp-notes-handler';
import { rulesMap } from '../components/rules-index/rules-map';
```

### Add comp notes to a single unit

```javascript
// In your print/render function for a unit:
function renderUnitForPrint(unit) {
  let html = `
    <div class="unit-card">
      <h3>${unit.name}</h3>
      
      <!-- Unit stats and other info -->
      
      <!-- Special Rules Section -->
      <div class="special-rules">
        <h4>Special Rules</h4>
        ${renderSpecialRules(unit)}
        
        <!-- Add Comp Notes here -->
        ${addCompNotesToPrint(unit, rulesMap)}
      </div>
    </div>
  `;
  
  return html;
}
```

### Get comp notes for entire army

```javascript
// Get a map of all units with their comp notes
const armyCompNotes = getArmyCompNotes(armyList, rulesMap);

// Access notes for a specific unit
if (armyCompNotes[unit.id]) {
  console.log(armyCompNotes[unit.id].compNotes); // Array of note strings
  console.log(armyCompNotes[unit.id].html);      // Pre-formatted HTML
}
```

### Get all unique comp notes in army

```javascript
// Useful for displaying a summary at the top of the army sheet
const allNotes = getAllArmyCompNotes(armyList, rulesMap);
console.log('All composition restrictions:', allNotes);
```

## Example Output

For a High Elf Prince with a Griffon mount and Sword of Might:

```
Special Rules
- Martial Prowess
- Valour of Ages
- Always Strikes First

Comp Notes
Max 1 per 1000 points, Counts as Rare choice, No duplicate magic items allowed
```

## What Gets Checked

The comp notes handler automatically checks the following fields on a unit:

- `unit.name` - The unit's name
- `unit.mount` - Any mount the unit has
- `unit.specialRules` - Array of special rules
- `unit.weapons` - Array of weapons
- `unit.equipment` - Array of equipment items
- `unit.magicItems` - Array of magic items
- `unit.armor` - Armor (can be string or array)
- `unit.options` - Any additional options

## Styling

The CSS is located in `src/styles/comp-notes.css` and includes:

- Default styling with blue accent
- Print-specific styles
- Dark mode support
- Mobile responsive layout
- Optional `.compact` class for tighter spacing
- Optional `.warning` class for yellow/orange accent (important notes)
- Optional `.error` class for red accent (restricted items)

### Using Alternative Styles

To use warning or error styling, modify the `generateCompNotesHTML` function:

```javascript
export function generateCompNotesHTML(compNotes, style = '') {
  if (!compNotes || compNotes.length === 0) {
    return '';
  }
  
  const notesText = compNotes.join(', ');
  const className = style ? `comp-notes-section ${style}` : 'comp-notes-section';
  
  return `
    <div class="${className}">
      <h4>Comp Notes</h4>
      <p>${notesText}</p>
    </div>
  `;
}

// Usage:
addCompNotesToPrint(unit, rulesMap, 'warning'); // Yellow styling
addCompNotesToPrint(unit, rulesMap, 'error');   // Red styling
```

## Example Composition Notes

Here are some examples of useful composition notes:

### Unit Limits
- "Max 1 per army"
- "Max 2 per 1000 points"
- "Limited to 0-1 per army"
- "Requires General to be [faction] character"

### Special Restrictions
- "Cannot be taken with [unit name]"
- "Requires [special rule/ability]"
- "Counts as Lord choice instead of Hero"
- "Occupies 2 Rare slots"

### Ruleset Specific
- "Renegade ruleset only"
- "Combined Arms composition"
- "Grand Melee restricted"
- "Open War - unrestricted"

### Equipment Notes
- "No duplicate magic items allowed"
- "One use only per battle"
- "Cannot be combined with [other item]"
- "Replaces standard equipment"

## Integration Checklist

- [ ] Import CSS file in your main stylesheet or component
- [ ] Import comp-notes-handler functions where needed
- [ ] Add compNote fields to relevant entries in rules-map.js
- [ ] Add compNote fields to relevant entries in rules-index-export.json
- [ ] Integrate `addCompNotesToPrint` into your print functionality
- [ ] Test with various unit combinations
- [ ] Verify print styling looks correct

## Future Enhancements

Possible additions to this feature:

1. **Validation**: Check comp notes against actual army composition and highlight violations
2. **Categories**: Group comp notes by type (limits, restrictions, special rules)
3. **Tooltips**: Show comp notes in the unit builder UI, not just on print
4. **Export**: Include comp notes in exported army lists (JSON, text format)
5. **Templates**: Pre-defined comp note templates for common restrictions

## Support

If you encounter issues or have questions about the comp notes feature, please check:

1. Ensure the CSS file is properly imported
2. Verify rulesMap is being passed correctly to the functions
3. Check browser console for any JavaScript errors
4. Confirm unit structure matches the expected format
