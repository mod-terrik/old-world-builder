/**
 * Composition Notes Handler
 * Collects and formats composition notes for army sheet printing
 */

/**
 * Extracts name from an item that might have multi-language properties
 * @param {*} item - Item that could be string, or object with name/name_en/name_cn etc.
 * @returns {string|null} - The extracted name or null
 */
function extractName(item) {
  if (!item) return null;
  
  // If it's a string, return it
  if (typeof item === 'string') {
    return item;
  }
  
  // If it's an object, try various name properties
  if (typeof item === 'object') {
    // Try multi-language names (your app uses this structure)
    if (item.name_en) return item.name_en;
    if (item.name_cn) return item.name_cn;
    if (item.name_de) return item.name_de;
    if (item.name_es) return item.name_es;
    if (item.name_fr) return item.name_fr;
    if (item.name_it) return item.name_it;
    
    // Try regular name property
    if (item.name) return item.name;
  }
  
  return null;
}

/**
 * Collects composition notes from a unit and all its equipment/special rules
 * @param {Object} unit - The unit object with selected equipment and rules
 * @param {Object} rulesMap - The rules mapping object
 * @returns {Array<string>} - Array of unique comp notes
 */
export function getUnitCompNotes(unit, rulesMap) {
  const compNotes = new Set();
  
  // Helper function to add comp note from a rule entry
  const addCompNote = (ruleName) => {
    if (!ruleName) return;
    
    const normalizedName = ruleName.toLowerCase().trim().replace(/[{}]/g, '');    
    const ruleEntry = rulesMap[normalizedName];
    
    if (ruleEntry && ruleEntry.compNote) {
      compNotes.add(ruleEntry.compNote);
    }
  };
  
  // Check the unit itself by all possible name fields
  const unitName = extractName(unit);
  if (unitName) {
    addCompNote(unitName);
  }
  
  // Check mount if present
  if (unit.mount) {
    const mountName = extractName(unit.mount);
    if (mountName) {
      addCompNote(mountName);
    }
  }
  
  // Check special rules
  // Check special rules
if (unit.specialRules) {
  if (Array.isArray(unit.specialRules)) {
    unit.specialRules.forEach(rule => {
      const ruleName = extractName(rule);
      if (ruleName) {
        // Split by comma and check each rule separately
        const rules = ruleName.split(',').map(r => r.trim());
        rules.forEach(r => addCompNote(r));
      }
    });
  } else {
    // specialRules might be a single object with comma-separated names
    const ruleName = extractName(unit.specialRules);
    if (ruleName) {
      // Split by comma and check each rule separately
      const rules = ruleName.split(',').map(r => r.trim());
      rules.forEach(r => addCompNote(r));
    }
  }
}

  
  // Check weapons
  if (unit.weapons && Array.isArray(unit.weapons)) {
    unit.weapons.forEach(weapon => {
      const weaponName = extractName(weapon);
      if (weaponName) addCompNote(weaponName);
    });
  }
  // Check equipment
  if (unit.equipment) {
    unit.equipment.forEach((item) => {
    if (!item.active) return;
    const itemName = item.name_en?.replace(/[{}]/g, '') || '';
    // Split by comma to handle multiple items on one line
    const items = itemName.split(',').map(i => i.toLowerCase().trim());
    items.forEach(normalized => {
      if (normalized && rulesMap[normalized]?.compNote) {
        compNotes.add(rulesMap[normalized].compNote);
      }
    });
  });
}
  
  // Check magic items
  if (unit.magicItems && Array.isArray(unit.magicItems)) {
    unit.magicItems.forEach(item => {
      const itemName = extractName(item);
      if (itemName) addCompNote(itemName);
    });
  }

 if (unit.items && Array.isArray(unit.items)) {
  unit.items.forEach(itemCategory => {
    if (itemCategory.selected && Array.isArray(itemCategory.selected)) {
      itemCategory.selected.forEach(item => {
        const itemName = extractName(item);
        if (itemName) addCompNote(itemName);
      });
    }
  });
} 
  
  // Check armor
  if (unit.armor) {
    if (Array.isArray(unit.armor)) {
      unit.armor.forEach(armor => {
        const armorName = extractName(armor);
        if (armorName) addCompNote(armorName);
      });
    } else {
      const armorName = extractName(unit.armor);
      if (armorName) addCompNote(armorName);
    }
  }
  
  // Check options (if your units have an options field)
  if (unit.options && Array.isArray(unit.options)) {
    unit.options.forEach(option => {
      const optionName = extractName(option);
      if (optionName) addCompNote(optionName);
    });
  }
  
  // Check mounts array (some units might have mounts in an array)
   if (unit.mounts) {
    unit.mounts.forEach((mount) => {
      if (!mount.active) return;
      const normalized = mount.name_en?.toLowerCase().trim().replace(/[{}]/g, '');
      if (rulesMap[normalized]?.compNote) {
        compNotes.add(rulesMap[normalized].compNote);
      }
    });
  }
  // Check command items (champions, musicians, standard bearers, etc.)
  if (unit.command && Array.isArray(unit.command)) {
    unit.command.forEach((commandItem) => {
      if (!commandItem.active) return;
      const commandName = extractName(commandItem);
      if (commandName) {
      // Split by comma in case there are multiple items
      const items = commandName.split(',').map(i => i.trim());
      items.forEach(item => addCompNote(item));
    }
  });
}
  // Check command magic items (banners, etc.)
  if (unit.command && Array.isArray(unit.command)) {
  unit.command.forEach((commandItem) => {
    if (!commandItem.active) return;
    
    // Check magic items selected within command (e.g., banners on standard bearers)
    if (commandItem.magic && commandItem.magic.selected && Array.isArray(commandItem.magic.selected)) {
      commandItem.magic.selected.forEach(magicItem => {
        const itemName = extractName(magicItem);
        if (itemName) addCompNote(itemName);
      });
    }
  });
}

  return Array.from(compNotes);
}

/**
 * Generates HTML for the Comp Notes section
 * @param {Array<string>} compNotes - Array of composition notes
 * @returns {string} - HTML string for comp notes section
 */
export function generateCompNotesHTML(compNotes) {
  if (!compNotes || compNotes.length === 0) {
    return '';
  }
  
  const notesText = compNotes.join(', ');
  
  return `
    <div class="comp-notes-section">
      <h4>Comp Notes</h4>
      <p>${notesText}</p>
    </div>
  `;
}

/**
 * Main function to add comp notes to unit printing
 * Integrates with your existing print functionality
 * @param {Object} unit - The unit being printed
 * @param {Object} rulesMap - The rules mapping object
 * @returns {string} - HTML to append after Special Rules section
 */
export function addCompNotesToPrint(unit, rulesMap) {
  const compNotes = getUnitCompNotes(unit, rulesMap);
  return generateCompNotesHTML(compNotes);
}

/**
 * Batch process multiple units for army sheet printing
 * @param {Array<Object>} army - Array of all units in the army
 * @param {Object} rulesMap - The rules mapping object
 * @returns {Object} - Map of unit IDs to their comp notes HTML
 */
export function getArmyCompNotes(army, rulesMap) {
  const result = {};
  
  if (!Array.isArray(army)) {
    return result;
  }
  
  army.forEach((unit, index) => {
    const compNotes = getUnitCompNotes(unit, rulesMap);
    if (compNotes.length > 0) {
      result[unit.id || index] = {
        compNotes: compNotes,
        html: generateCompNotesHTML(compNotes)
      };
    }
  });
  
  return result;
}

/**
 * Get all unique comp notes from an entire army (for summary display)
 * @param {Array<Object>} army - Array of all units in the army
 * @param {Object} rulesMap - The rules mapping object
 * @returns {Array<string>} - Array of all unique comp notes in the army
 */
export function getAllArmyCompNotes(army, rulesMap) {
  const allNotes = new Set();
  
  if (!Array.isArray(army)) {
    return [];
  }
  
  army.forEach(unit => {
    const unitNotes = getUnitCompNotes(unit, rulesMap);
    unitNotes.forEach(note => allNotes.add(note));
  });
  
  return Array.from(allNotes).sort();
}
