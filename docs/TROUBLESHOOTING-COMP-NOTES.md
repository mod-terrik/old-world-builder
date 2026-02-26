# Troubleshooting Composition Notes

## Problem: Comp Notes Not Showing Up

If you've added a `compNote` to your rules but it's not appearing when you print, follow these debugging steps:

### Step 1: Check Your Rules Entry

Your rules entry should look like this in `rules-map.js`:

```javascript
const additionalOWBRules = {
  "griffon empire": {  // Key must be lowercase
    "url": "unit/griffon-empire",
    "compNote": "serrated maw +1AP",  // <-- This is what shows up
    "stats": [
      {
        "Name": "Griffon",
        "M": "6",
        "WS": "5",
        // ... other stats
      }
    ]
  }
};
```

**Important:** The key ("griffon empire") must be:
- All lowercase
- Match exactly how it appears in the unit data

### Step 2: Check Your Unit Data Structure

The comp-notes-handler looks for comp notes in these fields:
- `unit.name`
- `unit.mount`
- `unit.weapons[]`
- `unit.equipment[]`
- `unit.magicItems[]`
- `unit.specialRules[]`
- `unit.armor`
- `unit.options[]`

**Debug Question:** How is your griffon stored in the unit?

Open your browser console and add this debug code to Print.js temporarily:

```javascript
const getSection = ({ type }) => {
  const units = list[type];

  return (
    <>
      {units.map((unit) => {
        // ADD THIS DEBUG CODE:
        console.log('Unit data:', unit);
        console.log('Unit name:', unit.name);
        console.log('Unit mount:', unit.mount);
        console.log('Unit equipment:', unit.equipment);
        console.log('Unit options:', unit.options);
        
        const compNotes = showCompNotes ? getUnitCompNotes(unit, rulesMap) : [];
        console.log('Comp notes found:', compNotes);
        // END DEBUG CODE
```

### Step 3: Common Issues and Solutions

#### Issue 1: Mount Name Doesn't Match

**Problem:** Your unit has `mount: "Griffon"` but your rules entry is `"griffon empire"`

**Solution:** The keys must match exactly (after lowercase conversion).

If your unit data has:
```javascript
{
  name: "General of the Empire",
  mount: "Griffon"  // <-- Stored as "Griffon"
}
```

Your rules entry should be:
```javascript
"griffon": {  // Not "griffon empire"
  compNote: "serrated maw +1AP"
}
```

#### Issue 2: Mount is in Equipment Array

**Problem:** Your mount might be stored in `unit.equipment` as an object

```javascript
{
  name: "General of the Empire",
  equipment: [
    { name: "Griffon" }  // <-- Mount stored here
  ]
}
```

**Solution:** The comp-notes-handler will check `equipment[].name`, so your rules entry should be:
```javascript
"griffon": {
  compNote: "serrated maw +1AP"
}
```

#### Issue 3: Mount Has Army-Specific Name

**Problem:** Your mount is called "Griffon Empire" in the data

```javascript
{
  name: "General of the Empire",
  mount: "Griffon Empire"  // <-- Full name
}
```

**Solution:** Your rules entry should match:
```javascript
"griffon empire": {
  compNote: "serrated maw +1AP"
}
```

### Step 4: Test with Console

Add this temporary debug function to your Print.js:

```javascript
// Add at top of getSection function
const debugCompNotes = (unit) => {
  console.log('\n=== DEBUGGING COMP NOTES ===');
  console.log('Unit:', unit.name);
  
  // Check all possible fields
  const fieldsToCheck = [
    { field: 'name', value: unit.name },
    { field: 'mount', value: unit.mount },
    { field: 'weapons', value: unit.weapons },
    { field: 'equipment', value: unit.equipment },
    { field: 'magicItems', value: unit.magicItems },
    { field: 'specialRules', value: unit.specialRules },
    { field: 'armor', value: unit.armor },
    { field: 'options', value: unit.options }
  ];
  
  fieldsToCheck.forEach(({ field, value }) => {
    if (value) {
      console.log(`${field}:`, value);
      
      // Check if it's in rulesMap
      const normalized = (value?.name || value).toString().toLowerCase().trim();
      if (rulesMap[normalized]) {
        console.log(`  ✓ Found in rulesMap:`, rulesMap[normalized]);
        if (rulesMap[normalized].compNote) {
          console.log(`  ✓✓ HAS COMP NOTE:`, rulesMap[normalized].compNote);
        } else {
          console.log(`  ✗ No compNote field`);
        }
      } else {
        console.log(`  ✗ Not found in rulesMap (looking for "${normalized}")`);
      }
    }
  });
  
  const finalNotes = getUnitCompNotes(unit, rulesMap);
  console.log('Final comp notes:', finalNotes);
  console.log('===========================\n');
};

// Then call it:
const compNotes = showCompNotes ? getUnitCompNotes(unit, rulesMap) : [];
debugCompNotes(unit);  // <-- Add this line
```

### Step 5: Check Import Path

Make sure Print.js has these imports:

```javascript
import { getUnitCompNotes } from "../../utils/comp-notes-handler";
import { rulesMap } from "../../components/rules-index/rules-map";
import "../../styles/comp-notes.css";
```

Verify the files exist:
- `src/utils/comp-notes-handler.js` ✓
- `src/components/rules-index/rules-map.js` ✓
- `src/styles/comp-notes.css` ✓

### Step 6: Check rulesMap Export

In `rules-map.js`, verify you have this at the bottom:

```javascript
export const rulesMap = {
  ...rulesIndexExport,
  ...additionalOWBRules,  // Your griffon entry should be here
};
```

### Step 7: Verify Comp Notes Toggle

In the print page, there's a checkbox called "Show Comp Notes". Make sure it's checked!

### Quick Fix: Universal Griffon Entry

If you're not sure how the griffon is stored, add multiple entries:

```javascript
const additionalOWBRules = {
  // Try all possible variations
  "griffon": {
    url: "unit/griffon",
    compNote: "serrated maw +1AP"
  },
  "griffon empire": {
    url: "unit/griffon-empire",
    compNote: "serrated maw +1AP"
  },
  "empire griffon": {
    url: "unit/empire-griffon",
    compNote: "serrated maw +1AP"
  },
};
```

One of these should match!

## Example: Working Configuration

Here's a complete working example:

### In rules-map.js:
```javascript
const additionalOWBRules = {
  // ... other entries ...
  
  "griffon empire": {
    url: "unit/griffon-empire",
    compNote: "serrated maw +1AP",
    stats: [
      {
        "Name": "Griffon",
        "M": "6",
        "WS": "5",
        "BS": "-",
        "S": "5",
        "T": "(+1)",
        "W": "(+3)",
        "I": "5",
        "A": "4",
        "Ld": "-"
      }
    ]
  },
};

export const rulesMap = {
  ...rulesIndexExport,
  ...additionalOWBRules,
};
```

### Unit data structure:
```javascript
{
  id: "abc123",
  name: "General of the Empire",
  mount: "Griffon Empire",  // This matches "griffon empire" after normalization
  // ... other unit data
}
```

### Result when printing:
```
General of the Empire on Griffon

Special Rules
- Leadership
- Hold Your Ground

Comp Notes
serrated maw +1AP
```

## Still Not Working?

If you've tried everything above:

1. **Share your console output** from the debug code
2. **Check the browser console** for any errors
3. **Verify the file was saved** and the server reloaded
4. **Try a different unit** with a simpler name to test
5. **Clear your browser cache** and reload

## Test with a Simple Example

Create a test entry that you know will work:

```javascript
const additionalOWBRules = {
  // ... your other entries ...
  
  // TEST ENTRY - should work with any unit named "general of the empire"
  "general of the empire": {
    url: "unit/general-of-the-empire",
    compNote: "TEST: This is a test comp note!"
  },
};
```

If this shows up, then your integration is working, and the issue is just the mount name matching.
