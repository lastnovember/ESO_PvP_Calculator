import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const constants = JSON.parse(readFileSync(join(here, '..', 'data', 'constants.json'), 'utf8'));

// Every leaf entry that carries a value must say where it came from.
// A source on an ancestor covers its children (a table row that yields several numbers).
function walk(node, path, out, covered = false) {
  if (Array.isArray(node)) { node.forEach((v, i) => walk(v, `${path}[${i}]`, out, covered)); return; }
  if (node && typeof node === 'object') {
    const has = covered || 'source' in node;
    const carriesMagnitude = 'value' in node || 'oneHand' in node
      || (Array.isArray(node.values) && node.values.length > 0 && (typeof node.values[0] === 'number' || 'value' in node.values[0]));
    if (carriesMagnitude && !has) out.push(path);
    for (const [k, v] of Object.entries(node)) walk(v, path ? `${path}.${k}` : k, out, has);
  }
}

test('constants.json: every valued entry carries a source', () => {
  const missing = [];
  walk(constants, '', missing);
  // nested "values" arrays inside an entry that itself has a source are fine
  const real = missing.filter((p) => !/\.values\[\d+\]$/.test(p) && !/\.(large|small)$/.test(p) && !/stats$/.test(p));
  assert.deepEqual(real, []);
});

test('constants.json: unverified entries are flagged verified:false', () => {
  const bad = [];
  (function w(n, p) {
    if (n && typeof n === 'object' && !Array.isArray(n)) {
      if (n.source === 'UNVERIFIED' && n.verified !== false) bad.push(p);
      for (const [k, v] of Object.entries(n)) w(v, `${p}.${k}`);
    } else if (Array.isArray(n)) n.forEach((v, i) => w(v, `${p}[${i}]`));
  })(constants, '');
  assert.deepEqual(bad, []);
});

test('constants.json: Champion passive stars fit under the per constellation cap', () => {
  const cap = constants.championPoints.perConstellationCap.value;
  const totals = {};
  for (const s of constants.championPoints.stars) {
    if (!s.slottable) totals[s.constellation] = (totals[s.constellation] || 0) + s.maxPoints;
  }
  for (const [c, t] of Object.entries(totals)) assert.ok(t + 4 * 75 <= cap, `${c}: ${t}`);
});

test('constants.json: 13 mundus stones and 39 named buffs', () => {
  assert.equal(Object.keys(constants.mundus.stones).length, 13);
  assert.equal(Object.keys(constants.namedBuffs.buffs).length, 39);
});

test('constants.json: every glyph quality row runs white to gold and ends on the value in use', () => {
  const E = constants.enchants;
  const order = ['white', 'green', 'blue', 'purple', 'gold'];
  const check = (name, by, gold) => {
    assert.deepEqual(Object.keys(by), order, name);
    const seq = order.map((q) => (Array.isArray(by[q]) ? by[q][0] : by[q]));
    for (let i = 1; i < seq.length; i += 1) assert.ok(seq[i] > seq[i - 1], `${name}: ${seq.join(' ')}`);
    assert.deepEqual(by.gold, gold, `${name}: gold row is the engine value`);
  };
  for (const [name, g] of Object.entries(E.armor)) check(name, g.byQuality, g.large.value);
  let withRows = 0;
  for (const [name, g] of Object.entries(E.jewelry)) if (g.byQuality) { withRows += 1; check(name, g.byQuality, g.magnitude.value); }
  assert.equal(withRows, Object.keys(E.jewelry).length - 1, 'every jewelry glyph but Increase Bash Damage (stale page) has its page row');
  assert.equal(E.glyphQualityFactor.gold, 1);
  assert.ok(E.glyphSmallRatio.value > 0.4 && E.glyphSmallRatio.value < 0.41);
});

test('constants.json: weapon damage by quality comes from the Nirnhoned tables and meets the gold ratings', () => {
  const W = constants.items.weaponDamageByQuality;
  assert.equal(W.oneHanded.base.gold, constants.items.weaponDamage.value);
  assert.equal(W.twoHanded.base.gold, constants.items.twoHandedMeleeWeaponDamage.value);
  assert.equal(W.oneHanded.nirnhoned.gold, 1535, '1335 x 1.15');
  assert.equal(W.twoHanded.nirnhoned.gold, 1806, 'the page row; 1571 x 1.15 would round to 1807');
  assert.deepEqual(Object.values(W.oneHanded.base), [1037, 1072, 1108, 1132, 1335]);
  assert.deepEqual(Object.values(W.twoHanded.base), [1220, 1262, 1304, 1332, 1571]);
});

test('constants.json: set bonus quality rows come from the six Craftable Sets tables', () => {
  const T = constants.sets.bonusByQuality;
  assert.deepEqual(Object.keys(T), ['recovery', 'maxMagickaOrStamina', 'maxHealth', 'weaponAndSpellDamage', 'critRating', 'resistance', 'offensivePenetration', 'critResistance']);
  assert.equal(T.critResistance.byQuality.blue, 399);
  assert.equal(T.critResistance.multiplier.blue, T.resistance.multiplier.blue);
  const order = ['white', 'green', 'blue', 'purple', 'gold'];
  // penetration has no table: blue read from a tooltip, the rest follow the resistance ratios
  assert.equal(T.offensivePenetration.verified, false);
  assert.equal(T.offensivePenetration.byQuality.blue, 1401);
  assert.equal(T.offensivePenetration.byQuality.purple, 1435);
  assert.equal(constants.traits.jewelry.Arcane.values[0].byQuality.blue, 827, 'the blue Spellshredder Ring reads Arcane 827');
  assert.equal(T.offensivePenetration.multiplier.blue, T.resistance.multiplier.blue);
  for (const [name, t] of Object.entries(T)) {
    if (name === 'offensivePenetration' || name === 'critResistance') continue;
    assert.deepEqual(Object.keys(t.byQuality), order, name);
    const seq = order.map((q) => t.byQuality[q]);
    for (let i = 1; i < seq.length; i += 1) assert.ok(seq[i] > seq[i - 1], `${name}: ${seq.join(' ')}`);
    assert.equal(t.multiplier.gold, 1);
    assert.match(t.source, /^tables\/uesp_Online_Craftable_Sets_t0[3-8]\.csv row '160'/);
  }
  assert.equal(T.maxHealth.byQuality.gold, 1206);
  assert.equal(T.weaponAndSpellDamage.byQuality.white, 112);
  assert.equal(T.resistance.byQuality.purple, 2871);
});
