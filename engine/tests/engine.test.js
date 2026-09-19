import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { computeSheet, validateBuild, countSetPieces } from '../src/engine.js';

const here = dirname(fileURLToPath(import.meta.url));
const constants = JSON.parse(readFileSync(join(here, '..', 'data', 'constants.json'), 'utf8'));
const B = constants.base;

// Minimal hand written effects so the engine maths can be checked independently of the parser.
const effects = {
  sets: {
    'Test Set': { settype: 'All Weights', maxPieces: 5, mythic: false, monster: false, weaponSet: false,
      bonuses: {
        2: { effects: [{ stat: 'maxHealth', value: 1206, kind: 'flat' }] },
        5: { effects: [{ stat: 'weaponAndSpellDamage', value: 300, kind: 'flat' }] } } },
    'Test Monster': { settype: 'Monster Helm Sets', maxPieces: 2, mythic: false, monster: true, weaponSet: false, bonuses: {} },
    'Test Mythic A': { settype: 'Jewelry', maxPieces: 1, mythic: true, monster: false, weaponSet: false, bonuses: {} },
    'Test Mythic B': { settype: 'Jewelry', maxPieces: 1, mythic: true, monster: false, weaponSet: false, bonuses: {} },
  },
  skills: {
    passives: {
      Juggernaut: { line: 'Heavy Armor', effects: [{ stat: 'maxHealth', value: 2, kind: 'percent', condition: { type: 'armorPieces', weight: 'heavy' } }] },
      'Test Slot Passive': { line: 'Fighters Guild', effects: [{ stat: 'weaponAndSpellDamage', value: 3, kind: 'percent', condition: { type: 'slotted', line: 'Fighters Guild', perAbility: true } }] },
      'Test Proc': { line: 'Assassination', effects: [{ stat: 'weaponDamage', value: 999, kind: 'proc', raw: 'x' }] },
      'Test Mastery': { line: 'Class Mastery', class: 'Nightblade', effects: [{ stat: 'critDamage', value: 25, kind: 'percent', condition: { type: 'battleSpirit', active: false, scope: 'target' } }, { stat: 'critDamage', value: 5, kind: 'percent', condition: { type: 'battleSpirit', active: true, scope: 'target' } }, { stat: 'critDamageCap', value: 30, kind: 'flat' }] },
    },
    actives: {
      'Test FG Ability': { line: 'Fighters Guild', whileSlotted: [] },
      'Test Buff Ability': { line: 'Assassination', whileSlotted: [{ buff: 'Major Resolve', condition: { type: 'slotted', ability: 'Test Buff Ability' } }] },
    },
  },
  championStars: {
    Fortified: { name: 'Fortified', slottable: true, effects: [{ stat: 'armor', value: 1730, kind: 'flat' }] },
    'Hero\'s Vigor': { name: "Hero's Vigor", slottable: false, effects: [{ stat: 'maxHealth', value: 560, kind: 'flat' }] },
  },
  buffs: { 'Major Resolve': { effects: [{ stat: 'physicalAndSpellResistance', value: 5948, kind: 'flat' }] } },
};
const data = { constants, effects };

function naked(over = {}) {
  return {
    schemaVersion: 1, race: 'Nord', class: 'Nightblade',
    attributes: { health: 0, magicka: 0, stamina: 64 },
    championPoints: { enabled: false },
    mundus: null, food: null, vampireStage: 0, werewolf: false, werewolfForm: false, battleSpirit: false,
    passives: { mode: 'all' },
    gear: { head: null, shoulders: null, chest: null, hands: null, waist: null, legs: null, feet: null, necklace: null, ring1: null, ring2: null },
    bars: [
      { mainHand: null, offHand: null, skills: [], ultimate: null },
      { mainHand: null, offHand: null, skills: [], ultimate: null },
    ],
    ...over,
  };
}
const heavy = (set) => ({ set, weight: 'heavy', trait: null, enchant: null });

test('naked character: base values plus attribute points', () => {
  const r = computeSheet(naked(), data);
  assert.deepEqual(r.validation.errors, []);
  const m = r.bars[0].main;
  assert.equal(m.maxStamina, B.maxStamina.value + 64 * constants.attributePoints.staminaPerPoint.value);
  assert.equal(m.maxHealth, B.maxHealth.value);
  assert.equal(m.weaponDamage, B.weaponDamage.value);
  assert.equal(m.weaponCritChance, B.critChancePercent.value);
  assert.equal(m.spellCritChance, B.critChancePercent.value);
  assert.equal(m.physicalResistance, 0);
  assert.equal(r.bars[0].advanced.blockCost, B.blockCost.value);
  assert.equal(r.bars[0].advanced.movementSpeedPercent, 100);
});

test('flat set bonus then percent passive, armor rating summed', () => {
  const b = naked();
  b.gear.head = heavy('Test Set'); b.gear.shoulders = heavy('Test Set'); b.gear.chest = heavy('Test Set');
  b.gear.hands = heavy('Test Set'); b.gear.waist = heavy('Test Set');
  const r = computeSheet(b, data);
  assert.deepEqual(r.validation.errors, []);
  const m = r.bars[0].main;
  // (16000 + 1206) * (1 + 5 heavy * 2%)
  assert.equal(m.maxHealth, Math.round((B.maxHealth.value + 1206) * 1.10));
  const A = constants.items.armor.heavy;
  assert.equal(m.physicalResistance, A.head.value + A.shoulders.value + A.chest.value + A.hands.value + A.waist.value);
  assert.equal(m.spellResistance, m.physicalResistance);
  assert.equal(r.bars[0].advanced.physicalMitigationPercent, Math.round(m.physicalResistance / 660 * 10) / 10);
  assert.equal(m.weaponDamage, B.weaponDamage.value + 300);
  assert.equal(r.bars[1].main.weaponDamage, B.weaponDamage.value + 300);
});

test('a two handed weapon counts as two pieces on its own bar only', () => {
  const b = naked();
  b.gear.head = heavy('Test Set'); b.gear.shoulders = heavy('Test Set'); b.gear.chest = heavy('Test Set');
  b.bars[0].mainHand = { set: 'Test Set', type: 'greatsword', trait: null, enchant: null };
  b.bars[1].mainHand = { set: null, type: 'sword', trait: null, enchant: null };
  const counts = countSetPieces(b);
  assert.equal(counts.perBar[0]['Test Set'].total, 5);
  assert.equal(counts.perBar[1]['Test Set'].total, 3);
  const r = computeSheet(b, data);
  assert.deepEqual(r.validation.errors, []);
  const w = constants.items.weaponDamage.value; const w2 = constants.items.twoHandedMeleeWeaponDamage.value;
  const rating = (bar) => (['greatsword', 'battle axe', 'maul'].includes(bar.mainHand.type) ? w2 : w);
  assert.equal(r.bars[0].main.weaponDamage, B.weaponDamage.value + rating(b.bars[0]) + 300);
  assert.equal(r.bars[1].main.weaponDamage, B.weaponDamage.value + rating(b.bars[1]));
});

test('while slotted effects and per ability passives read the bar', () => {
  const b = naked();
  b.bars[0].skills = ['Test FG Ability', 'Test Buff Ability'];
  const r = computeSheet(b, data);
  assert.equal(r.bars[0].main.weaponDamage, Math.round(B.weaponDamage.value * 1.03));
  assert.equal(r.bars[0].main.physicalResistance, 5948);
  assert.equal(r.bars[1].main.physicalResistance, 0);
  assert.equal(r.bars[1].main.weaponDamage, B.weaponDamage.value);
});

test('proc effects are dropped and reported', () => {
  const r = computeSheet(naked(), data);
  assert.ok(r.bars[0].dropped.some((d) => d.source === 'passive Test Proc' && d.reason === 'proc'));
  assert.equal(r.bars[0].main.weaponDamage, B.weaponDamage.value);
});

test('Champion Points: passives always on, slottables only when slotted', () => {
  const b = naked({ championPoints: { enabled: true, slotted: { fitness: ['Fortified'] } } });
  const r = computeSheet(b, data);
  assert.equal(r.bars[0].main.physicalResistance, 1730);
  assert.equal(r.bars[0].main.maxHealth, B.maxHealth.value + 560);
  const off = computeSheet(naked({ championPoints: { enabled: true, slotted: {} } }), data);
  assert.equal(off.bars[0].main.physicalResistance, 0);
  const none = computeSheet(naked({ championPoints: { enabled: false } }), data);
  assert.equal(none.bars[0].main.maxHealth, B.maxHealth.value);
});

test('Battle Spirit halves Health Recovery and reports the advanced deltas', () => {
  const r = computeSheet(naked({ battleSpirit: true }), data);
  assert.equal(r.bars[0].main.healthRecovery, Math.round(B.healthRecovery.value * 0.5));
  assert.equal(r.bars[0].advanced.healingTakenPercent, 0, 'sheet value leaves Battle Spirit out');
  assert.equal(r.bars[0].advanced.battleSpirit.healingTakenPercent, -55);
  assert.equal(r.bars[0].advanced.battleSpirit.damageTakenPercent, -50);
  assert.equal(r.bars[0].advanced.abilityRangeBonusMeters, 8);
  const flag = computeSheet(naked({ battleSpirit: true, flags: { battleSpiritFlatHealth: true } }), data);
  assert.equal(flag.bars[0].main.maxHealth, B.maxHealth.value + data.constants.battleSpirit.legacyFlatMaxHealth.value);
  const off = computeSheet(naked({ battleSpirit: true, flags: { battleSpiritFlatHealth: false } }), data);
  assert.equal(off.bars[0].main.maxHealth, B.maxHealth.value, 'flag false leaves the flat health out');
});

test('mundus scaled by Divines, food flat, glyph large and small pieces', () => {
  const b = naked({ mundus: 'The Lord', food: 'purple-tristat' });
  b.gear.chest = { set: null, weight: 'light', trait: 'Divines', enchant: 'Health' };
  b.gear.hands = { set: null, weight: 'light', trait: 'Divines', enchant: 'Health' };
  const r = computeSheet(b, data);
  const lord = constants.mundus.stones['The Lord'].values[0].value;
  const E = constants.enchants.armor.Health;
  const expected = B.maxHealth.value + Math.round(lord * (1 + 2 * 9.1 / 100)) + 4624 + E.large.value + E.small.value;
  assert.equal(r.bars[0].main.maxHealth, expected);
});

test('validation: attribute sum, mythic limit, monster slot, two handed with off hand', () => {
  const b = naked();
  b.attributes = { health: 10, magicka: 10, stamina: 10 };
  b.gear.ring1 = { set: 'Test Mythic A', trait: null, enchant: null };
  b.gear.ring2 = { set: 'Test Mythic B', trait: null, enchant: null };
  b.gear.chest = heavy('Test Monster');
  b.bars[0].mainHand = { set: null, type: 'bow', trait: null, enchant: null };
  b.bars[0].offHand = { set: null, type: 'shield', trait: null, enchant: null };
  const v = validateBuild(b, data);
  assert.ok(!v.warnings.some((e) => e.includes('unspent')), 'unspent points are not a warning');
  assert.ok(v.errors.some((e) => e.includes('more than one mythic')));
  assert.ok(v.errors.some((e) => e.includes('monster set')));
  assert.ok(v.errors.some((e) => e.includes('off hand must be empty')));
});

test('strategies can be switched', () => {
  const b = naked();
  b.gear.chest = { set: null, weight: 'heavy', trait: 'Sturdy', enchant: null };
  b.gear.ring1 = { set: null, trait: null, enchant: 'Reduce Block Cost' };
  const a = computeSheet(b, data).bars[0].advanced.blockCost;
  const c = computeSheet(b, data, { strategies: { costOrder: 'percentThenFlat' } }).bars[0].advanced.blockCost;
  assert.equal(a, Math.round((B.blockCost.value - 203) * 0.96));
  assert.equal(c, Math.round(B.blockCost.value * 0.96 - 203));
  assert.throws(() => computeSheet(b, data, { strategies: { costOrder: 'nope' } }));
});

test('Class Mastery: only purchased passives, hidden while subclassing, target scoped Battle Spirit values', () => {
  const off = computeSheet(naked(), data);
  assert.equal(off.bars[0].main.critDamage, 0, 'sheet shows the bonus above base');
  const on = computeSheet(naked({ classMastery: ['Test Mastery'], battleSpirit: true }), data);
  assert.equal(on.bars[0].main.critDamage, 25);
  const pvp = computeSheet(naked({ classMastery: ['Test Mastery'], battleSpirit: true }), data, { strategies: { battleSpiritTargetValues: 'pvpTarget' } });
  assert.equal(pvp.bars[0].main.critDamage, 5);
  const sub = computeSheet(naked({ classMastery: ['Test Mastery'], classSkillLines: ['Assassination', 'Shadow', 'Ardent Flame'] }), data);
  assert.equal(sub.bars[0].main.critDamage, 0);
  const bad = validateBuild(naked({ classMastery: ['Nope'] }), data);
  assert.ok(bad.errors.some((e) => e.includes('unknown Class Mastery')));
});

test('skillLines toggles switch guild passives off', () => {
  const on = computeSheet(naked({ bars: [{ mainHand: null, offHand: null, skills: ['Test FG Ability'], ultimate: null }, { mainHand: null, offHand: null, skills: [], ultimate: null }] }), data);
  assert.equal(on.bars[0].main.weaponDamage, Math.round(B.weaponDamage.value * 1.03));
  const off = computeSheet(naked({ skillLines: { 'Fighters Guild': false }, bars: [{ mainHand: null, offHand: null, skills: ['Test FG Ability'], ultimate: null }, { mainHand: null, offHand: null, skills: [], ultimate: null }] }), data);
  assert.equal(off.bars[0].main.weaponDamage, B.weaponDamage.value);
});

// Real data: armor passives follow the equipped weights.
test('real data: light armor passives scale with the piece count', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const b = naked();
  for (const slot of ['head', 'shoulders', 'chest', 'hands', 'waist']) b.gear[slot] = { set: null, weight: 'light', trait: null, enchant: null };
  b.gear.legs = { set: null, weight: 'heavy', trait: null, enchant: null };
  b.gear.feet = { set: null, weight: 'medium', trait: null, enchant: null };
  const r = computeSheet(b, real);
  const rows = (stat, src) => r.bars[0].breakdown[stat].filter((x) => x.source === src).map((x) => x.value);
  assert.deepEqual(rows('spellResistance', 'passive Spell Warding'), [726 * 5]);
  assert.deepEqual(rows('weaponCritRating', 'passive Prodigy'), [219 * 5]);
  assert.deepEqual(rows('physicalPenetration', 'passive Concentration'), [939 * 5]);
  assert.deepEqual(rows('physicalResistance', 'passive Resolve'), [343 * 1]);
  assert.deepEqual(rows('maxHealth', 'passive Juggernaut'), [2 * 1]);
  assert.deepEqual(rows('weaponDamage', 'passive Agility'), [2 * 1]);
  assert.deepEqual(rows('maxHealth', 'passive Undaunted Mettle'), [2 * 3]);
  assert.ok(real.effects.skills.actives['Torchbearer'].scribing);
  assert.equal(real.effects.skills.actives['Torchbearer'].line, 'Fighters Guild');
});

// Real data: "for each X ability slotted" and "with an X ability slotted" passives count the bar.
test('real data: slotted passives count abilities on the bar', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const rows = (r, stat, src) => (r.bars[0].breakdown[stat] || []).filter((x) => x.source === src).map((x) => x.value);

  // Warden: Advanced Species is 5% Critical Damage per Animal Companions ability; Flourish needs one slotted.
  const w = naked(); w.class = 'Warden'; w.classSkillLines = ['Animal Companions', 'Green Balance', "Winter's Embrace"];
  w.bars[0].skills = ['Cutting Dive', 'Deep Fissure', 'Blue Betty']; w.bars[0].ultimate = 'Eternal Guardian';
  w.bars[1].skills = ['Arctic Blast'];
  let r = computeSheet(w, real);
  assert.deepEqual(rows(r, 'critDamage', 'passive Advanced Species'), [5 * 4], 'three morphs plus the ultimate count');
  assert.deepEqual(rows(r, 'magickaRecovery', 'passive Flourish'), [20]);
  assert.deepEqual(rows(r, 'physicalResistance', 'passive Frozen Armor'), [], 'nothing from Winter\'s Embrace on the front bar');
  assert.deepEqual((r.bars[1].breakdown.physicalResistance || []).filter((x) => x.source === 'passive Frozen Armor').map((x) => x.value), [1240], 'one Winter\'s Embrace ability on the back bar');
  assert.deepEqual((r.bars[1].breakdown.critDamage || []).filter((x) => x.source === 'passive Advanced Species'), [], 'no Animal Companions ability on the back bar');

  // Sorcerer: Expert Mage is 108 Weapon and Spell Damage per Sorcerer ability, any Sorcerer line.
  const s = naked(); s.class = 'Sorcerer'; s.classSkillLines = ['Dark Magic', 'Daedric Summoning', 'Storm Calling'];
  s.bars[0].skills = ['Crystal Fragments', 'Hardened Ward', 'Streak']; s.bars[0].ultimate = 'Greater Storm Atronach';
  r = computeSheet(s, real);
  assert.deepEqual(rows(r, 'weaponDamage', 'passive Expert Mage'), [108 * 4]);

  // Nightblade: Pressure Points per Nightblade ability, Hemorrhage with any Assassination ability, Dark Vigor per Shadow ability.
  const n = naked(); n.class = 'Nightblade'; n.classSkillLines = ['Assassination', 'Shadow', 'Siphoning'];
  n.bars[0].skills = ['Killer\'s Blade', 'Shadowy Disguise', 'Dark Cloak', 'Siphoning Attacks'];
  r = computeSheet(n, real);
  assert.deepEqual(rows(r, 'weaponCritRating', 'passive Pressure Points'), [438 * 4]);
  assert.deepEqual(rows(r, 'critDamage', 'passive Hemorrhage'), [10]);
  assert.deepEqual(rows(r, 'maxHealth', 'passive Dark Vigor'), [5 * 2]);
  assert.deepEqual(rows(r, 'maxMagicka', 'passive Magicka Flood'), [6]);

  // Guild lines: Magicka Controller counts a scribed Mages Guild grimoire, Slayer counts Fighters Guild abilities.
  const g = naked(); g.bars[0].skills = ['Ulfsild\'s Contingency', 'Inner Light', 'Camouflaged Hunter']; g.bars[0].ultimate = 'Dawnbreaker of Smiting';
  r = computeSheet(g, real);
  assert.deepEqual(rows(r, 'maxMagicka', 'passive Magicka Controller'), [2 * 2]);
  assert.deepEqual(rows(r, 'weaponDamage', 'passive Slayer'), [3 * 2]);
});

// Real data: perfected and normal pieces of a trial set count together (patch note 103, Update 30).
test('real data: perfected and normal trial pieces share the set count', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const rows = (r, stat, src) => (r.bars[0].breakdown[stat] || []).filter((x) => x.source === src).map((x) => x.value);
  const b = naked();
  for (const slot of ['head', 'chest', 'legs', 'feet']) b.gear[slot] = { set: 'Slivers of the Null Arca', weight: 'medium', trait: null, enchant: null };
  b.gear.hands = { set: 'Perfected Slivers of the Null Arca', weight: 'medium', trait: null, enchant: null };
  let r = computeSheet(b, real);
  assert.equal(r.validation.errors.length, 0, r.validation.errors.join('; '));
  assert.equal(r.bars[0].setCounts['Slivers of the Null Arca'], 5, 'one perfected piece counts toward the five');
  assert.equal(r.bars[0].setPerfected['Slivers of the Null Arca'], 1);
  assert.deepEqual(rows(r, 'weaponCritRating', 'set Slivers of the Null Arca (2)'), [657]);
  assert.deepEqual(rows(r, 'weaponCritRating', 'set Slivers of the Null Arca (4)'), [657]);
  assert.deepEqual(rows(r, 'weaponDamage', 'set Perfected Slivers of the Null Arca (5 perfected)'), [], 'the perfected extra needs five perfected pieces');
  for (const slot of ['head', 'chest', 'legs', 'feet']) b.gear[slot].set = 'Perfected Slivers of the Null Arca';
  r = computeSheet(b, real);
  assert.equal(r.bars[0].setCounts['Slivers of the Null Arca'], 5);
  assert.deepEqual(rows(r, 'weaponDamage', 'set Perfected Slivers of the Null Arca (5 perfected)'), [129]);
});

// Item quality: traits from the trait table columns, ratings by the quality factor, only with the toggle on.
test('real data: item quality scales traits and ratings when the toggle is on', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const rows = (r, stat, src) => (r.bars[0].breakdown[stat] || []).filter((x) => x.source === src).map((x) => x.value);
  const b = naked({ mundus: 'The Lover' });
  b.gear.hands = { set: null, weight: 'light', trait: 'Divines', enchant: null, quality: 'purple' };
  b.bars[0].mainHand = { set: null, type: 'sword', trait: 'Nirnhoned', enchant: null, quality: 'purple' };
  const off = computeSheet(b, real);
  const gold = constants.items.weaponDamage.value;
  assert.deepEqual(rows(off, 'weaponDamage', 'item mainHand rating'), [Math.round(gold * 1.15)], 'toggle off: gold');
  assert.deepEqual(rows(off, 'physicalPenetration', 'mundus The Lover'), [Math.round(2744 * 1.091)]);
  b.flags = { ...b.flags, itemQuality: true };
  const on = computeSheet(b, real);
  assert.deepEqual(rows(on, 'weaponDamage', 'item mainHand (purple) rating'), [constants.items.weaponDamageByQuality.oneHanded.nirnhoned.purple], 'purple Nirnhoned sword: the Nirnhoned page row (1290)');
  assert.equal(constants.items.weaponDamageByQuality.oneHanded.nirnhoned.purple, 1290);
  b.bars[0].mainHand.trait = null;
  assert.deepEqual(rows(computeSheet(b, real), 'weaponDamage', 'item mainHand (purple) rating'), [1132], 'purple sword base: 1132');
  assert.deepEqual(rows(on, 'physicalPenetration', 'mundus The Lover'), [Math.round(2744 * 1.081)], 'purple Divines is 8.1%');
});

// Skill slots are positional: an ability in slot 5 stays in slot 5 and still counts.
test('real data: skill slots are positional and weapon passives follow the equipped weapon', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const rows = (r, stat, src) => (r.bars[0].breakdown[stat] || []).filter((x) => x.source === src).map((x) => x.value);
  const n = naked(); n.class = 'Nightblade'; n.classSkillLines = ['Assassination', 'Shadow', 'Siphoning'];
  n.bars[0].skills = [null, null, null, null, "Killer's Blade"];
  let r = computeSheet(n, real);
  assert.equal(r.validation.errors.length, 0);
  assert.deepEqual(rows(r, 'weaponCritRating', 'passive Pressure Points'), [438], 'slot 5 counts');
  n.bars[0].skills = ["Killer's Blade", null, "Killer's Blade", null, null];
  assert.ok(computeSheet(n, real).validation.errors.some((e) => /same skill/.test(e)));
  // Destruction Staff passives need the staff, not a staff skill on the bar
  const d = naked(); d.bars[0].skills = ['Destructive Clench', null, null, null, null];
  d.bars[0].mainHand = { set: null, type: 'sword', trait: null, enchant: null }; d.bars[0].offHand = { set: null, type: 'sword', trait: null, enchant: null };
  r = computeSheet(d, real);
  assert.deepEqual(rows(r, 'blockCost', 'passive Ancient Knowledge'), [], 'no ice staff, no Ancient Knowledge');
  d.bars[0].mainHand = { set: null, type: 'ice staff', trait: null, enchant: null }; d.bars[0].offHand = null;
  r = computeSheet(d, real);
  assert.deepEqual(rows(r, 'blockCost', 'passive Ancient Knowledge'), [-36]);
});

test('real data: fixture 005 rules (block points per heavy piece, spell only flats, typed resistance, Dark Stalker, CP stars not taken)', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked(); n.race = 'Wood Elf'; n.class = 'Templar'; n.classSkillLines = ['Aedric Spear', 'Dawn\'s Wrath', 'Restoring Light'];
  n.championPoints = { enabled: true, slotted: { warfare: [], fitness: ['Expert Evasion'], craft: [] } };
  for (const slot of ['head', 'chest', 'legs']) n.gear[slot] = { set: null, weight: 'heavy', trait: null, enchant: null };
  n.gear.waist = { set: null, weight: 'light', trait: null, enchant: null };
  let r = computeSheet(n, real); let a = r.bars[0].advanced; let m = r.bars[0].main;
  // block mitigation: 50 x 1.04 (Fortification) + 3 heavy pieces
  assert.equal(a.blockMitigationPercent, 55);
  // Spell Warding (726, spell only) is not multiplied by Balanced Warrior's 6% armor
  assert.equal(m.spellResistance - m.physicalResistance, 726);
  // nor is the Defending trait (fixture 006): the staff adds exactly 3276
  n.bars[0].mainHand = { set: null, type: 'ice staff', trait: 'Defending', enchant: null };
  assert.equal(computeSheet(n, real).bars[0].main.physicalResistance - m.physicalResistance, 3276);
  n.bars[0].mainHand = null;
  // Resist Affliction adds 2310 to the Disease and Poison percents only
  assert.equal(a.diseaseResistancePercent, Math.round((m.physicalResistance + 2310) / 660 * 10) / 10);
  assert.equal(a.bleedResistancePercent, Math.round(m.physicalResistance / 660 * 10) / 10);
  // Expert Evasion leaves the regular roll dodge cost but notes the free one
  assert.ok(r.bars[0].notes.some((x) => /Expert Evasion/.test(x)));
  assert.ok(a.rollDodgeCost > 3000);
  // Sprinter not taken: the 40 flat goes away ((500 - 40) x 0.97 Grace = 446, then 500 x 0.97 = 485)
  assert.equal(a.sprintCost, 446);
  n.championPoints.notTaken = ['Sprinter'];
  r = computeSheet(n, real); a = r.bars[0].advanced;
  assert.equal(a.sprintCost, 485);
  // Dark Stalker: sneak speed capped at 100
  n.vampireStage = 3;
  r = computeSheet(n, real);
  assert.equal(r.bars[0].advanced.sneakSpeedPercent, 100);
  // The Shadow counts for Critical Healing (no Fighting Finesse slotted here, so 11 alone)
  n.mundus = 'The Shadow';
  r = computeSheet(n, real);
  assert.equal(r.bars[0].advanced.critHealingPercent, 11);
  assert.equal(r.bars[0].main.critDamage, 11);
});

test('real data: fixture 007 rules (CP star points, Battle Spirit adds no flat health by default)', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked();
  n.championPoints = { enabled: true, slotted: { warfare: [], fitness: [], craft: ['Sustaining Shadows'] } };
  let r = computeSheet(n, real);
  assert.equal(r.bars[0].advanced.sneakCost, 59, '118 x 0.5 at 50 stages');
  n.championPoints.points = { 'Sustaining Shadows': 10 };
  r = computeSheet(n, real);
  assert.equal(r.bars[0].advanced.sneakCost, Math.round(118 * 0.9), '10 of 50 stages');
  assert.ok(r.bars[0].breakdown.sneakCost.some((x) => /10 of 50/.test(x.source)));
  const plain = computeSheet(n, real).bars[0].main.maxHealth;
  n.battleSpirit = true;
  assert.equal(computeSheet(n, real).bars[0].main.maxHealth, plain, 'no flat health under Battle Spirit');
  n.flags = { battleSpiritFlatHealth: true };
  assert.equal(computeSheet(n, real).bars[0].main.maxHealth, plain + 1600, 'legacy flag keeps the 1600');
});

test('real data: fixture 008 rules (Curative Curse under Battle Spirit, Deadly Bash on the base, shield 1720, Battlefield Mobility)', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked(); n.race = 'Breton'; n.class = 'Necromancer'; n.classSkillLines = ['Grave Lord', 'Bone Tyrant', 'Living Death'];
  n.championPoints = { enabled: true, slotted: { warfare: [], fitness: [], craft: [] } };
  let r = computeSheet(n, real);
  assert.equal(r.bars[0].advanced.healingDonePercent, 2, 'Blessed alone');
  n.battleSpirit = true;
  r = computeSheet(n, real);
  assert.equal(r.bars[0].advanced.healingDonePercent, 14, 'Curative Curse counts Battle Spirit as a negative effect');
  n.battleSpirit = false;
  // dagger and shield: Deadly Bash halves the base before the Savage Defense flat, the shield adds 1720 x 1.16
  const before = computeSheet(n, real).bars[0];
  n.bars[0].mainHand = { set: null, type: 'dagger', trait: null, enchant: null };
  n.bars[0].offHand = { set: null, type: 'shield', trait: 'Reinforced', enchant: null };
  r = computeSheet(n, real);
  assert.equal(r.bars[0].advanced.bashCost, Math.round(765 * 0.5 - 90));
  assert.equal(r.bars[0].main.physicalResistance - before.main.physicalResistance, Math.round(1720 * 1.16));
  assert.equal(r.bars[0].advanced.blockMoveSpeedPercent, 54);
});

test('real data: fixture 009 rules (Combat Medic near a keep, food health scale)', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked(); n.battleSpirit = true; n.championPoints = { enabled: true, slotted: { warfare: [], fitness: [], craft: [] } };
  const base = computeSheet(n, real).bars[0].advanced.healingDonePercent;
  n.flags = { nearKeep: true };
  assert.equal(computeSheet(n, real).bars[0].advanced.healingDonePercent, base + 20, 'Combat Medic near a keep');
  n.battleSpirit = false;
  assert.equal(computeSheet(n, real).bars[0].advanced.healingDonePercent, base, 'only under Battle Spirit');
  const skulls = constants.foods.items.find((f) => f.id === 'bewitched-sugar-skulls').stats;
  assert.deepEqual([skulls.maxHealth, skulls.maxMagicka, skulls.maxStamina, skulls.healthRecovery], [4624, 4250, 4250, 462]);
});

test('real data: Oakensoul Ring locks the back bar and grants its buffs', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked();
  n.bars[1].skills = ['Merciless Resolve', null, null, null, null]; n.class = 'Nightblade'; n.classSkillLines = ['Assassination', 'Shadow', 'Siphoning'];
  const plain = computeSheet(n, real);
  assert.equal(plain.lockedBy, undefined);
  n.gear.ring1 = { set: 'Oakensoul Ring', trait: 'Arcane', enchant: null };
  const r = computeSheet(n, real);
  assert.equal(r.lockedBy, 'Oakensoul Ring');
  assert.equal(r.bars[1].locked, true);
  assert.equal(r.bars[1].main.weaponDamage, r.bars[0].main.weaponDamage, 'back bar result is the front bar');
  // Major Brutality and Sorcery (20%), Major Resolve (5948), Minor Force, Major Savagery from the ring
  const srcs = r.bars[0].breakdown.weaponDamage.map((x) => x.source);
  assert.ok(srcs.some((x) => /Oakensoul.*Major Brutality/.test(x)), srcs.join(' | '));
  assert.ok(r.bars[0].breakdown.physicalResistance.some((x) => /Major Resolve/.test(x.source)));
  assert.ok(r.bars[0].breakdown.weaponCritRating.some((x) => /Oakensoul.*Major Savagery/.test(x.source)), 'Major Savagery from the ring');
  assert.equal(r.bars[0].main.weaponCritChance, plain.bars[0].main.weaponCritChance, 'same Major Savagery Merciless Resolve gave from the back bar');
  // the back bar's "on either bar" Merciless Resolve no longer reaches the front bar
  assert.ok(!r.bars[0].breakdown.weaponCritRating.some((x) => /Merciless/.test(x.source)));
  assert.ok(r.bars[0].notes.some((x) => /locked/.test(x)));
});

test('real data: Cyrodiil advanced sim flags (scrolls, enemy keeps, Emperorship, Continuous Attack)', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked(); n.battleSpirit = true; n.championPoints = { enabled: true, slotted: { warfare: [], fitness: [], craft: [] } };
  const base = computeSheet(n, real).bars[0];
  n.flags = { cyrodiil: { enabled: true, offensiveScrolls: 2, defensiveScrolls: 1, enemyKeeps: 3, allianceEmperorKeeps: 6, continuousAttack: true, emperor: true } };
  const r = computeSheet(n, real); const b = r.bars[0];
  assert.equal(b.main.weaponDamage, Math.round(base.main.weaponDamage * 1.15), 'offensive scrolls II 5% + Continuous Attack 10%');
  assert.equal(b.main.weaponCritChance, Math.round((base.main.weaponCritChance + 3) * 10) / 10, 'three enemy keeps');
  // Emperorship VI adds 1750 flat; the Emperor passive at 6 home keeps adds 75% Max Health on top
  assert.equal(b.main.maxHealth, Math.round((base.main.maxHealth + 1750) * 1.75), 'Emperorship VI plus the Emperor passive');
  assert.ok(b.breakdown.magickaRecovery.some((x) => /Domination/.test(x.source) && x.value === 100));
  assert.ok(b.breakdown.healingTaken.some((x) => /Monarch/.test(x.source) && x.value === 50));
  assert.ok(b.breakdown.magickaRecovery.some((x) => /Continuous Attack/.test(x.source) && x.value === 20), 'Continuous Attack recovery 20%');
  assert.ok(b.breakdown.physicalResistance.some((x) => /Defensive Scroll/.test(x.source)));
  n.battleSpirit = false;
  assert.equal(computeSheet(n, real).bars[0].main.maxHealth, base.main.maxHealth - 0, 'nothing outside Battle Spirit');
});

test('real data: Torc of the Last Ayleid King disables every other set; Velothi grants Minor Force', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked();
  n.gear.head = { set: 'Armor of the Trainee', weight: 'heavy', trait: null, enchant: null };
  const withTrainee = computeSheet(n, real).bars[0];
  assert.ok(withTrainee.breakdown.maxHealth.some((x) => /Trainee/.test(x.source)));
  n.gear.necklace = { set: 'Torc of the Last Ayleid King', trait: null, enchant: null };
  const r = computeSheet(n, real).bars[0];
  assert.ok(!r.breakdown.maxHealth.some((x) => /Trainee/.test(x.source)), 'Trainee disabled');
  assert.ok(r.breakdown.weaponDamage.some((x) => /Torc/.test(x.source) && x.value === 1337));
  assert.ok(r.notes.some((x) => /disabled/.test(x)));
  n.gear.necklace = { set: "Velothi Ur-Mage's Amulet", trait: null, enchant: null };
  assert.ok(computeSheet(n, real).bars[0].breakdown.critDamage.some((x) => /Velothi.*Minor Force/.test(x.source)));
});

test('real data: dual wield off hand share, active buffs, vampire penalty without Unnatural Resistance', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked();
  n.bars[0].mainHand = { set: null, type: 'mace', trait: 'Nirnhoned', enchant: null };
  n.bars[0].offHand = { set: null, type: 'mace', trait: 'Sharpened', enchant: null };
  const one = computeSheet({ ...n, bars: [{ ...n.bars[0], offHand: null }, n.bars[1]] }, real).bars[0].main.weaponDamage;
  const two = computeSheet(n, real).bars[0].main.weaponDamage;
  assert.equal(two - one, Math.round(1335 * 0.2367), 'off hand adds 23.67% of its rating');
  n.bars[0].offHand.trait = 'Nirnhoned';
  assert.equal(computeSheet(n, real).bars[0].main.weaponDamage - one, Math.round(1535 * 0.2367), 'trait counts on the off hand');
  // active buffs go through the named buff table and do not stack with themselves
  n.activeBuffs = ['Major Brutality', 'Major Brutality', 'Major Resolve'];
  const r = computeSheet(n, real).bars[0];
  assert.equal(r.breakdown.weaponDamage.filter((x) => /Major Brutality/.test(x.source)).length, 1);
  assert.ok(r.breakdown.physicalResistance.some((x) => /Major Resolve/.test(x.source)));
  // vampire stage 3: the full 60% penalty, no Unnatural Resistance anywhere
  const v = naked(); v.vampireStage = 3;
  const base = computeSheet(naked(), real).bars[0].main.healthRecovery;
  assert.equal(computeSheet(v, real).bars[0].main.healthRecovery, Math.round(base * 0.4));
  assert.equal(real.effects.skills.passives['Unnatural Resistance'], undefined);
});

test('real data: harm glyphs add 10 recovery scaled by Infused, Prismatic Recovery 84, Reduce Skill Cost 133', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked();
  const before = computeSheet(n, real).bars[0].main;
  n.gear.necklace = { set: null, trait: 'Arcane', enchant: 'Spell Damage' };
  n.gear.ring1 = { set: null, trait: 'Infused', enchant: 'Spell Damage' };
  n.gear.ring2 = { set: null, trait: 'Infused', enchant: 'Weapon Damage' };
  const r = computeSheet(n, real).bars[0];
  const mag = r.breakdown.magickaRecovery.filter((x) => /glyph/.test(x.source)).map((x) => x.value);
  const sta = r.breakdown.staminaRecovery.filter((x) => /glyph/.test(x.source)).map((x) => x.value);
  assert.deepEqual(mag, [10, 16], 'Spell Harm: 10 plain, 16 Infused (note 135)');
  assert.deepEqual(sta, [16], 'Physical Harm: 16 on the Infused ring');
  assert.equal(r.main.weaponDamage - before.weaponDamage, 174 + 278 + 278, 'the damage part is unchanged');
  n.gear.ring2 = { set: null, trait: 'Protective', enchant: 'Prismatic Recovery' };
  const p = computeSheet(n, real).bars[0];
  for (const stat of ['healthRecovery', 'magickaRecovery', 'staminaRecovery']) assert.equal(p.breakdown[stat].find((x) => /Prismatic/.test(x.source)).value, 84, 'Prismatic Recovery 84 each (tooltip)');
  n.gear.ring2 = { set: null, trait: 'Protective', enchant: 'Reduce Skill Cost' };
  assert.equal(computeSheet(n, real).bars[0].advanced.magickaCostFlat - r.advanced.magickaCostFlat, 133);
});

test('real data: sheet Bash Damage is the flat bonuses plus 0.02252 x the average resistance, times the physical percents', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const n = naked();
  const r = computeSheet(n, real).bars[0];
  const avg = (r.advanced.physicalResistance + r.advanced.spellResistance) / 2;
  const expected = Math.round((r.advanced.bashDamageBonus + 0.02252 * avg) * (1 + (r.advanced.physicalDamagePercent + r.advanced.damageDoneDirectPercent) / 100));
  assert.equal(r.advanced.bashDamage, expected);
  n.gear.necklace = { set: null, trait: 'Arcane', enchant: 'Increase Bash Damage' };
  const g = computeSheet(n, real).bars[0];
  assert.equal(g.advanced.bashDamageBonus - r.advanced.bashDamageBonus, 500, 'Glyph of Bashing adds 500 (note 087)');
  assert.ok(g.advanced.bashDamage > r.advanced.bashDamage);
});

// Glyph quality is its own axis under the same toggle: the item can be gold while its glyph is purple.
test('real data: glyph quality scales glyph magnitudes only when the toggle is on', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const rows = (r, stat, src) => (r.bars[0].breakdown[stat] || []).filter((x) => x.source === src).map((x) => x.value);
  const b = naked();
  b.gear.chest = { set: null, weight: 'light', trait: null, enchant: 'Health', enchantQuality: 'purple' };
  b.gear.hands = { set: null, weight: 'light', trait: 'Infused', enchant: 'Health', enchantQuality: 'purple', quality: 'blue' };
  b.gear.ring1 = { set: null, trait: null, enchant: 'Weapon Damage', enchantQuality: 'purple' };
  b.gear.ring2 = { set: null, trait: null, enchant: 'Prismatic Defense', enchantQuality: 'white' };
  const G = constants.enchants;
  const off = computeSheet(b, real);
  assert.deepEqual(rows(off, 'maxHealth', 'item chest glyph Health'), [G.armor.Health.large.value], 'toggle off: gold');
  assert.deepEqual(rows(off, 'maxHealth', 'item hands glyph Health'), [Math.round(G.armor.Health.small.value * 1.25)]);
  assert.deepEqual(rows(off, 'weaponDamage', 'item ring1 glyph Weapon Damage'), [174]);
  b.flags = { ...b.flags, itemQuality: true };
  const on = computeSheet(b, real);
  assert.deepEqual(rows(on, 'maxHealth', 'item chest glyph Health (purple glyph)'), [882], 'large piece: the purple row of the glyph page');
  const small = Math.floor(882 * G.glyphSmallRatio.value);
  assert.deepEqual(rows(on, 'maxHealth', 'item hands (blue) glyph Health (purple glyph)'), [Math.round(small * (1 + 17 / 100))], 'small piece truncated, blue Infused is 17%');
  assert.deepEqual(rows(on, 'weaponDamage', 'item ring1 glyph Weapon Damage (purple glyph)'), [160], 'jewelry: the purple row');
  assert.deepEqual(rows(on, 'staminaRecovery', 'item ring1 glyph Weapon Damage (purple glyph)'), [10], 'the 10 recovery holds at every quality');
  assert.equal(on.validation.errors.length, 0, on.validation.errors.join('; '));
});

// Arena weapon sets exist for one weapon kind.
test('real data: an arena weapon set on the wrong weapon kind is a validation error', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const b = naked();
  b.bars[0].mainHand = { set: 'Crushing Wall', type: 'bow', trait: null, enchant: null };
  let v = validateBuild(b, real);
  assert.ok(v.errors.some((e) => e.includes('Crushing Wall only comes as inferno staff, lightning staff, ice staff, not bow')), v.errors.join('; '));
  b.bars[0].mainHand.type = 'inferno staff';
  v = validateBuild(b, real);
  assert.deepEqual(v.errors, []);
  b.bars[1].mainHand = { set: 'Perfected Rampaging Slash', type: 'sword', trait: null, enchant: null };
  b.bars[1].offHand = { set: 'Perfected Rampaging Slash', type: 'shield', trait: null, enchant: null };
  v = validateBuild(b, real);
  assert.deepEqual(v.errors, [], 'a one hand and shield set takes the weapon and the shield');
  b.bars[1].offHand = { set: 'Perfected Cruel Flurry', type: 'shield', trait: null, enchant: null };
  v = validateBuild(b, real);
  assert.ok(v.errors.some((e) => e.includes('Cruel Flurry only comes as axe, mace, sword, dagger, not shield')), 'a dual wield set never takes a shield');
  // the perfected extra of an arena weapon: one perfected two handed weapon is two perfected pieces
  b.bars[1].mainHand = { set: 'Perfected Crushing Wall', type: 'lightning staff', trait: null, enchant: null };
  b.bars[1].offHand = null;
  const r = computeSheet(b, real);
  assert.deepEqual((r.bars[1].breakdown.physicalPenetration || []).filter((x) => x.source === 'set Perfected Crushing Wall (2 perfected)').map((x) => x.value), [1190]);
});

// Set bonuses scale with the quality of the set's pieces (Online:Craftable Sets quality tables).
test('real data: ranged set bonuses follow the piece quality when the toggle is on', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const rows = (r, stat, src) => (r.bars[0].breakdown[stat] || []).filter((x) => x.source === src).map((x) => x.value);
  const b = naked();
  for (const slot of ['head', 'shoulders', 'chest', 'hands', 'waist']) b.gear[slot] = { set: 'Aegis of Galenwe', weight: 'heavy', trait: null, enchant: null, quality: 'gold' };
  b.gear.waist.quality = 'purple';
  const off = computeSheet(b, real);
  assert.deepEqual(rows(off, 'maxHealth', 'set Aegis of Galenwe (2)'), [1206], 'toggle off: the gold CP160 maximum of "28-1206"');
  b.flags = { ...b.flags, itemQuality: true };
  const on = computeSheet(b, real);
  assert.deepEqual(rows(on, 'maxHealth', 'set Aegis of Galenwe (2) [purple]'), [1164], 'lowest piece is purple: the Epic CP160 row');
  assert.deepEqual(rows(on, 'healingTaken', 'set Aegis of Galenwe (4) [purple]'), [4], 'a percent bonus never scales');
  b.flags.strategies = { setBonusQuality: 'highestPiece' };
  const hi = computeSheet(b, real);
  assert.deepEqual(rows(hi, 'maxHealth', 'set Aegis of Galenwe (2)'), [1206]);
  b.flags.strategies = {};
  b.gear.waist.quality = 'white';
  const white = computeSheet(b, real);
  assert.deepEqual(rows(white, 'maxHealth', 'set Aegis of Galenwe (2) [white]'), [1051], 'the Normal CP160 row');
  // a type with no quality table keeps the gold value and says so
  const pen = Object.entries(real.effects.sets).find(([, s]) => s.maxPieces === 5 && !s.monster && !s.weaponSet && s.settype !== 'Jewelry' && s.bonuses['2'] && s.bonuses['2'].effects.some((e) => e.stat === 'critResistance' && e.ranged));
  assert.ok(pen, 'a Critical Resistance set exists');
  for (const slot of ['head', 'shoulders', 'chest', 'hands', 'waist']) b.gear[slot] = { set: pen[0], weight: 'heavy', trait: null, enchant: null, quality: 'purple' };
  const p = computeSheet(b, real);
  assert.deepEqual(rows(p, 'critResistance', `set ${pen[0]} (2) [purple]`), [pen[1].bonuses['2'].effects.find((e) => e.stat === 'critResistance').value]);
  assert.ok(p.bars[0].notes.some((n) => n.includes('no quality table')), p.bars[0].notes.join('; '));
});

// Sprint Cost: the armor passives multiply per source (or add and round up); the plain additive rule reads one low.
test('real data: sprint cost percents multiply per source (Templar with Sprinter reads 433, Necromancer 401)', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const fx = JSON.parse(readFileSync(join(here, 'fixtures', '011-templar-front-bar-sprinter.fixture.json'), 'utf8'));
  const b = JSON.parse(JSON.stringify(fx.build));
  assert.equal(computeSheet(b, real).bars[0].advanced.sprintCost, 433);
  b.flags = { ...(b.flags || {}), strategies: { sprintCostPercents: 'additiveCeil' } };
  assert.equal(computeSheet(b, real).bars[0].advanced.sprintCost, 433);
  b.flags.strategies = { sprintCostPercents: 'additive' };
  assert.equal(computeSheet(b, real).bars[0].advanced.sprintCost, 432, 'the additive rule the other costs follow reads one low');
  const necro = JSON.parse(readFileSync(join(here, 'fixtures', '007-necro-healer-front-bar.fixture.json'), 'utf8'));
  assert.equal(computeSheet(necro.build, real).bars[0].advanced.sprintCost, 401);
});

// A blue Spellshredder Hat tooltip (DK inventory, 2026-09-19): every quality axis on one item.
test('real data: the blue Spellshredder Hat reads back from the tables', async () => {
  const real = { constants, effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')) };
  const rows = (r, stat, src) => (r.bars[0].breakdown[stat] || []).filter((x) => x.source === src).map((x) => x.value);
  const b = naked();
  b.flags = { ...(b.flags || {}), itemQuality: true };
  const blue = (slot) => ({ set: 'Spellshredder', weight: 'light', trait: 'Invigorating', enchant: 'Magicka', quality: 'blue', enchantQuality: 'blue' });
  for (const slot of ['head', 'shoulders', 'chest', 'hands']) b.gear[slot] = blue(slot);
  const r = computeSheet(b, real);
  assert.deepEqual(rows(r, 'physicalResistance', 'item head (blue) armor'), [1151], 'armor 1151 on the tooltip');
  assert.deepEqual(rows(r, 'maxMagicka', 'item head (blue) glyph Magicka (blue glyph)'), [763], 'Adds 763 Maximum Magicka');
  assert.deepEqual(rows(r, 'healthRecovery', 'item head (blue) Invigorating'), [12], 'Invigorating 12');
  assert.deepEqual(rows(r, 'physicalPenetration', 'set Spellshredder (2) [blue]'), [1401], '(2 items) Adds 1401 Offensive Penetration');
  assert.deepEqual(rows(r, 'physicalPenetration', 'set Spellshredder (3) [blue]'), [1401]);
  assert.deepEqual(rows(r, 'weaponCritRating', 'set Spellshredder (4) [blue]'), [618], '(4 items) Adds 618 Critical Chance');
});
