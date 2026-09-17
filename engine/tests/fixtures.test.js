import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { computeSheet } from '../src/engine.js';
import { compare } from './fixture_compare.js';

const here = dirname(fileURLToPath(import.meta.url));
const data = {
  constants: JSON.parse(readFileSync(join(here, '..', 'data', 'constants.json'), 'utf8')),
  effects: JSON.parse(readFileSync(join(here, '..', 'data', 'effects.json'), 'utf8')),
};

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
    const { rows, unknown, filled } = compare(fixture, data);
    if (!filled) { t.skip('no readings filled in yet'); return; }
    const bad = rows.filter((r) => !r.ok);
    const fmt = (r) => `${r.ok ? 'ok  ' : 'MISS'} ${r.zone}/${r.bar}/${r.panel} ${r.key}: game ${r.expected} vs engine ${r.computed}`;
    console.log(`\n${f}\n` + rows.map(fmt).join('\n'));
    if (unknown.length) console.log('not modelled: ' + unknown.join(', '));
    if (fixture.status === 'open') { t.diagnostic(`${f}: ${bad.length} of ${rows.length} readings differ (status open, calibration in progress)`); return; }
    assert.equal(bad.length, 0, `${bad.length} of ${rows.length} readings differ:\n` + bad.map(fmt).join('\n'));
  });
}
