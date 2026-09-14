#!/usr/bin/env node
/*
 * tools/build_app: inline the engine and the JSON data into app/index.html.
 *
 *   node tools/build_app/index.js
 *
 * Reads app/src/template.html, engine/src/engine.js, engine/data/constants.json
 * and engine/data/effects.json. The effects are slimmed (per effect raw text
 * dropped, bonus and passive text kept) so the page stays small enough for a
 * phone. The result makes no network requests at runtime.
 */
import { readFileSync, writeFileSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..');

const template = readFileSync(join(ROOT, 'app', 'src', 'template.html'), 'utf8');
let engine = readFileSync(join(ROOT, 'engine', 'src', 'engine.js'), 'utf8');
const constants = JSON.parse(readFileSync(join(ROOT, 'engine', 'data', 'constants.json'), 'utf8'));
const effects = JSON.parse(readFileSync(join(ROOT, 'engine', 'data', 'effects.json'), 'utf8'));

// ES module -> plain script exposing window.ESOEngine
engine = engine.replace(/^export default [^\n]*\n/m, '').replace(/^export (function|const|class|let)/gm, '$1');
engine = `window.ESOEngine = (function () {\n${engine}\nreturn { computeSheet, validateBuild, countSetPieces, STRATEGIES, DEFAULT_STRATEGIES, CLASS_LINES, TWO_HANDED };\n})();`;

function slimEffect(e) {
  const o = { ...e };
  delete o.raw;
  return o;
}
const slim = {
  _meta: effects._meta,
  sets: Object.fromEntries(Object.entries(effects.sets).map(([k, s]) => [k, {
    ...s,
    tags: undefined,
    bonuses: Object.fromEntries(Object.entries(s.bonuses).map(([n, b]) => [n, { raw: b.raw, kind: b.kind, effects: b.effects.map(slimEffect), perfected: b.perfected ? { pieces: b.perfected.pieces, raw: b.perfected.raw, effects: b.perfected.effects.map(slimEffect) } : undefined }])),
  }])),
  skills: {
    passives: Object.fromEntries(Object.entries(effects.skills.passives).map(([k, p]) => [k, { name: p.name, line: p.line, group: p.group, class: p.class, aliases: p.aliases, raw: p.raw, effects: p.effects.map(slimEffect) }])),
    actives: Object.fromEntries(Object.entries(effects.skills.actives).map(([k, a]) => [k, { ...a, whileSlotted: a.whileSlotted.map(slimEffect) }])),
    lines: effects.skills.lines,
  },
  championStars: Object.fromEntries(Object.entries(effects.championStars).map(([k, s]) => [k, { ...s, effects: s.effects.map(slimEffect) }])),
  buffs: Object.fromEntries(Object.entries(effects.buffs).map(([k, b]) => [k, { name: b.name, raw: b.raw, effects: b.effects.map(slimEffect) }])),
  scribing: effects.scribing,
};

const LS = String.fromCharCode(0x2028); const PS = String.fromCharCode(0x2029);
const safe = (obj) => JSON.stringify(obj).split('</').join('<\\/').split(LS).join('\\u2028').split(PS).join('\\u2029');
const data = `window.ESO_DATA = { constants: ${safe(constants)}, effects: ${safe(slim)} };`;

const out = template.replace('/*__ENGINE__*/', () => engine).replace('/*__DATA__*/', () => data).replace('__BUILD_DATE__', new Date().toISOString().slice(0, 10));
const dest = join(ROOT, 'app', 'index.html');
writeFileSync(dest, out);
console.log(`wrote ${dest} (${Math.round(statSync(dest).size / 1024)} KB)`);
