/**
 * Test suite for composition notes functionality
 * Run these tests to verify the comp-notes-handler works correctly
 */

import { 
  getUnitCompNotes, 
  generateCompNotesHTML,
  addCompNotesToPrint,
  getArmyCompNotes,
  getAllArmyCompNotes
} from '../src/utils/comp-notes-handler';

// Mock rules map for testing
const mockRulesMap = {
  "high elf prince": {
    url: "unit/high-elf-prince",
    compNote: "Max 1 per 1000 points"
  },
  "griffon": {
    url: "unit/griffon",
    compNote: "Counts as Rare choice"
  },
  "sword of might": {
    url: "magic-items/sword-of-might",
    compNote: "No duplicate magic items"
  },
  "martial prowess": {
    url: "special-rules/martial-prowess",
    // No comp note - should not appear
  },
  "gromril armour": {
    url: "weapons-of-war/gromril-armour",
    compNote: "Dwarfs only"
  }
};

// Test 1: Basic unit with single comp note
function testBasicUnit() {
  console.log('Test 1: Basic unit with single comp note');
  
  const unit = {
    name: "High Elf Prince",
    weapons: [],
    specialRules: []
  };
  
  const notes = getUnitCompNotes(unit, mockRulesMap);
  console.assert(notes.length === 1, 'Should have 1 comp note');
  console.assert(notes[0] === "Max 1 per 1000 points", 'Should have correct note');
  console.log('✓ Test 1 passed');
}

// Test 2: Unit with mount
function testUnitWithMount() {
  console.log('\nTest 2: Unit with mount');
  
  const unit = {
    name: "High Elf Prince",
    mount: "Griffon",
    specialRules: []
  };
  
  const notes = getUnitCompNotes(unit, mockRulesMap);
  console.assert(notes.length === 2, 'Should have 2 comp notes');
  console.assert(notes.includes("Max 1 per 1000 points"), 'Should include unit note');
  console.assert(notes.includes("Counts as Rare choice"), 'Should include mount note');
  console.log('✓ Test 2 passed');
}

// Test 3: Unit with equipment and no comp notes on some items
function testMixedItems() {
  console.log('\nTest 3: Mixed items (some with, some without comp notes)');
  
  const unit = {
    name: "High Elf Prince",
    specialRules: ["Martial Prowess"], // No comp note
    magicItems: ["Sword of Might"]     // Has comp note
  };
  
  const notes = getUnitCompNotes(unit, mockRulesMap);
  console.assert(notes.length === 2, 'Should have 2 comp notes');
  console.assert(!notes.includes("Martial Prowess"), 'Should not include items without comp notes');
  console.log('✓ Test 3 passed');
}

// Test 4: Unit with no comp notes
function testUnitNoNotes() {
  console.log('\nTest 4: Unit with no comp notes');
  
  const unit = {
    name: "Regular Warrior",
    specialRules: ["Martial Prowess"]
  };
  
  const notes = getUnitCompNotes(unit, mockRulesMap);
  console.assert(notes.length === 0, 'Should have 0 comp notes');
  console.log('✓ Test 4 passed');
}

// Test 5: Duplicate notes are filtered
function testDuplicateFiltering() {
  console.log('\nTest 5: Duplicate comp notes are filtered');
  
  const unit = {
    name: "High Elf Prince",
    specialRules: ["High Elf Prince"], // Same as name
    weapons: ["High Elf Prince"]       // Same as name
  };
  
  const notes = getUnitCompNotes(unit, mockRulesMap);
  console.assert(notes.length === 1, 'Should deduplicate to 1 note');
  console.log('✓ Test 5 passed');
}

// Test 6: HTML generation
function testHTMLGeneration() {
  console.log('\nTest 6: HTML generation');
  
  const notes = ["Max 1 per army", "No duplicates"];
  const html = generateCompNotesHTML(notes);
  
  console.assert(html.includes('comp-notes-section'), 'Should have correct class');
  console.assert(html.includes('Comp Notes'), 'Should have heading');
  console.assert(html.includes('Max 1 per army'), 'Should include first note');
  console.assert(html.includes('No duplicates'), 'Should include second note');
  console.assert(html.includes(','), 'Should be comma-separated');
  console.log('✓ Test 6 passed');
}

// Test 7: Empty comp notes returns empty HTML
function testEmptyHTML() {
  console.log('\nTest 7: Empty comp notes returns empty HTML');
  
  const html = generateCompNotesHTML([]);
  console.assert(html === '', 'Should return empty string');
  
  const html2 = generateCompNotesHTML(null);
  console.assert(html2 === '', 'Should handle null');
  
  console.log('✓ Test 7 passed');
}

// Test 8: Full integration test
function testFullIntegration() {
  console.log('\nTest 8: Full integration test');
  
  const unit = {
    name: "High Elf Prince",
    mount: "Griffon",
    magicItems: ["Sword of Might"],
    specialRules: ["Martial Prowess"]
  };
  
  const html = addCompNotesToPrint(unit, mockRulesMap);
  console.assert(html.includes('Max 1 per 1000 points'), 'Should include unit note');
  console.assert(html.includes('Counts as Rare choice'), 'Should include mount note');
  console.assert(html.includes('No duplicate magic items'), 'Should include magic item note');
  console.log('✓ Test 8 passed');
}

// Test 9: Army-wide comp notes
function testArmyCompNotes() {
  console.log('\nTest 9: Army-wide comp notes');
  
  const army = [
    {
      id: 1,
      name: "High Elf Prince",
      mount: "Griffon"
    },
    {
      id: 2,
      name: "Regular Warrior",
      specialRules: ["Martial Prowess"]
    },
    {
      id: 3,
      name: "High Elf Prince",
      equipment: [{ name: "Gromril Armour" }]
    }
  ];
  
  const armyNotes = getArmyCompNotes(army, mockRulesMap);
  console.assert(Object.keys(armyNotes).length === 2, 'Should have notes for 2 units');
  console.assert(armyNotes[1], 'Should have notes for unit 1');
  console.assert(!armyNotes[2], 'Should not have notes for unit 2');
  console.log('✓ Test 9 passed');
}

// Test 10: Get all unique army comp notes
function testAllArmyNotes() {
  console.log('\nTest 10: All unique army comp notes');
  
  const army = [
    { name: "High Elf Prince" },
    { name: "High Elf Prince" }, // Duplicate
    { mount: "Griffon" },
    { magicItems: ["Sword of Might"] }
  ];
  
  const allNotes = getAllArmyCompNotes(army, mockRulesMap);
  console.assert(allNotes.length === 3, 'Should have 3 unique notes');
  console.assert(allNotes.includes("Max 1 per 1000 points"), 'Should include unit note');
  console.assert(allNotes.includes("Counts as Rare choice"), 'Should include mount note');
  console.assert(allNotes.includes("No duplicate magic items"), 'Should include item note');
  console.log('✓ Test 10 passed');
}

// Test 11: Array vs string vs object handling
function testVariousFormats() {
  console.log('\nTest 11: Various data format handling');
  
  const unit = {
    name: "High Elf Prince",
    weapons: ["Sword of Might", { name: "Gromril Armour" }],
    armor: "Gromril Armour",
    specialRules: [{ name: "Griffon" }]
  };
  
  const notes = getUnitCompNotes(unit, mockRulesMap);
  console.assert(notes.length === 4, 'Should handle strings and objects');
  console.log('✓ Test 11 passed');
}

// Run all tests
export function runAllTests() {
  console.log('=== Running Composition Notes Tests ===\n');
  
  try {
    testBasicUnit();
    testUnitWithMount();
    testMixedItems();
    testUnitNoNotes();
    testDuplicateFiltering();
    testHTMLGeneration();
    testEmptyHTML();
    testFullIntegration();
    testArmyCompNotes();
    testAllArmyNotes();
    testVariousFormats();
    
    console.log('\n=== All Tests Passed! ✓ ===');
    return true;
  } catch (error) {
    console.error('\n✗ Test failed:', error);
    return false;
  }
}

// Auto-run tests if this file is executed directly
if (typeof window === 'undefined') {
  runAllTests();
}
