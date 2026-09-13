import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { parseText, resolveBrackets, splitSentences } from '../../tools/parse_effects/grammar.js';
import { parseCsv } from '../../tools/parse_effects/csv.js';

const here = dirname(fileURLToPath(import.meta.url));
const effects = JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8'));

const flat = (r) => r.effects.filter((e) => e.stat).map((e) => [e.stat, e.value, e.kind]);

test('csv: quoted fields, embedded commas and newlines, doubled quotes', () => {
  const rows = parseCsv('a,b,c\n1,"x, y","line1\nline2"\n2,"say ""hi""",z\n');
  assert.deepEqual(rows, [['a', 'b', 'c'], ['1', 'x, y', 'line1\nline2'], ['2', 'say "hi"', 'z']]);
});

test('brackets resolve to the last (max rank) value, sentences split on periods', () => {
  assert.equal(resolveBrackets('absorbs [9000 / 9098 / 9198 / 9297] damage'), 'absorbs 9297 damage');
  assert.deepEqual(splitSentences('One thing. Two things. (Three)'), ['One thing.', 'Two things.', '(Three)']);
});

test('set bonus ranges resolve to the maximum', () => {
  assert.deepEqual(flat(parseText('Adds 6-300 Weapon Damage and Spell Damage')), [['weaponAndSpellDamage', 300, 'flat']]);
  assert.deepEqual(flat(parseText('Adds 4% Healing Taken')), [['healingTaken', 4, 'percent']]);
  assert.deepEqual(flat(parseText('Adds 15-657 Critical Chance')), [['critRating', 657, 'flat']]);
  assert.deepEqual(flat(parseText('Adds 34-1487 Armor')), [['armor', 1487, 'flat']]);
});

test('named buffs at all times', () => {
  const r = parseText('Gain Minor Berserk at all times, increasing your damage done by 5%.');
  assert.deepEqual(r.effects.map((e) => e.buff), ['Minor Berserk']);
  assert.equal(r.status, 'ok');
});

test('per piece and per ability conditions', () => {
  const a = parseText('Increases your Max Health by 2% for each piece of Heavy Armor equipped.');
  assert.deepEqual(a.effects[0].condition, { type: 'armorPieces', weight: 'heavy' });
  const b = parseText('Increases your Weapon Damage and Spell Damage by 3% for each Fighters Guild ability slotted.');
  assert.deepEqual(b.effects[0].condition, { type: 'slotted', line: 'Fighters Guild', perAbility: true });
  const c = parseText('Increases your Critical Chance rating by 438 for each Nightblade ability slotted, increasing your chance to critically strike by 2% per ability.');
  assert.deepEqual(c.effects[0].condition, { type: 'slotted', class: 'Nightblade', perAbility: true });
  const d = parseText('Increases your Max Health, Stamina, and Magicka by 2% per type of Armor (Heavy, Medium, Light) that you have equipped.');
  assert.deepEqual(d.effects[0].condition, { type: 'armorTypes' });
});

test('weapon prefix conditions and per weapon type bonuses', () => {
  const a = parseText('WITH BOW EQUIPPED Increases your Critical Chance rating by 1314.');
  assert.deepEqual(a.effects[0].condition, { type: 'weapon', weapon: 'bow' });
  const b = parseText('WHILE DUAL WIELDING Grants a bonus based on the type of weapon equipped: Each axe increases your Critical Damage done by 6%. Each mace increases your Offensive Penetration by 1487.');
  assert.equal(b.effects.length, 2);
  assert.deepEqual(b.effects[1].condition, { type: 'all', of: [{ type: 'weapon', weapon: 'dual wield' }, { type: 'weaponTypeCount', weaponType: 'mace' }] });
});

test('Battle Spirit alternate values are kept as conditions, not discarded', () => {
  const r = parseText('Increases your Critical Damage and Healing by 25%. This effect is reduced to 5% against targets with Battle Spirit.');
  const vals = r.effects.filter((e) => e.stat).map((e) => [e.value, e.condition.active]);
  assert.deepEqual(vals, [[25, false], [5, true]]);
  const w = parseText('WHILE YOU ARE IN WEREWOLF FORM Increases your Weapon Damage and Spell Damage by 25%, reducing to 10% against targets with Battle Spirit. Grants you Major Resolve.');
  assert.deepEqual(w.effects.map((e) => e.stat ? [e.stat, e.value] : ['buff', e.buff]), [['weaponAndSpellDamage', 25], ['weaponAndSpellDamage', 10], ['buff', 'Major Resolve']]);
});

test('while slotted effects on abilities', () => {
  const r = parseText('While slotted on either bar, you gain Minor Expedition, increasing your Movement Speed by 15%.');
  assert.deepEqual(r.effects, [{ buff: 'Minor Expedition', condition: { type: 'slotted', ability: '$self' }, raw: r.effects[0].raw }]);
  const m = parseText('While slotted you gain Major Savagery and Prophecy, increasing your Weapon Critical and Spell Critical rating by 2629 and your Max Magicka is increased by [2 / 3 / 4 / 5]%.');
  assert.deepEqual(m.effects.map((e) => e.buff || [e.stat, e.value]), ['Major Savagery', 'Major Prophecy', ['maxMagicka', 5]]);
});

test('costs and block', () => {
  assert.deepEqual(flat(parseText('Reduces the cost of Roll Dodge by 120 Stamina per stage.')), [['rollDodgeCost', -120, 'flat']]);
  assert.deepEqual(flat(parseText('WITH ONE HAND WEAPON AND SHIELD EQUIPPED Reduces the Stamina cost of your One Hand and Shield abilities by 15% and reduces the cost of blocking by 36%.')), [['blockCost', -36, 'percent']]);
  assert.deepEqual(flat(parseText('Increases the amount of damage you can block by 2% per stage.')), [['blockMitigation', 2, 'percent']]);
  assert.deepEqual(flat(parseText('Reduces your Block Mitigation to 0.')), [['blockMitigation', 0, 'set']]);
  assert.deepEqual(flat(parseText('Reduced cost of all abilities by 6%.')), [['abilityCost', -6, 'percent']]);
});

test('combat and target text becomes a proc, never a sheet effect', () => {
  const r = parseText('When you deal damage, you have a 10% chance to gain 500 Weapon Damage for 10 seconds.');
  assert.equal(r.status, 'proc');
  assert.ok(r.effects.every((e) => e.kind === 'proc'));
  const q = parseText('Grants 41 Weapon and Spell Damage to your damaging abilities per stage.');
  assert.equal(q.status, 'proc');
});

test('effects.json: coverage and known entries', () => {
  const c = effects._meta.coverage;
  assert.ok(c.setBonuses.parsedPercent >= 95, `set bonuses ${c.setBonuses.parsedPercent}`);
  assert.ok(c.passives.parsedPercent >= 95, `passives ${c.passives.parsedPercent}`);
  assert.equal(c.championStars.parsedPercent, 100);
  assert.equal(c.namedBuffs.parsedPercent, 100);
  const rc = effects.sets['Rallying Cry'];
  assert.equal(rc.maxPieces, 5);
  assert.equal(rc.bonuses['2'].effects[0].stat, 'critRating');
  assert.equal(effects.sets['Oakensoul Ring'].mythic, true);
  assert.equal(effects.sets['Oakensoul Ring'].mythicSlot, 'ring');
  assert.equal(effects.sets['Slimecraw'].monster, true);
  assert.equal(effects.sets['Crushing Wall'].weaponSet, true);
  assert.equal(effects.sets["Druid's Braid"].maxPieces, 12);
  assert.deepEqual(effects.buffs['Major Resolve'].effects.map((e) => [e.stat, e.value]), [['physicalAndSpellResistance', 5948]]);
  assert.equal(effects.championStars['Fortified'].effects[0].value, 1730);
  assert.equal(effects.championStars['Boundless Vitality'].effects[0].value, 1400);
  assert.equal(effects.skills.passives['Juggernaut'].effects[0].value, 2);
  assert.ok(effects.skills.actives['Concealed Weapon'].whileSlotted.some((e) => e.buff === 'Minor Expedition'));
  assert.ok(effects.skills.passives['Landslide'] || effects.skills.passives['Battle Roar']);
  assert.equal(Object.values(effects.skills.passives).filter((p) => p.line === 'Class Mastery').length, 35);
});
