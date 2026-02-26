import rulesIndexExport from "./rules-index-export.json";

const additionalOWBRules = {
  "saurus scar veteran": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/saurus-scar-veteran.html?minimal=true",
    stats: [
      { Name: "Saurus Scar-Veteran", M: "4", WS: "5", BS: "0", S: "5", T: "5", W: "2", I: "3", A: "4", Ld: "8" }
    ]
  },
  "saurus oldblood": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/saurus-oldblood.html?minimal=true",
    stats: [
      { Name: "Saurus Oldblood", M: "4", WS: "6", BS: "0", S: "5", T: "5", W: "3", I: "3", A: "5", Ld: "8" }
    ]
  },
  "saurus warriors": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/saurus-warriors.html?minimal=true",
    stats: [
      { Name: "Saurus Warrior", M: "4", WS: "3", BS: "0", S: "4", T: "4", W: "1", I: "1", A: "2", Ld: "8" },
      { Name: "Spawn Leader", M: "4", WS: "3", BS: "0", S: "4", T: "4", W: "1", I: "1", A: "3", Ld: "8" }
    ]
  },
  "crypt horrors": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/crypt-horrors.html?minimal=true",
    stats: [
      { Name: "Crypt Horror", M: "6", WS: "3", BS: "0", S: "4", T: "5", W: "3", I: "2", A: "3", Ld: "5" },
      { Name: "Crypt Haunter", M: "6", WS: "3", BS: "0", S: "4", T: "5", W: "3", I: "2", A: "4", Ld: "5" }
    ]
  },
  "varghulf": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/varghulf.html?minimal=true",
    stats: [
      { Name: "Varghulf", M: "8", WS: "5", BS: "0", S: "5", T: "5", W: "4", I: "4", A: "4", Ld: "4" }
    ]
  },
  "vargheists": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/vargheists.html?minimal=true",
    stats: [
      { Name: "Vargheist", M: "6", WS: "4", BS: "0", S: "5", T: "4", W: "3", I: "4", A: "3", Ld: "7" },
      { Name: "Vargoyle", M: "6", WS: "4", BS: "0", S: "5", T: "4", W: "3", I: "4", A: "4", Ld: "7" }
    ]
  },
  "strigoi ghoul king": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/strigoi-ghoul-king.html?minimal=true",
    stats: [
      { Name: "Strigoi Ghoul King", M: "6", WS: "6", BS: "3", S: "5", T: "5", W: "3", I: "7", A: "5", Ld: "8" }
    ]
  },
  "zzzzap": { fullUrl: "https://owapps.grra.me/owb/rules/special-rules/zzzzap.html?minimal=true" },
  "doomwheel": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/doomwheel.html?minimal=true",
    stats: [
      { Name: "Doomwheel", M: "3D6", WS: "-", BS: "-", S: "5", T: "5", W: "4", I: "-", A: "-", Ld: "-" },
      { Name: "Warlock (x1)", M: "-", WS: "3", BS: "3", S: "3", T: "-", W: "-", I: "3", A: "1", Ld: "7" },
      { Name: "Rats", M: "-", WS: "2", BS: "0", S: "2", T: "-", W: "-", I: "4", A: "2D6", Ld: "5" }
    ]
  },
  "the fellblade": { fullUrl: "https://owapps.grra.me/owb/rules/magic-items/the-fellblade.html?minimal=true" },
  "plagueclaw catapult": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/plagueclaw-catapult.html?minimal=true",
    stats: [
      { Name: "Plagueclaw Catapult", M: "-", WS: "-", BS: "-", S: "-", T: "6", W: "4", I: "-", A: "-", Ld: "-" },
      { Name: "Plague Monk Crew", M: "5", WS: "3", BS: "3", S: "3", T: "4", W: "3", I: "2", A: "D3+3", Ld: "6" }
    ]
  },
  "poisoned wind globadiers": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/poisoned-wind-globadiers.html?minimal=true",
    stats: [
      { Name: "Globadier", M: "5", WS: "3", BS: "4", S: "3", T: "3", W: "1", I: "4", A: "1", Ld: "5" }
    ]
  },"warplock jezzails": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/warplock-jezzails.html?minimal=true",
    stats: [
      { Name: "Jezzail Team", M: "5", WS: "3", BS: "4", S: "3", T: "3", W: "1", I: "3", A: "2", Ld: "5" }
    ]
  },
  "high priest of ulric": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/high-priest-of-ulric.html?minimal=true",
    stats: [
      { Name: "High Priest of Ulric", M: "4", WS: "5", BS: "3", S: "4", T: "4", W: "3", I: "5", A: "3", Ld: "9" }
    ]
  },
  "lector of sigmar": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/lector-of-sigmar.html?minimal=true",
    stats: [
      { Name: "Lector of Sigmar", M: "4", WS: "5", BS: "3", S: "4", T: "4", W: "3", I: "5", A: "3", Ld: "9" }
    ]
  },
  "sisters of the thorn": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/sisters-of-the-thorn.html?minimal=true",
    stats: [
      { Name: "Sister of the Thorn", M: "-", WS: "4", BS: "5", S: "3", T: "3", W: "1", I: "4", A: "1", Ld: "9" },
      { Name: "Handmaiden of the Thorn", M: "-", WS: "4", BS: "6", S: "3", T: "3", W: "1", I: "4", A: "2", Ld: "9" },
      { Name: "Steed of Isha", M: "8", WS: "3", BS: "-", S: "4", T: "-", W: "-", I: "4", A: "1", Ld: "-" }
    ]
  },
  "grave guard": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/grave-guard.html?minimal=true",
    stats: [
      { Name: "Grave Guard", M: "4", WS: "3", BS: "3", S: "4", T: "4", W: "1", I: "3", A: "1", Ld: "7" },
      { Name: "Seneschal", M: "4", WS: "3", BS: "3", S: "4", T: "4", W: "1", I: "3", A: "2", Ld: "7" }
    ]
  },
  "tomb guard": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/tomb-guard.html?minimal=true",
    stats: [
      { Name: "Tomb Guard", M: "4", WS: "3", BS: "3", S: "4", T: "4", W: "1", I: "2", A: "1", Ld: "7" },
      { Name: "Tomb Captain", M: "4", WS: "3", BS: "3", S: "4", T: "4", W: "1", I: "3", A: "2", Ld: "7" }
    ]
  },
  "sea guard garrison commander": {
    url: "unit/sea-guard-garrison-commander",
    stats: [
      { Name: "Sea Guard Garrison Commander", M: "5", WS: "6", BS: "7", S: "4", T: "3", W: "3", I: "5", A: "3", Ld: "9" }
    ]
  },
  "demigryph": {
    url:  "unit/demigryph",
    stats: [
      { Name: "Demigryph", M: "7", WS: "4", BS: "-", S: "5", T: "(+1)", W: "(+1)", I: "4", A: "3", Ld: "-" }
    ]
  },
  "shieldbearers": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/shieldbearers.html?minimal=true",
    stats: [
      { Name: "Shieldbearers", M: "3", WS: "5", BS: "-", S: "4", T: "-", W: "(+3)", I: "2", A: "3", Ld: "-" }
    ]
  },
  "grail reliquae": { fullUrl: "https://owapps.grra.me/owb/rules/unit/grail-reliquae.html?minimal=true" },
  "the green knight": {
    fullUrl: "https://owapps.grra.me/owb/rules/unit/the-green-knight.html?minimal=true",
    stats: [
      { Name: "The Green Knight", M: "-", WS: "7", BS: "3", S: "4", T: "4", W: "4", I: "6", A: "4", Ld: "9" },
      { Name: "The Shadow Steed", M: "8", WS: "4", BS: "-", S: "4", T: "-", W: "-", I: "4", A: "1", Ld: "-" }
    ]
  },
  "wildwood rangers": {
    url: "unit/wildwood-rangers",
    stats: [
      { Name: "Wildwood Ranger", M: "5", WS: "5", BS: "4", S: "4", T: "3", W: "1", I: "4", A: "1", Ld: "9" },
      { Name: "Wildwood Warden", M: "5", WS: "5", BS: "4", S: "4", T: "3", W: "1", I: "4", A: "2", Ld: "9" }
    ]
  },
  "kharibdyss": {
    url: "unit/kharibdyss.html",
    stats: [
      { Name: "Kharibdyss", M: "6", WS: "5", BS: "0", S: "7", T: "6", W: "5", I: "3", A: "5", Ld: "6" },
      { Name: "Beastmaster Handlers (x2)", M: "6", WS: "4", BS: "-", S: "3", T: "-", W: "-", I: "4", A: "1", Ld: "8" }
    ]
  },
  "war hydra": {
    url: "unit/war-hydra",
    stats: [
      { Name: "War Hydra", M: "6", WS: "4", BS: "0", S: "5", T: "6", W: "5", I: "3", A: "2", Ld: "6" },
      { Name: "Beastmaster Handlers (x2)", M: "6", WS: "4", BS: "-", S: "3", T: "-", W: "-", I: "4", A: "1", Ld: "8" }
    ]
  },
  "cygor": {
    url: "unit/cygor",
    stats: [
      { Name: "Cygor", M: "7", WS: "2", BS: "1", S: "6", T: "6", W: "6", I: "3", A: "4", Ld: "8" }
    ]
  },
  "dragon ogre shaggoth": {
    url: "units/dragon-ogre-shaggoth",
    stats: [
      { Name: "Shaggoth", M: "7", WS: "6", BS: "2", S: "6", T: "6", W: "6", I: "4", A: "5", Ld: "9" }
    ]
  },
  "bloodletters of khorne": {
    url: "unit/bloodletters-of-khorne",
    stats: [
      { Name: "Bloodletter", M: "5", WS: "5", BS: "3", S: "4", T: "4", W: "1", I: "4", A: "1", Ld: "7" },
      { Name: "Bloodreaper", M: "5", WS: "5", BS: "3", S: "4", T: "4", W: "1", I: "4", A: "2", Ld: "7" },
    ],
  },
  "gnoblar scraplauncher": {
    url: "unit/gnoblar-scraplauncher",
    stats: [
      { Name: "Scraplauncher", M: "-", WS: "-", BS: "-", S: "5", T: "6", W: "5", I: "-", A: "-", Ld: "-" },
      { Name: "Gnoblar Scrapper (x7)", M: "-", WS: "2", BS: "3", S: "2", T: "-", W: "-", I: "3", A: "1", Ld: "5" },
      { Name: "Rhinox (x1)", M: "6", WS: "3", BS: "-", S: "5", T: "-", W: "-", I: "2", A: "3", Ld: "-" },
    ],
  },
  "questing knights": {
    url: "unit/questing-knights",
    stats: [
      { Name: "Questing Knight", M: "-", WS: "5", BS: "2", S: "4", T: "3", W: "1", I: "4", A: "2", Ld: "8" },
      { Name: "Paragon", M: "-", WS: "5", BS: "2", S: "4", T: "3", W: "1", I: "4", A: "3", Ld: "8" },
      { Name: "Bretonnian Warhorse", M: "8", WS: "3", BS: "-", S: "3", T: "-", W: "-", I: "3", A: "1", Ld: "-" },
    ],
  },
  "throwing spears": { url: "weapons-of-war/throwing-spear" },
  halberds: { url: "weapons-of-war/halberd" },
  "additional hand weapons": {
    url: "weapons-of-war/two-hand-weapons-additional-hand-weapon",
  },
  "cavalry spears": { url: "weapons-of-war/cavalry-spear" },
  "repeater handguns": { url: "weapons-of-war/repeater-handgun" },
  "hand weapons": { url: "weapons-of-war/hand-weapon" },
  flails: { url: "weapons-of-war/flail" },
  "plague censers": { url: "weapons-of-war/plague-censer" },
  "great weapons": { url: "weapons-of-war/great-weapon" },
  whips: { url: "weapons-of-war/whip" },
  spears: { url: "weapons-of-war/spears" },
  "morning stars": { url: "weapons-of-war/morning-star" },
  blowpipes: { url: "weapons-of-war/blowpipe" },
  handguns: { url: "weapons-of-war/handgun" },
  lances: { url: "weapons-of-war/lance" },
  shortbows: { url: "weapons-of-war/shortbow" },
  "thrusting spears": { fullUrl: "https://owapps.grra.me/owb/rules/weapons-of-war/thrusting-spear.html?minimal=true" },
  javelins: { url: "weapons-of-war/javelin" },
  longbows: { url: "weapons-of-war/longbow" },
  pistols: { url: "weapons-of-war/pistol" },
  "throwing axes": { url: "weapons-of-war/throwing-axe" },
  hellblades: { url: "weapons-of-war/hellblade" },
  "repeater pistols": { url: "weapons-of-war/repeater-pistol" },
  "blackbriar javelins": { url: "weapons-of-war/blackbriar-javelin" },
  drakeguns: { url: "weapons-of-war/drakegun" },
  "great hammers": { url: "weapons-of-war/great-hammer" },
  "brimstone guns": { url: "weapons-of-war/brimstone-gun" },
  clatterguns: { url: "weapons-of-war/clattergun" },
  crossbows: { url: "weapons-of-war/crossbow" },
  "throwing weapons": { url: "weapons-of-war/throwing-weapons" },
  slings: { url: "weapons-of-war/sling" },
  blunderbusses: { url: "weapons-of-war/blunderbuss" },
  "repeater handbows": { url: "weapons-of-war/repeater-handbow" },
  "repeater crossbows": { url: "weapons-of-war/repeater-crossbow" },
  "daemons of khorne": { url: "special-rules/daemon-of-khorne" },
  "daemons of tzeentch": { url: "special-rules/daemon-of-tzeentch" },
  "daemons of nurgle": { url: "special-rules/daemon-of-nurgle" },
  "daemons of slaanesh": { url: "special-rules/daemon-of-slaanesh" },
  "asrai spears": { url: "weapons-of-war/asrai-spear" },
  "asrai longbows": { url: "weapons-of-war/asrai-longbow" },
  general: { url: "characters/the-general-characters" },
  "moonfire shots": { url: "weapons-of-war/moonfire-shot" },
  "battle standard bearer": { url: "characters/the-battle-standard" },
  champions: { url: "command-groups/champions" },
  musician: { url: "command-groups/musicians" },
  "standard bearer": { url: "command-groups/standard-bearers" },
  wizard: { url: "magic/wizards" },
  "level 1 wizard": { url: "magic/levels-of-wizardry" },
  "level 2 wizard": { url: "magic/levels-of-wizardry" },
  "level 3 wizard": { url: "magic/levels-of-wizardry" },
  "level 4 wizard": { url: "magic/levels-of-wizardry" },
  "storm call warriors": {
    url: "special-rules/storm-call",
  },
  "doomseeker dwarfs": {
    url: "special-rules/doomseeker",
  },
  "armour piercing": {
    url: "the-shooting-phase/armour-piercing",
  },
  "nuln state troops empire": {
    url: "special-rules/nuln-state-troops",
  },
  "crown of horns beastmen": {
    url: "magic-item/crown-of-horns-beastmen",
  },
  "crown of horns cathay": {
    url: "weapons-of-war/crown-of-horns-grand-cathay",
  },
  "engine of the gods renegade": {
    url: "special-rules/engine-of-the-gods-renegade",
  },
  "crown of antlers beastmen": {
    url: "special-rules/crown-of-antlers",
  },
  "crown of antlers wood-elf-realms": {
    url: "magic-item/crown-of-antlers",
  },
  "heavy infantry": { url: "troop-types-in-detail/heavy-infantry" },
  "helblaster volley gun weapon": {
    url: "weapons-of-war/helblaster-volley-gun",
  },
  "helstorm rocket battery weapon": {
    url: "weapons-of-war/helstorm-rocket-battery",
  },
  "organ gun weapon": {
    url: "war-machines/organ-guns",
  },
  "screaming skull catapult weapon": {
    url: "weapons-of-war/screaming-skull-catapult",
  },
  "open-war": {
    url: "matched-play/open-war",
  },
  "grand-melee": {
    url: "matched-play/grand-melee",
  },
  "combined-arms": {
    url: "matched-play/combined-arms",
  },
  "grand-melee-combined-arms": {
    url: "warhammer-armies/army-composition-lists",
  },
  "battle-march": {
    url: "warhammer-armies/battle-march",
  },
  "dreadquake mortar weapon": {
    url: "weapons-of-war/dreadquake-mortar",
  },
};

export const synonyms = {
  "the witch": "suffer not...",
  "the revenant": "suffer not...",
  "the mutant": "suffer not...",
  "the daemon": "suffer not...",
  "spear of kurnous": "the spear of kurnous",
  warbows: "warbow",
  greatbows: "greatbow",
  "chracian great blades": "chracian great blade",
  "swords of hoeth": "sword of hoeth",
  "gromril great axes": "gromril great axe",
  "bows of avelorn": "bow of avelorn",
  "ceremonial halberds": "ceremonial halberd",
  "wolf hammers": "wolf hammer",
  shields: "shield",
  bellower: "bellowers & musicians",
  "revered guardian": "champions",
  "patrol leader": "champions",
  "sky leader": "champions",
  "great cannon": "cannon",
  "repeater bolt thrower": "bolt thrower",
  "bolt thrower": "bolt throwers",
  plagueswords: "plaguesword",
  "steam guns dwarfs": "steam gun dwarfs",
  "har ganeth greatswords": "har ganeth greatsword",
  "dread halberds": "dread halberd",
  fanatics: "fanatic",
  "nasty skulkers": "nasty skulker",
  "leadbelcher guns": "leadbelcher gun",
  "leadbelcher guns renegade": "leadbelcher gun renegade",
  "grimfrost weapons": "grimfrost weapon",
  "tiranoc chariots": "tiranoc chariot",
  "steam tank": "empire steam tank",
  halberds: "halberd",
  polearms: "polearm",
  gyrocopters: "gyrocopter",
  "scout gyrocopters": "scout gyrocopter",
  ironfists: "ironfist",
  "ironfists renegade": "ironfist renegade",
  "marauder chieftain": "champions",
  "marauder horsemaster": "champions",
  "lion guard captain": "champions",
  "chracian captain": "champions",
  "jade officer": "champions",
  "jade lancer officer": "champions",
  boss: "champions",
  marksman: "champions",
  preceptor: "champions",
  seneschal: "champions",
  "skeleton champion": "champions",
  "inner circle preceptor": "champions",
  "doom wolf": "champions",
  "crypt haunter": "champions",
  "crypt ghast": "champions",
  "glade knight": "champions",
  kastellan: "champions",
  sharpshooter: "champions",
  hellwraith: "champions",
  crusher: "champions",
  "demigryph preceptor": "champions",
  "count's champion": "champions",
  vargoyle: "champions",
  lordling: "champions",
  reaver: "champions",
  hag: "champions",
  master: "champions",
  bloodshade: "champions",
  "tower master": "champions",
  "draich master": "champions",
  "wildwood warden": "champions",
  "first knight": "champions",
  "dread knight": "champions",
  bladesinger: "champions",
  "handmaiden of the thorn": "champions",
  "hell knight": "champions",
  plagueridden: "champions",
  "spawn leader": "champions",
  "iridescent horror": "champions",
  "ectoplasmic horror": "champions",
  heartseeker: "champions",
  alluress: "champions",
  "master moulder": "champions",
  sergeant: "champions",
  "veteran sergeant": "champions",
  bloodreaper: "champions",
  nymph: "champions",
  guardian: "champions",
  harbinger: "champions",
  "high sister": "champions",
  groinbiter: "champions",
  snarefinger: "champions",
  "high helm": "champions",
  bloodkine: "champions",
  "gouge-horn": "champions",
  "true-horn": "champions",
  "half-horn": "champions",
  gorehoof: "champions",
  shartak: "champions",
  "maneater captain": "champions",
  thunderfist: "champions",
  "keeper of the flame": "champions",
  nightleader: "champions",
  assassin: "champions",
  greyback: "champions",
  "sea master": "champions",
  "pack leader": "champions",
  "grail guardian": "champions",
  champion: "champions",
  gutlord: "champions",
  desperado: "champions",
  "wild hunter": "champions",
  "wind rider": "champions",
  esquire: "champions",
  elder: "champions",
  "lord's bowmen": "champions",
  "ol' deadeye": "champions",
  "royal champion": "champions",
  sentinel: "champions",
  yeoman: "champions",
  gallant: "champions",
  pyroclaster: "champions",
  villein: "champions",
  paragon: "champions",
  warden: "champions",
  "militia leader": "champions",
  ironbeard: "champions",
  "ripperdactyl champion": "champions",
  prospector: "champions",
  "eternal warden": "champions",
  ironwarden: "champions",
  "prophet of doom": "champions",
  overseer: "champions",
  deathmask: "champions",
  "plague deacon": "champions",
  fangleader: "champions",
  watchmaster: "champions",
  "foe-render": "champions",
  "splice-horn": "champions",
  clawleader: "champions",
  "master of arms": "champions",
  "master of arrows": "champions",
  "tomb captain": "champions",
  "master charioteer": "champions",
  "master of horse": "champions",
  kroxigors: "kroxigor",
  ancient: "champions",
  "venerable ancient": "champions",
  "necropolis captain": "champions",
  "royal clan veteran": "champions",
  "borri forkbeard": "champions",
  headtaker: "champions",
  "skin wolf jarl": "champions",
  "first sword": "champions",
  captain: "champions",
  officer: "champions",
  "veteran officer": "champions",
  commander: "champions",
  "shrine keeper": "champions",
  "veteran commander": "champions",
  "boar chariot": "orc boar chariot",
  "wolf chariot": "goblin wolf chariot",
  fireglaives: "fireglaive",
  "warplock jezzails": "warplock jezzails",
  "warplock jezzails skaven": "warplock jezzail",
  "scourgerunner chariots": "scourgerunner chariot",
  "bloodwrack shrines": "bloodwrack shrine",
  "bloodwrack medusas": "bloodwrack medusa",
  "snotling pump wagons": "snotling pump wagon",
  "goblin wolf chariots": "goblin wolf chariot",
  "expeditionary marksman": "expeditionary marksmen",
  "braces of pistols": "brace of pistols",
  "troll magic": "lore of troll magic",
  "empire knights panther": "empire knights",
  "empire knights of the white wolf": "empire knights",
  "empire knights of the fiery heart": "empire knights",
  "empire knights of the blazing sun": "empire knights",
  "empire knights of morr": "empire knights",
  "inner circle knights panther": "inner circle knights",
  "inner circle knights of the white wolf": "inner circle knights",
  "inner circle knights of the fiery heart": "inner circle knights",
  "inner circle knights of the blazing sun": "inner circle knights",
  "inner circle knights of morr": "inner circle knights",
  "demigryph knights panther": "demigryph knights",
  "demigryph knights of the white wolf": "demigryph knights",
  "demigryph knights of the fiery heart": "demigryph knights",
  "demigryph knights of the blazing sun": "demigryph knights",
  "demigryph knights of morr": "demigryph knights",
  "ogre pistols": "ogre pistol",
  "light cannons": "light cannon",
  "bigger choppier axe": "bigger, choppier axe",
  orion: "orion, the king in the woods",
  araloth: "araloth, lord of talsyn",
  kralmaw: "kralmaw, the prophet of ruin",
  ghorros: "ghorros warhoof",
  "primal magic": "lore of primal magic",
  "a tingle in the air": "herdstones",
  "dark sorcery": "herdstones",
  "fearsome edifice": "herdstones",
  "bestial fury beastmen": "herdstones",
  "cathayan lances": "cathayan lance",
  "sky lantern crane guns": "sky lantern crane gun",
  "iron hail guns": "iron hail gun",
  warhorses: "warhorse",
  "barded warhorses": "barded warhorse",
  "chaos furies of tzeentch": "chaos furies",
  "chaos furies of nurgle": "chaos furies",
  "chaos furies of slaanesh": "chaos furies",
  "chaos furies of khorne": "chaos furies",
  shadowlands: "lore of the shadowlands",
};

export const rulesMap = {
  ...rulesIndexExport,
  ...additionalOWBRules,
};
