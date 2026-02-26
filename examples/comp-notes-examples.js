/**
 * Example Composition Notes
 * 
 * This file shows examples of how to add compNote fields to your rules.
 * Copy these patterns into rules-map.js or rules-index-export.json
 */

// Example entries for rules-map.js
const exampleRulesMapEntries = {
  // Units with limits
  "high elf prince": {
    url: "unit/high-elf-prince",
    compNote: "Max 1 per 1000 points",
    stats: [
      { Name: "High Elf Prince", M: "5", WS: "7", BS: "6", S: "4", T: "3", W: "3", I: "7", A: "4", Ld: "10" }
    ]
  },

  "saurus scar veteran": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/saurus-scar-veteran.html?minimal=true",
    compNote: "Max 2 per army",
    stats: [
      { Name: "Saurus Scar-Veteran", M: "4", WS: "5", BS: "0", S: "5", T: "5", W: "2", I: "3", A: "4", Ld: "8" }
    ]
  },

  // Mounts with restrictions
  "griffon": {
    url: "unit/griffon",
    compNote: "Counts as Rare choice",
    stats: [
      { Name: "Griffon", M: "6", WS: "5", BS: "0", S: "5", T: "5", W: "4", I: "5", A: "4", Ld: "7" }
    ]
  },

  "dragon": {
    url: "unit/dragon",
    compNote: "Monstrous mount - occupies 2 Rare slots"
  },

  // Special rules for specific compositions
  "murderous renegade": {
    url: "special-rules/murderous-renegade",
    page: "TRLP, p. 18",
    compNote: "Renegade ruleset only"
  },

  "nuln state troops empire": {
    url: "special-rules/nuln-state-troops",
    compNote: "Combined Arms composition - Max 1 unit per Core"
  },

  // Magic items
  "sword of might": {
    url: "magic-items/sword-of-might",
    compNote: "No duplicate magic items"
  },

  "banner of the eternal flame": {
    url: "magic-items/banner-of-the-eternal-flame",
    compNote: "One per army"
  },

  // Weapons with restrictions
  "repeater bolt thrower": {
    url: "unit/repeater-bolt-thrower",
    compNote: "Max 1 per 500 points"
  },

  "helblaster volley gun weapon": {
    url: "weapons-of-war/helblaster-volley-gun",
    compNote: "Requires Engineering School of Nuln"
  },

  // Campaign or scenario specific
  "steam tank": {
    url: "unit/empire-steam-tank",
    compNote: "0-1 per army, Grand Melee restricted"
  },

  // Character upgrades
  "battle standard bearer": {
    url: "characters/the-battle-standard",
    compNote: "One per army, must be Hero or Lord"
  },

  "general": {
    url: "characters/the-general-characters",
    compNote: "Highest Leadership character automatically becomes General"
  }
};

// Example entries for rules-index-export.json
const exampleRulesIndexEntries = {
  // Ruleset-specific special rules
  "wisdom of the old ones renegade": {
    "url": "special-rules/wisdom-of-the-old-ones-renegade",
    "page": "TRLP, p. 11",
    "compNote": "Renegade Lizardmen only"
  },

  "born of fire renegade": {
    "url": "special-rules/born-of-fire-renegade",
    "page": "TRLP, p. 7",
    "compNote": "Renegade Chaos Dwarfs only"
  },

  // Army composition rules
  "open-war": {
    "url": "matched-play/open-war",
    "compNote": "Open War composition - No restrictions"
  },

  "grand-melee": {
    "url": "matched-play/grand-melee",
    "compNote": "Grand Melee - All units Battleline, no Lords/Rare"
  },

  "combined-arms": {
    "url": "matched-play/combined-arms",
    "compNote": "Combined Arms - Max 1 duplicate Core unit"
  },

  // Unit type notes
  "doomseeker dwarfs": {
    "url": "special-rules/doomseeker",
    "compNote": "Does not count toward minimum Core requirements"
  },

  "mercenaries": {
    "url": "special-rules/mercenaries",
    "compNote": "Max 25% of army points in Mercenaries"
  },

  // Equipment restrictions
  "gromril armour": {
    "url": "special-rules/gromril-armour",
    "page": "FoF, p. 39",
    "compNote": "Dwarfs only"
  },

  "elven reflexes": {
    "url": "special-rules/elven-reflexes",
    "page": "DE, p. 25, FoF, p. 145 & 185",
    "compNote": "Elves only"
  }
};

// Example of multiple comp notes scenarios
const complexScenarios = {
  // A unit that could trigger multiple comp notes
  exampleUnit: {
    name: "High Elf Prince",        // "Max 1 per 1000 points"
    mount: "Griffon",                // "Counts as Rare choice"
    weapons: ["Sword of Might"],     // "No duplicate magic items"
    magicItems: ["Crown of Command"], // "One per army"
    specialRules: ["Martial Prowess"] // No comp note
  },
  // Would display:
  // "Comp Notes: Max 1 per 1000 points, Counts as Rare choice, No duplicate magic items, One per army"
};

// Categorized comp note suggestions
const compNoteSuggestions = {
  // Quantity Limits
  limits: [
    "0-1 per army",
    "Max 1 per army",
    "Max 2 per army",
    "Max 1 per 1000 points",
    "Max 2 per 1500 points",
    "One per army",
    "Limited to 1-2 units"
  ],

  // Slot Restrictions
  slots: [
    "Counts as Lord choice",
    "Counts as Hero choice",
    "Counts as Rare choice",
    "Occupies 2 Rare slots",
    "Occupies 1 Lord + 1 Hero slot",
    "Does not count toward Core minimum"
  ],

  // Requirements
  requirements: [
    "Requires General to be [faction]",
    "Requires [special rule]",
    "Must take [unit] first",
    "Army must include [unit type]",
    "Only if General has [trait]"
  ],

  // Restrictions
  restrictions: [
    "Cannot be taken with [unit]",
    "Not allowed in [composition type]",
    "Restricted in Grand Melee",
    "Cannot duplicate",
    "Exclusive choice - replaces [unit]"
  ],

  // Ruleset Specific
  rulesets: [
    "Renegade ruleset only",
    "Combined Arms composition",
    "Grand Melee restricted",
    "Open War unrestricted",
    "Campaign only",
    "Matched Play legal"
  ],

  // Equipment
  equipment: [
    "No duplicate magic items",
    "One use per battle",
    "Cannot combine with [item]",
    "Replaces standard equipment",
    "[Faction] only"
  ],

  // Points or percentage based
  percentage: [
    "Max 25% of army points",
    "Max 50% of army points",
    "Counts double for points limits",
    "Free with [condition]"
  ]
};

export {
  exampleRulesMapEntries,
  exampleRulesIndexEntries,
  complexScenarios,
  compNoteSuggestions
};
