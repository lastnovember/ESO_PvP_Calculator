import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { computeSheet } from '../src/engine.js';

const here = dirname(fileURLToPath(import.meta.url));
const data = {
  constants: JSON.parse(readFileSync(join(here, '..', 'data', 'constants.json'), 'utf8')),
  effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')),
};

// Game label -> engine output key. Several spellings accepted.
export const MAIN_KEYS = {
  'max health': 'maxHealth', 'maximum health': 'maxHealth', 'health': 'maxHealth',
  'max magicka': 'maxMagicka', 'maximum magicka': 'maxMagicka', 'magicka': 'maxMagicka',
  'max stamina': 'maxStamina', 'maximum stamina': 'maxStamina', 'stamina': 'maxStamina',
  'health recovery': 'healthRecovery', 'magicka recovery': 'magickaRecovery', 'stamina recovery': 'staminaRecovery',
  'weapon damage': 'weaponDamage', 'spell damage': 'spellDamage',
  'weapon critical': 'weaponCritChance', 'spell critical': 'spellCritChance', 'critical chance': 'weaponCritChance',
  'critical damage': 'critDamage',
  'physical penetration': 'physicalPenetration', 'spell penetration': 'spellPenetration',
  'physical resistance': 'physicalResistance', 'spell resistance': 'spellResistance',
};
export const ADVANCED_KEYS = {
  'critical chance': 'weaponCritChancePercent', 'weapon critical': 'weaponCritChancePercent', 'spell critical': 'spellCritChancePercent',
  'critical damage': 'critDamagePercent', 'critical resistance': 'critResistance',
  'physical penetration': 'physicalPenetration', 'spell penetration': 'spellPenetration',
  'physical resistance': 'physicalResistance', 'physical mitigation': 'physicalMitigationPercent',
  'spell resistance': 'spellResistance', 'spell mitigation': 'spellMitigationPercent',
  'damage done': 'damageDonePercent', 'healing done': 'healingDonePercent', 'healing taken': 'healingTakenPercent',
  'damage taken': 'damageTakenPercent', 'damage shield strength': 'damageShieldStrengthPercent',
  'block cost': 'blockCost', 'block mitigation': 'blockMitigationPercent',
  'roll dodge cost': 'rollDodgeCost', 'dodge roll cost': 'rollDodgeCost', 'sprint cost': 'sprintCost',
  'break free cost': 'breakFreeCost', 'bash cost': 'bashCost', 'bash damage': 'bashDamageBonus',
  'movement speed': 'movementSpeedPercent', 'sprint speed': 'sprintSpeedPercent',
  'magicka cost': 'magickaCostPercent', 'stamina cost': 'staminaCostPercent', 'ultimate cost': 'ultimateCostPercent',
};

const PERCENT_KEYS = new Set(['weaponCritChance', 'spellCritChance', 'critDamage']);

function compare(fixture) {
  const rows = [];
  const unknown = [];
  let filled = 0;
  for (const [zone, battleSpirit] of [['outOfPvpZone', false], ['inPvpZone', true]]) {
    const readings = fixture.readings && fixture.readings[zone];
    if (!readings) continue;
    const build = { ...fixture.build, battleSpirit };
    const result = computeSheet(build, data);
    if (result.validation.errors.length) rows.push({ zone, key: 'validation', expected: '', computed: result.validation.errors.join('; '), ok: false });
    for (const [barKey, idx] of [['bar1', 0], ['bar2', 1]]) {
      const bar = readings[barKey];
      if (!bar || !result.bars[idx]) continue;
      for (const [panel, map, out] of [['main', MAIN_KEYS, result.bars[idx].main], ['advanced', ADVANCED_KEYS, result.bars[idx].advanced]]) {
        for (const [label, expected] of Object.entries(bar[panel] || {})) {
          if (expected === null || expected === undefined || expected === '') continue;
          filled += 1;
          const key = map[label.toLowerCase().trim()];
          if (!key) { unknown.push(`${zone}/${barKey}/${panel}/${label}`); continue; }
          const computed = out[key];
          const exp = typeof expected === 'string' ? Number(expected.replace(/[%,\s]/g, '')) : expected;
          const isPct = panel === 'advanced' ? /Percent$/.test(key) : PERCENT_KEYS.has(key);
          const tol = isPct ? (fixture.tolerance?.percent ?? 0.15) : (fixture.tolerance?.flat ?? 1);
          const ok = computed != null && Math.abs(computed - exp) <= tol;
          rows.push({ zone, bar: barKey, panel, key: label, expected: exp, computed, ok });
        }
      }
    }
  }
  return { rows, unknown, filled };
}

const dir = join(here, 'fixtures');
const files = readdirSync(dir).filter((f) => f.endsWith('.fixture.json') && !f.startsWith('TEMPLATE'));

test('fixture template is valid JSON with a computable build', () => {
  const t = JSON.parse(readFileSync(join(dir, 'TEMPLATE.fixture.json'), 'utf8'));
  const r = computeSheet(t.build, data);
  assert.ok(Array.isArray(r.bars) && r.bars.length === 2);
});

for (const f of files) {
  test(`fixture ${f}`, (t) => {
    const fixture = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    const { rows, unknown, filled } = compare(fixture);
    if (!filled) { t.skip('no readings filled in yet'); return; }
    const bad = rows.filter((r) => !r.ok);
    const fmt = (r) => `${r.ok ? 'ok  ' : 'MISS'} ${r.zone}/${r.bar}/${r.panel} ${r.key}: game ${r.expected} vs engine ${r.computed}`;
    console.log(`\n${f}\n` + rows.map(fmt).join('\n'));
    if (unknown.length) console.log('not modelled: ' + unknown.join(', '));
    assert.equal(bad.length, 0, `${bad.length} of ${rows.length} readings differ:\n` + bad.map(fmt).join('\n'));
  });
}
