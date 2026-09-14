#!/usr/bin/env node
/*
 * tools/parse_effects: build engine/data/effects.json from data/reference.
 *
 *   node tools/parse_effects/index.js [--report]
 *
 * Reads sets.csv, skills.csv and engine/data/constants.json (Champion stars,
 * named buffs) and writes structured effects plus a coverage report.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { parseCsv, csvObjects } from './csv.js';
import { parseText, mergeCond } from './grammar.js';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..');
const REF = join(ROOT, 'data', 'reference');
const OUT = join(ROOT, 'engine', 'data', 'effects.json');
const constants = JSON.parse(readFileSync(join(ROOT, 'engine', 'data', 'constants.json'), 'utf8'));

const P = 'Online Skill Summary.';
const stripName = (page) => page.replace(/^Online:/, '').replace(/\s*\((?:set|skill)\)$/, '');

// ------------------------------------------------------------------ groups
export const CLASS_LINES = {
  Dragonknight: ['Ardent Flame', 'Draconic Power', 'Earthen Heart'],
  Sorcerer: ['Dark Magic', 'Daedric Summoning', 'Storm Calling'],
  Nightblade: ['Assassination', 'Shadow', 'Siphoning'],
  Templar: ['Aedric Spear', "Dawn's Wrath", 'Restoring Light'],
  Warden: ['Animal Companions', 'Green Balance', "Winter's Embrace"],
  Necromancer: ['Grave Lord', 'Bone Tyrant', 'Living Death'],
  Arcanist: ['Herald of the Tome', 'Soldier of Apocrypha', 'Curative Runeforms'],
};
const LINE_GROUP = {};
for (const [cls, lines] of Object.entries(CLASS_LINES)) for (const l of lines) LINE_GROUP[l] = { group: 'Class', class: cls };
for (const l of ['Two Handed', 'One Hand and Shield', 'Dual Wield', 'Bow', 'Destruction Staff', 'Restoration Staff']) LINE_GROUP[l] = { group: 'Weapon' };
for (const l of ['Light Armor', 'Medium Armor', 'Heavy Armor']) LINE_GROUP[l] = { group: 'Armor' };
for (const l of ['Vampire', 'Werewolf', 'Soul Magic']) LINE_GROUP[l] = { group: 'World' };
for (const l of ['Fighters Guild', 'Mages Guild', 'Psijic Order', 'Undaunted']) LINE_GROUP[l] = { group: 'Guild' };
for (const l of ['Assault', 'Support']) LINE_GROUP[l] = { group: 'Alliance War' };
for (const l of ['Argonian', 'Breton', 'Dark Elf', 'High Elf', 'Imperial', 'Khajiit', 'Nord', 'Orc', 'Redguard', 'Wood Elf']) LINE_GROUP[l] = { group: 'Racial' };
LINE_GROUP['Class Mastery'] = { group: 'Class Mastery' };

// Class Mastery passives belong to a class; recover it from the icon prefix (e.g. "Green Balance-Emerald Moss").
function classFromIcon(icon) {
  const line = (icon || '').split('-')[0];
  for (const [cls, lines] of Object.entries(CLASS_LINES)) if (lines.includes(line)) return cls;
  return null;
}
const MASTERY_CLASS = { 'Above and Beyond': 'Nightblade', 'An Eye for Exploitation': 'Nightblade', 'Cutthroat\'s Focus': 'Nightblade', 'Nocturnal Inspiration': 'Nightblade', 'Share the Spoils': 'Nightblade',
  'Abyssal Emergence': 'Arcanist', 'Erudite\'s Rigor': 'Arcanist', 'Fate Realigned': 'Arcanist', 'Ink-Scribe\'s Verve': 'Arcanist', 'Unbound Potential': 'Arcanist',
  'Bastion of Light': 'Templar', 'Bright Harbinger': 'Templar', 'Devout Guardian': 'Templar', 'Judgment\'s Brand': 'Templar', 'Steadfast Candescence': 'Templar',
  'Booming Voice': 'Dragonknight', 'Inexorable Descent': 'Dragonknight', 'Lead from the Front': 'Dragonknight', 'Resolute Defense': 'Dragonknight', 'Wildfire Embers': 'Dragonknight',
  'Bountiful Harvest': 'Warden', 'Glacial Obstinance': 'Warden', 'Green-Keeper\'s Hide': 'Warden', 'Tundra\'s Maw': 'Warden', 'Wild Adaptation': 'Warden',
  'Calculated Defense': 'Sorcerer', 'Conservation of Energy': 'Sorcerer', 'Font of Power': 'Sorcerer', 'Sphere of Influence': 'Sorcerer', 'Static Reverberation': 'Sorcerer',
  'Cycle Unending': 'Necromancer', 'Malevolent Promise': 'Necromancer', 'Nothing Wasted': 'Necromancer', 'Pound of Flesh': 'Necromancer', 'Veil\'s Forfeit': 'Necromancer' };

// ------------------------------------------------------------------ sets
const MYTHIC_SLOT_WORDS = [
  [/\b(ring|band)\b/i, 'ring'], [/\b(amulet|necklace|torc|pendant|chain|fete|pearls|coil)\b/i, 'necklace'],
  [/\b(belt|sash|girdle)\b/i, 'waist'], [/\b(kilt|greaves|breeches|leggings)\b/i, 'legs'],
  [/\b(treaders|sabatons|boots|shoes|striders)\b/i, 'feet'], [/\b(stranglers|gloves|gauntlets|steamguards|bracers|hands)\b/i, 'hands'],
  [/\b(vestments|embrace|cuirass|cladding|robe|jerkin|hauberk)\b/i, 'chest'], [/\b(gaze|visage|helm|mask|crown|hood|hat)\b/i, 'head'],
  [/\b(spaulder|whispers|pauldron|shoulder)\b/i, 'shoulders'],
];
const MYTHIC_SLOT_OVERRIDE = { "Sea-Serpent's Coil": 'waist', 'Death Dealer\'s Fete': 'necklace', 'The Saint and the Seducer': 'chest', 'Faun\'s Lark Cladding': 'chest', 'Shapeshifter\'s Chain': 'necklace', 'Syrabane\'s Ward': 'shoulders', 'Esoteric Environment Greaves': 'legs', "Huntsman's Warmask": 'head', "The Shadow Queen's Cowl": 'head', "Prowler's Talisman": 'necklace', 'Shattered Paths Signet': 'ring', 'Monomyth Reforged': 'ring',
  // slots supplied by the user from in game tooltips (Update 50 sets.csv has no slot word in the name)
  "Rakkhat's Voidmantle": 'shoulders', "Stormweaver's Cavort": 'legs' };
// sets.csv dropped the leading stat line of some tooltips. Text here is the full in game tooltip as supplied by the user.
const BONUS_TEXT_OVERRIDE = {
  "Stormweaver's Cavort": { 1: 'Adds 300 Magicka Recovery. Sprint, Roll Dodge, Bash, Break Free, Sneak, and Block now consume Magicka instead of Stamina. You reduce your Magicka Recovery to 0 while Blocking, Sneaking, or Sprinting. You no longer reduce your Stamina Recovery to 0 while Blocking, Sneaking or Sprinting.' },
};

function buildSets() {
  const rows = csvObjects(readFileSync(join(REF, 'sets.csv'), 'utf8'));
  const sets = {};
  const stats = { sets: 0, bonuses: 0, byStatus: {} };
  for (const r of rows) {
    const bonusIdx = [];
    for (let i = 1; i <= 12; i += 1) if ((r[`bonus_${i}`] || '').trim()) bonusIdx.push(i);
    if (!bonusIdx.length) continue;
    const name = stripName(r.page);
    const settype = r['ESO Sets With.settype'] || '';
    const mythic = r['ESO Quality Color.2'] === 'Mythic';
    const tags = [];
    for (const [k, v] of Object.entries(r)) if (/^ESO Sets With\.\d+$/.test(k) && v) tags.push(v);
    const meta = {
      name, settype, mythic,
      monster: settype === 'Monster Helm Sets',
      weaponSet: settype === 'Weapon',
      maxPieces: mythic ? 1 : Math.max(...bonusIdx),
      source: r['ESO Sets With.source'] || '',
      dlc: r['ESO Sets With.dlc'] || r['Mod Header.1'] || '',
      tags,
      bonuses: {},
    };
    if (mythic) {
      meta.mythicSlot = MYTHIC_SLOT_OVERRIDE[name] || null;
      if (!meta.mythicSlot) for (const [re, slot] of MYTHIC_SLOT_WORDS) if (re.test(name)) { meta.mythicSlot = slot; break; }
      if (!meta.mythicSlot && settype === 'Jewelry') meta.mythicSlot = 'jewelry';
    }
    if (meta.weaponSet) {
      meta.weaponTypes = tags.filter((t) => /Staff|Bow|Two Handed|Dual Wield|One Hand and Shield|Shield|Greatsword|Battle Axe|Maul|Axe|Sword|Dagger|Mace/i.test(t));
    }
    for (const i of bonusIdx) {
      const raw = ((BONUS_TEXT_OVERRIDE[name] || {})[i] || r[`bonus_${i}`]).trim();
      const b = parseBonus(raw, i, meta);
      meta.bonuses[String(i)] = b;
      stats.bonuses += 1;
      stats.byStatus[b.status] = (stats.byStatus[b.status] || 0) + 1;
    }
    sets[name] = meta;
    stats.sets += 1;
  }
  return { sets, stats };
}

function parseBonus(raw, pieces, meta) {
  // Perfected trial sets fold the 5 piece perfected bonus into the 4 piece cell: "Adds X 5 perfected items: Adds Y"
  let text = raw;
  let perfectedExtra = null;
  const m = raw.match(/^(.*?)\s+(\d+) perfected items:\s*(.*)$/i);
  if (m) { text = m[1]; perfectedExtra = { pieces: Number(m[2]), text: m[3] }; }
  const parsed = parseText(text);
  const kindOfBonus = parsed.status === 'ok' ? 'stat' : parsed.status === 'proc' ? 'proc' : parsed.status;
  const out = { raw, status: parsed.status, kind: kindOfBonus, effects: parsed.effects.map(cleanEffect) };
  if (perfectedExtra) {
    const p2 = parseText(perfectedExtra.text);
    out.perfected = { pieces: perfectedExtra.pieces, raw: perfectedExtra.text, status: p2.status, effects: p2.effects.map(cleanEffect) };
  }
  return out;
}

function cleanEffect(e) {
  const o = {};
  if (e.buff) o.buff = e.buff;
  if (e.stat) { o.stat = e.stat; o.value = e.value; o.kind = e.kind; }
  if (!e.stat && !e.buff) o.kind = e.kind;
  o.condition = e.condition || null;
  o.raw = e.raw;
  return o;
}

// ------------------------------------------------------------------ skills
function buildSkills() {
  const rows = csvObjects(readFileSync(join(REF, 'skills.csv'), 'utf8'));
  const passives = {};
  const actives = {};
  const lines = {};
  const stats = { passives: 0, byStatus: {}, actives: 0, slottedNodes: 0 };
  const seenIds = new Map();
  for (const r of rows) {
    const type = r[`${P}type`];
    const line = r[`${P}line`];
    const grp = LINE_GROUP[line];
    if (!grp) continue;
    const name = stripName(r.page);
    if (!lines[line]) lines[line] = { name: line, group: grp.group, class: grp.class || null, passives: [], actives: [] };
    if (type === 'Passive') {
      const id = r[`${P}id`];
      const desc = [r[`${P}desc3`], r[`${P}desc2`], r[`${P}desc`]].find((x) => x && x.trim()) || '';
      if (id && seenIds.has(id)) {
        // same skill under an older or newer name (skill lines were renamed): keep one entry, record the alias
        const primary = seenIds.get(id);
        passives[primary].aliases.push(name);
        continue;
      }
      if (id) seenIds.set(id, name);
      const parsed = parseText(desc);
      const cls = grp.class || (line === 'Class Mastery' ? (MASTERY_CLASS[name] || classFromIcon(r[`${P}icon`])) : null);
      passives[name] = { name, line, group: grp.group, class: cls, aliases: [], raw: desc, status: parsed.status, effects: parsed.effects.map(cleanEffect), prefixConditions: parsed.prefixConditions };
      lines[line].passives.push(name);
      stats.passives += 1;
      stats.byStatus[parsed.status] = (stats.byStatus[parsed.status] || 0) + 1;
    } else if (type === '' || type === 'Ultimate') {
      if (!line) continue;
      const ultimate = type === 'Ultimate';
      const nodes = [
        { name, morphOf: null, desc: r[`${P}desc`] },
        { name: r[`${P}morph1name`], morphOf: name, desc: r[`${P}desc1`] },
        { name: r[`${P}morph2name`], morphOf: name, desc: r[`${P}desc2`] },
      ].filter((n) => n.name);
      const entry = { base: name, morphs: nodes.slice(1).map((n) => n.name), ultimate };
      lines[line].actives.push(entry);
      for (const n of nodes) {
        const parsed = parseText(n.desc || '');
        // keep only effects gated on this ability being slotted
        const whileSlotted = parsed.effects.filter((e) => hasSelfSlot(e.condition)).map((e) => ({ ...cleanEffect(e), condition: replaceSelf(e.condition, n.name) }));
        actives[n.name] = { name: n.name, line, group: grp.group, class: grp.class || null, base: name, morph: n.morphOf ? true : false, ultimate, whileSlotted };
        stats.actives += 1;
        if (whileSlotted.length) stats.slottedNodes += 1;
      }
    }
  }
  return { passives, actives, lines, stats };
}
function hasSelfSlot(c) {
  if (!c) return false;
  if (c.type === 'slotted' && c.ability === '$self') return true;
  if (c.type === 'all') return c.of.some(hasSelfSlot);
  return false;
}
function replaceSelf(c, name) {
  if (!c) return c;
  if (c.type === 'all') return { type: 'all', of: c.of.map((x) => replaceSelf(x, name)) };
  if (c.type === 'slotted' && c.ability === '$self') return { type: 'slotted', ability: name };
  return c;
}

// ------------------------------------------------------------------ scribing
// Grimoire to skill line. Scripts act on cast and have no sheet effect in phase 1; the
// selection is kept so a build is complete. Focus names come from the esolog table,
// affix scripts from the UESP Buffs page. See UNKNOWNS.md for what is missing.
const GRIMOIRES = {
  'Banner Bearer': 'Support', 'Elemental Explosion': 'Destruction Staff', "Mender's Bond": 'Restoration Staff',
  'Shield Throw': 'One Hand and Shield', 'Smash': 'Two Handed', 'Soul Burst': 'Soul Magic', 'Torchbearer': 'Fighters Guild',
  'Trample': 'Assault', 'Traveling Knife': 'Dual Wield', "Ulfsild's Contingency": 'Mages Guild', 'Vault': 'Bow', 'Wield Soul': 'Soul Magic',
};
// The script catalog (focus, signature, affix, and which grimoires take each) is extracted from
// the UESP Online:Scribing page by tools/extract_scribing_pdf.py into data/reference/scribing_scripts.json.
// The UESP Buffs and Debuffs pages add the Major or Minor tier an affix grants on a given grimoire.
const SCRIPTS = JSON.parse(readFileSync(join(REF, 'scribing_scripts.json'), 'utf8'));
function buildScribing() {
  const tier = {};
  for (const table of ['uesp_Online_Buffs_t00.csv', 'uesp_Online_Buffs_t01.csv']) {
    let t = null;
    for (const row of parseCsv(readFileSync(join(REF, 'tables', table), 'utf8'))) {
      const c0 = (row[0] || '').trim(); const c1 = (row[1] || '').trim();
      if (c0 === 'Major' || c0 === 'Minor') t = c0;
      else if (/\[ edit \]/.test(c0)) t = (c1 === 'Major' || c1 === 'Minor') ? c1 : null;
      const i = row.indexOf('Scribing');
      if (i < 0 || !row[i + 1] || !t) continue;
      const m = row[i + 1].match(/^(.+?) on (.+)$/);
      if (!m) continue;
      for (const g of m[2].split(',').map((x) => x.trim())) if (GRIMOIRES[g]) (tier[g] = tier[g] || {})[m[1].trim()] = t;
    }
  }
  const perGrimoire = (section) => {
    const out = {};
    for (const [script, v] of Object.entries(SCRIPTS[section])) for (const g of (v.grimoires || v)) (out[g] = out[g] || []).push(script);
    return out;
  };
  const focus = perGrimoire('focus'); const signature = perGrimoire('signature'); const affix = perGrimoire('affix');
  const out = {};
  for (const [g, line] of Object.entries(GRIMOIRES)) {
    out[g] = {
      name: g, line,
      focus: (focus[g] || []).slice().sort(),
      signature: (signature[g] || []).slice().sort(),
      affix: (affix[g] || []).map((a) => ((tier[g] || {})[a] ? `${tier[g][a]} ${a}` : a)).sort(),
    };
  }
  out._meta = {
    source: SCRIPTS._meta.source,
    aliases: SCRIPTS._meta.aliases,
    signatureDescriptions: Object.fromEntries(Object.entries(SCRIPTS.signature).map(([n, v]) => [n, v.description])),
  };
  return out;
}

// ------------------------------------------------------------------ champion stars and buffs
function buildStars() {
  const stars = {};
  const stats = { stars: 0, byStatus: {} };
  for (const s of constants.championPoints.stars) {
    const parsed = parseText(s.effect);
    const effects = parsed.effects.map(cleanEffect).map((e) => {
      if (e.stat && hasPerStage(e.condition)) return { ...e, value: round3(e.value * s.stages), condition: dropPerStage(e.condition) };
      if (e.stat && /per stage/i.test(e.raw)) return { ...e, value: round3(e.value * s.stages) };
      return e;
    });
    stars[s.name] = { name: s.name, constellation: s.constellation, slottable: s.slottable, stages: s.stages, costPerStage: s.costPerStage, raw: s.effect, status: parsed.status, effects };
    stats.stars += 1;
    stats.byStatus[parsed.status] = (stats.byStatus[parsed.status] || 0) + 1;
  }
  return { stars, stats };
}
function hasPerStage(c) { return !!c && (c.type === 'perStage' || (c.type === 'all' && c.of.some(hasPerStage))); }
function dropPerStage(c) {
  if (!c) return null;
  if (c.type === 'perStage') return null;
  if (c.type === 'all') { const of = c.of.filter((x) => x.type !== 'perStage'); return of.length === 0 ? null : of.length === 1 ? of[0] : { type: 'all', of }; }
  return c;
}
function round3(x) { return Math.round(x * 1000) / 1000; }

function buildBuffs() {
  const buffs = {};
  const stats = { buffs: 0, byStatus: {} };
  for (const [name, b] of Object.entries(constants.namedBuffs.buffs)) {
    const parsed = parseText(b.description);
    buffs[name] = { name, raw: b.description, status: parsed.status, effects: parsed.effects.map(cleanEffect) };
    stats.buffs += 1;
    stats.byStatus[parsed.status] = (stats.byStatus[parsed.status] || 0) + 1;
  }
  return { buffs, stats };
}

// ------------------------------------------------------------------ main
export function build() {
  const S = buildSets();
  const K = buildSkills();
  const SC = buildScribing();
  // grimoires are slottable abilities of their skill line with no while slotted effects
  for (const [g, meta] of Object.entries(SC)) {
    if (g.startsWith('_')) continue;
    K.actives[g] = { name: g, line: meta.line, group: 'Scribing', class: null, base: g, morph: false, ultimate: false, scribing: true, whileSlotted: [] };
    if (K.lines[meta.line]) K.lines[meta.line].actives.push({ base: g, morphs: [], ultimate: false, scribing: true });
  }
  // slotted conditions name a skill line in prose ("Animal Companion ability"); map them onto the real line names
  const lineNames = Object.keys(K.lines);
  const canonLine = (name) => {
    if (K.lines[name]) return name;
    const low = name.toLowerCase();
    return lineNames.find((l) => l.toLowerCase() === low || l.toLowerCase() === low + 's' || l.toLowerCase() === low + ' magic') || name;
  };
  const fixCond = (c) => {
    if (!c) return;
    if (c.type === 'slotted' && c.line) c.line = canonLine(c.line);
    if (c.type === 'all' && Array.isArray(c.of)) c.of.forEach(fixCond);
  };
  for (const p of Object.values(K.passives)) for (const e of p.effects) fixCond(e.condition);
  for (const a of Object.values(K.actives)) for (const e of a.whileSlotted || []) fixCond(e.condition);
  const C = buildStars();
  const B = buildBuffs();
  const pct = (n, d) => (d ? Math.round((n / d) * 1000) / 10 : 0);
  const covered = (by) => Object.entries(by).filter(([k]) => k !== 'unparsed' && k !== 'partial').reduce((a, [, v]) => a + v, 0);
  const coverage = {
    setBonuses: { total: S.stats.bonuses, byStatus: S.stats.byStatus, parsedPercent: pct(covered(S.stats.byStatus), S.stats.bonuses) },
    passives: { total: K.stats.passives, byStatus: K.stats.byStatus, parsedPercent: pct(covered(K.stats.byStatus), K.stats.passives) },
    championStars: { total: C.stats.stars, byStatus: C.stats.byStatus, parsedPercent: pct(covered(C.stats.byStatus), C.stats.stars) },
    namedBuffs: { total: B.stats.buffs, byStatus: B.stats.byStatus, parsedPercent: pct(covered(B.stats.byStatus), B.stats.buffs) },
    activeNodes: { total: K.stats.actives, withWhileSlotted: K.stats.slottedNodes },
    note: 'parsedPercent counts a text as covered when every sentence was understood: as a sheet effect, a named buff, a combat or target proc (kept as kind proc), or flavor. partial and unparsed count against coverage.',
  };
  const out = {
    _meta: { generatedBy: 'tools/parse_effects/index.js', sources: ['data/reference/sets.csv', 'data/reference/skills.csv', 'data/reference/scribing_scripts.json', 'engine/data/constants.json'], coverage },
    sets: S.sets,
    skills: { passives: K.passives, actives: K.actives, lines: K.lines },
    championStars: C.stars,
    buffs: B.buffs,
    scribing: SC,
  };
  return out;
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMain) {
  const out = build();
  writeFileSync(OUT, JSON.stringify(out, null, 1) + '\n');
  const c = out._meta.coverage;
  console.log(`wrote ${OUT}`);
  for (const k of ['setBonuses', 'passives', 'championStars', 'namedBuffs']) console.log(`  ${k}: ${c[k].parsedPercent}% of ${c[k].total}  ${JSON.stringify(c[k].byStatus)}`);
  console.log(`  active nodes: ${c.activeNodes.total}, with while slotted effects: ${c.activeNodes.withWhileSlotted}`);
  if (process.argv.includes('--report')) {
    const gaps = [];
    for (const s of Object.values(out.sets)) for (const [n, b] of Object.entries(s.bonuses)) if (b.status === 'unparsed' || b.status === 'partial') gaps.push(`SET ${s.name} (${n}) [${b.status}]: ${b.raw}`);
    for (const p of Object.values(out.skills.passives)) if (p.status === 'unparsed' || p.status === 'partial') gaps.push(`PASSIVE ${p.name} [${p.line}] [${p.status}]: ${p.raw}`);
    for (const s of Object.values(out.championStars)) if (s.status === 'unparsed' || s.status === 'partial') gaps.push(`CP ${s.name} [${s.status}]: ${s.raw}`);
    for (const b of Object.values(out.buffs)) if (b.status === 'unparsed' || b.status === 'partial') gaps.push(`BUFF ${b.name} [${b.status}]: ${b.raw}`);
    console.log('\nGAPS:\n' + gaps.join('\n'));
  }
}
