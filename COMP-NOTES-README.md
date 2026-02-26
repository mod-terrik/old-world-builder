# Composition Notes Feature

✨ **Add special composition ruleset notes to your army sheets that display when printing!**

## What It Does

When users print their army sheets, any units, mounts, weapons, special rules, or equipment that have composition notes will automatically display those notes in a dedicated "Comp Notes" section under the Special Rules for each unit.

### Example

If a player creates a High Elf Prince with a Griffon mount and Sword of Might:

```
High Elf Prince on Griffon

Special Rules
- Martial Prowess
- Valour of Ages
- Always Strikes First

Comp Notes
Max 1 per 1000 points, Counts as Rare choice, No duplicate magic items
```

## Quick Start

### 1. The code is already in your repo! ✅

I've added all necessary files:
- `src/utils/comp-notes-handler.js` - Core functionality
- `src/styles/comp-notes.css` - Styling
- Complete documentation and examples

### 2. Import and use in your print function:

```javascript
import { addCompNotesToPrint } from './utils/comp-notes-handler';
import { rulesMap } from './components/rules-index/rules-map';
import './styles/comp-notes.css';

// In your unit printing code:
const compNotesHTML = addCompNotesToPrint(unit, rulesMap);
// Add this after the Special Rules section
```

### 3. Add comp notes to your rules files:

```javascript
// In rules-map.js or rules-index-export.json:
{
  "high elf prince": {
    "url": "unit/high-elf-prince",
    "compNote": "Max 1 per 1000 points"  // ← Add this field
  }
}
```

## Files Added to Your Repository

| File | Purpose |
|------|--------|
| **Core Functionality** |
| `src/utils/comp-notes-handler.js` | Main JavaScript functions |
| `src/styles/comp-notes.css` | Styling for comp notes display |
| **Documentation** |
| `docs/COMP-NOTES.md` | Complete feature documentation |
| `docs/INTEGRATION-GUIDE.md` | Step-by-step integration instructions |
| `docs/QUICK-REFERENCE.md` | Quick reference cheat sheet |
| **Examples & Tests** |
| `examples/comp-notes-examples.js` | Example implementations |
| `tests/comp-notes.test.js` | Test suite |
| **This File** |
| `COMP-NOTES-README.md` | Overview and navigation |

## Features

✅ **Automatic Collection** - Scans all unit components (mount, weapons, equipment, etc.)  
✅ **Smart Deduplication** - Only shows each unique note once  
✅ **Easy Integration** - Single function call in your print code  
✅ **Flexible Data Structure** - Works with strings, objects, or arrays  
✅ **Print Optimized** - Includes print-specific CSS styling  
✅ **Dark Mode Support** - Automatically adapts to dark themes  
✅ **Mobile Responsive** - Works on all screen sizes  
✅ **Fully Tested** - Complete test suite included  
✅ **Well Documented** - Extensive docs and examples  

## Documentation Navigation

### 🚀 Getting Started
Start here if this is your first time:
1. Read **[QUICK-REFERENCE.md](./docs/QUICK-REFERENCE.md)** - Fast overview
2. Read **[INTEGRATION-GUIDE.md](./docs/INTEGRATION-GUIDE.md)** - Connect to your code
3. Check **[examples/comp-notes-examples.js](./examples/comp-notes-examples.js)** - See examples

### 📚 Complete Reference
For full details:
- **[COMP-NOTES.md](./docs/COMP-NOTES.md)** - Complete feature documentation

### 🛠️ Testing
To verify functionality:
- **[tests/comp-notes.test.js](./tests/comp-notes.test.js)** - Run the test suite

## How It Works

1. **Data Storage**: Add optional `compNote` field to any entry in your rules files
2. **Collection**: Function walks through all unit components looking for comp notes
3. **Processing**: Deduplicates and formats notes into comma-separated list
4. **Display**: Renders as HTML section below Special Rules

```
Unit Definition              Comp Notes Function           Display
│                                │                             │
├─ name: "Prince"                 │                             │
│  compNote: "Max 1"          ───► Collection           ───► "Comp Notes"
│                                │                             "Max 1, Rare choice,
├─ mount: "Griffon"                │                             No duplicates"
│  compNote: "Rare choice"    ───► Deduplication
│                                │
├─ weapon: "Sword"                 │
   compNote: "No duplicates" ───► Formatting
```

## Integration Steps

### Step 1: Import CSS

In your main app or print component:

```javascript
import './styles/comp-notes.css';
```

### Step 2: Import Functions

Where you handle printing:

```javascript
import { addCompNotesToPrint } from './utils/comp-notes-handler';
import { rulesMap } from './components/rules-index/rules-map';
```

### Step 3: Integrate into Print Function

Add to your unit rendering:

```javascript
function renderUnitForPrint(unit) {
  return `
    <div class="unit-card">
      <h3>${unit.name}</h3>
      
      <div class="special-rules">
        <h4>Special Rules</h4>
        ${renderSpecialRules(unit)}
        
        <!-- ADD THIS LINE -->
        ${addCompNotesToPrint(unit, rulesMap)}
      </div>
    </div>
  `;
}
```

### Step 4: Add Comp Notes to Rules

In `rules-map.js` or `rules-index-export.json`:

```javascript
{
  "high elf prince": {
    "url": "unit/high-elf-prince",
    "compNote": "Max 1 per 1000 points"
  },
  "griffon": {
    "url": "unit/griffon",
    "compNote": "Counts as Rare choice"
  }
}
```

## Common Use Cases

### Army Composition Limits
```javascript
compNote: "Max 1 per army"
compNote: "0-1 per 1000 points"
compNote: "Max 2 per 1500 points"
```

### Slot Restrictions
```javascript
compNote: "Counts as Rare choice"
compNote: "Occupies 2 Rare slots"
compNote: "Does not count toward Core minimum"
```

### Ruleset Specific
```javascript
compNote: "Renegade ruleset only"
compNote: "Combined Arms composition"
compNote: "Grand Melee restricted"
```

### Equipment Limitations
```javascript
compNote: "No duplicate magic items"
compNote: "One per army"
compNote: "Cannot combine with [item]"
```

## Testing Your Implementation

1. **Add a test note**:
   ```javascript
   { "test-unit": { "compNote": "TEST NOTE" } }
   ```

2. **Create an army** with that unit

3. **Click Print** from the three-dot dropdown

4. **Verify** "TEST NOTE" appears under Comp Notes

5. **Run test suite** (optional):
   ```javascript
   import { runAllTests } from './tests/comp-notes.test.js';
   runAllTests();
   ```

## Next Steps

Once basic integration is complete:

1. ✅ Add `compNote` fields to relevant entries in your rules files
2. ✅ Test with various army compositions
3. ✅ Customize styling if desired (edit `src/styles/comp-notes.css`)
4. ✅ Consider adding validation logic based on comp notes
5. ✅ Add tooltips in unit builder UI (future enhancement)

## Support & Troubleshooting

**Comp notes not showing?**
- Check CSS is imported
- Verify function is called with correct parameters
- Check browser console for errors
- See [INTEGRATION-GUIDE.md](./docs/INTEGRATION-GUIDE.md) troubleshooting section

**Need examples?**
- See [examples/comp-notes-examples.js](./examples/comp-notes-examples.js)

**Want to customize?**
- Edit [src/styles/comp-notes.css](./src/styles/comp-notes.css) for styling
- Edit [src/utils/comp-notes-handler.js](./src/utils/comp-notes-handler.js) for behavior

## Credits

Composition Notes feature for Old World Builder  
Implemented: February 26, 2026

---

**Ready to get started?** Head to the [Quick Reference](./docs/QUICK-REFERENCE.md) or [Integration Guide](./docs/INTEGRATION-GUIDE.md)!
