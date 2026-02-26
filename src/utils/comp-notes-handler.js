/**
 * Composition Notes Handler
 * Collects and formats composition notes for army sheet printing
 */

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
    
    const normalizedName = ruleName.toLowerCase().trim();
    const ruleEntry = rulesMap[normalizedName];
    
    if (ruleEntry && ruleEntry.compNote) {
      compNotes.add(ruleEntry.compNote);
    }
  };
  
  // Check the unit itself
  if (unit.name) {
    addCompNote(unit.name);
  }
  
  // Check mount if present
  if (unit.mount) {
    addCompNote(unit.mount);
  }
  
  // Check special rules
  if (unit.specialRules && Array.isArray(unit.specialRules)) {
    unit.specialRules.forEach(rule => {
      if (typeof rule === 'string') {
        addCompNote(rule);
      } else if (rule.name) {
        addCompNote(rule.name);
      }
    });
  }
  
  // Check weapons
  if (unit.weapons && Array.isArray(unit.weapons)) {
    unit.weapons.forEach(weapon => {
      if (typeof weapon === 'string') {
        addCompNote(weapon);
      } else if (weapon.name) {
        addCompNote(weapon.name);
      }
    });
  }
  
  // Check equipment
  if (unit.equipment && Array.isArray(unit.equipment)) {
    unit.equipment.forEach(item => {
      if (typeof item === 'string') {
        addCompNote(item);
      } else if (item.name) {
        addCompNote(item.name);
      }
    });
  }
  
  // Check magic items
  if (unit.magicItems && Array.isArray(unit.magicItems)) {
    unit.magicItems.forEach(item => {
      if (typeof item === 'string') {
        addCompNote(item);
      } else if (item.name) {
        addCompNote(item.name);
      }
    });
  }
  
  // Check armor
  if (unit.armor) {
    if (typeof unit.armor === 'string') {
      addCompNote(unit.armor);
    } else if (Array.isArray(unit.armor)) {
      unit.armor.forEach(armor => {
        if (typeof armor === 'string') {
          addCompNote(armor);
        } else if (armor.name) {
          addCompNote(armor.name);
        }
      });
    }
  }
  
  // Check options (if your units have an options field)
  if (unit.options && Array.isArray(unit.options)) {
    unit.options.forEach(option => {
      if (typeof option === 'string') {
        addCompNote(option);
      } else if (option.name) {
        addCompNote(option.name);
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
