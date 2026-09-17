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
  const w = constants.items.weaponDamage.value;
  assert.equal(r.bars[0].main.weaponDamage, B.weaponDamage.value + w + 300);
  assert.equal(r.bars[1].main.weaponDamage, B.weaponDamage.value + w);
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
  const expected = B.maxHealth.value + Math.round(lord * (1 + 2 * 9.1 / 100)) + 4620 + E.large.value + E.small.value;
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
  const f = constants.items.qualityFactor.purple.value;
  assert.deepEqual(rows(on, 'weaponDamage', 'item mainHand (purple) rating'), [Math.round(gold * f * 1.14)], 'purple Nirnhoned is 14% on a purple rating');
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
