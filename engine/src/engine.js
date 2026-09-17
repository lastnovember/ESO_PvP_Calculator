/*
 * ESO PvP Calculator, phase 1 engine: character sheet.
 *
 * Pure ES module, no dependencies, no I/O. computeSheet(build, data) returns
 * both in game panels (main sheet and Advanced Stats) for both weapon bars.
 *
 * data = { constants, effects }  (engine/data/constants.json, engine/data/effects.json)
 *
 * ORDER OF OPERATIONS (per bar)
 * ------------------------------
 *  1. Collect every active effect source for the bar:
 *       racial passives, class passives (the three class skill lines, or the
 *       subclassing lines), armor passives scaled by piece count, weapon
 *       passives gated by the weapons on this bar, guild and Alliance War
 *       passives, Vampire and Werewolf passives, Champion stars, set bonuses
 *       by piece count on this bar, item traits and glyphs, mundus (scaled by
 *       Divines), food, "while slotted" effects of the abilities on this bar,
 *       Battle Spirit.
 *  2. Evaluate conditions. Effects whose condition needs a target or combat
 *       state are dropped (kind "proc" or unsupported condition). Battle
 *       Spirit conditions read build.battleSpirit. "While slotted" reads the
 *       bar. Per piece effects are multiplied by the piece count.
 *  3. Sum flat contributions and percent contributions per stat, separately.
 *       Every percent source of one stat adds into one bucket (additive
 *       stacking). Named buffs of the same name do not stack: the largest
 *       Major and the largest Minor of a family apply.
 *  4. Combine:  value = (base + flat) * (1 + percent / 100)
 *       Max resources: base + attribute points + flats (sets, glyphs, traits,
 *         food, mundus, racial, CP) then times the percent bucket.
 *       Recoveries: same shape. Battle Spirit Health Recovery and the vampire
 *         stage penalty are multiplied in after (STRATEGIES.recoveryPenalties).
 *       Weapon and Spell Damage: base + weapon rating + flats, times percent.
 *       Critical Chance: base percent + rating / critRatingPerPercent + percent.
 *       Critical Damage: base percent + percents, capped.
 *       Resistances: item armor (with Reinforced) + flats, then percent,
 *         then displayed with mitigation min(res, cap) / resistancePerPercent.
 *       Penetration: flats only.
 *       Costs: (base - flat reductions) * (1 + percent) by default
 *         (STRATEGIES.costOrder).
 *       Block mitigation: base * (1 + percent) (STRATEGIES.blockMitigation).
 *       Movement speed: 100 + percents, capped at 200.
 *  5. Flat sources that apply after multiplication: the unverified Battle
 *       Spirit flat Max Health, off by default (flags.battleSpiritFlatHealth).
 *
 * Every uncertain ordering is a named entry in STRATEGIES with the choices it
 * accepts, so a fixture can be replayed under each choice.
 */

export const STRATEGIES = {
  // How percent Max Health/Magicka/Stamina bonuses treat food and glyph flats.
  // 'all': percent multiplies every flat source (default).
  // 'excludeFood': food is added after the multiplication.
  maxStatPercentBase: ['all', 'excludeFood'],
  // Battle Spirit -50% Health Recovery and vampire stage recovery penalty.
  // 'multiplicative': applied after the additive percent bucket (default).
  // 'additive': added into the percent bucket.
  recoveryPenalties: ['multiplicative', 'additive'],
  // Cost reductions. 'flatThenPercent': (base - flat) * (1 - pct) (default).
  // 'percentThenFlat': base * (1 - pct) - flat.
  costOrder: ['flatThenPercent', 'percentThenFlat'],
  // Block mitigation bonuses. 'multiplicative': 50 * (1 + pct) (default).
  // 'additive': 50 + pct.
  blockMitigation: ['multiplicative', 'additive'],
  // Battle Spirit healing taken and damage taken. 'multiplicative' (default)
  // or 'additive' into the percent bucket.
  battleSpiritPercents: ['multiplicative', 'additive'],
  // Dual wield off hand weapon rating contribution.
  // 'passiveOnly': only through the Dual Wield Expert passive (default).
  // 'full': off hand rating added like the main hand.
  offHandRating: ['passiveOnly', 'full'],
  // Precise trait. 'rating': percent * critRatingPerPercent (default).
  // 'percent': added as a percent.
  preciseTrait: ['rating', 'percent'],
  // Effects that state a different value "against targets with Battle Spirit".
  // 'sheet': the sheet shows the unreduced value (default).
  // 'pvpTarget': use the reduced value whenever build.battleSpirit is on.
  battleSpiritTargetValues: ['sheet', 'pvpTarget'],
  // Cost percent reductions: armor passives add up, a weapon passive (Ice Staff block cost) multiplies on top.
  // Fixtures 001 and 002: (1750 - 40) x 0.91 = 1556 on maces, x 0.64 more = 996 on the ice staff.
  costWeaponPercent: ['multiplicative', 'additive'],
};

export const DEFAULT_STRATEGIES = Object.fromEntries(
  Object.entries(STRATEGIES).map(([k, v]) => [k, v[0]]),
);

// Stats that share one bucket under an alias.
const STAT_ALIASES = {
  weaponAndSpellDamage: ['weaponDamage', 'spellDamage'],
  critRating: ['weaponCritRating', 'spellCritRating'],
  armor: ['physicalResistance', 'spellResistance'],
  physicalAndSpellResistance: ['physicalResistance', 'spellResistance'],
  offensivePenetration: ['physicalPenetration', 'spellPenetration'],
  physicalAndSpellPenetration: ['physicalPenetration', 'spellPenetration'],
  allRecovery: ['healthRecovery', 'magickaRecovery', 'staminaRecovery'],
  allMax: ['maxHealth', 'maxMagicka', 'maxStamina'],
  sprintAndRollDodgeCost: ['sprintCost', 'rollDodgeCost'],
  abilityCost: ['magickaCost', 'staminaCost'],
  critDamageAndHealing: ['critDamage', 'critHealing'],
  damageAndHealingDone: ['damageDone', 'healingDone'],
};

export const TWO_HANDED = new Set(['greatsword', 'battle axe', 'maul', 'bow', 'inferno staff', 'lightning staff', 'ice staff', 'restoration staff']);
const STAVES = new Set(['inferno staff', 'lightning staff', 'ice staff']);
const ARMOR_SLOTS = ['head', 'shoulders', 'chest', 'hands', 'waist', 'legs', 'feet'];
const JEWELRY_SLOTS = ['necklace', 'ring1', 'ring2'];
const LARGE_GLYPH_SLOTS = new Set(['head', 'chest', 'legs', 'shield']);

export const CLASS_LINES = {
  Dragonknight: ['Ardent Flame', 'Draconic Power', 'Earthen Heart'],
  Sorcerer: ['Dark Magic', 'Daedric Summoning', 'Storm Calling'],
  Nightblade: ['Assassination', 'Shadow', 'Siphoning'],
  Templar: ['Aedric Spear', "Dawn's Wrath", 'Restoring Light'],
  Warden: ['Animal Companions', 'Green Balance', "Winter's Embrace"],
  Necromancer: ['Grave Lord', 'Bone Tyrant', 'Living Death'],
  Arcanist: ['Herald of the Tome', 'Soldier of Apocrypha', 'Curative Runeforms'],
};

const ALWAYS_LINES = ['Light Armor', 'Medium Armor', 'Heavy Armor', 'Two Handed', 'One Hand and Shield', 'Dual Wield', 'Bow', 'Destruction Staff', 'Restoration Staff', 'Fighters Guild', 'Mages Guild', 'Psijic Order', 'Undaunted', 'Assault', 'Support', 'Soul Magic'];

// ------------------------------------------------------------ helpers

function v(entry) {
  // constants.json entries are {value, source, ...}; accept raw numbers too
  return entry && typeof entry === 'object' && 'value' in entry ? entry.value : entry;
}

function stripSetName(name) {
  return name ? name.replace(/^Online:/, '').replace(/\s*\(set\)$/, '') : name;
}

class Bucket {
  constructor() { this.flat = 0; this.percent = 0; this.weaponPercents = []; this.rows = []; this.override = null; }
  add(kind, value, source, group) {
    if (kind === 'flat') this.flat += value;
    else if (kind === 'percent') { this.percent += value; if (group === 'weapon') this.weaponPercents.push(value); }
    else if (kind === 'set') this.override = value;
    this.rows.push({ source, kind, value, ...(group ? { group } : {}) });
  }
}

class Accumulator {
  constructor() { this.buckets = new Map(); this.named = new Map(); this.dropped = []; }
  bucket(stat) {
    if (!this.buckets.has(stat)) this.buckets.set(stat, new Bucket());
    return this.buckets.get(stat);
  }
  add(stat, kind, value, source, group) {
    const targets = STAT_ALIASES[stat] || [stat];
    for (const t of targets) {
      const b = this.bucket(t); b.add(kind, value, source, group);
      // A flat added to Spell Resistance alone (Spell Warding) is not armor: armor percents leave it out (fixture 005)
      if (stat === 'spellResistance' && kind === 'flat') b.rows[b.rows.length - 1].spellOnly = true;
    }
  }
  weaponPercents(stat) { return this.buckets.has(stat) ? this.buckets.get(stat).weaponPercents : []; }
  // Named buffs (Major Resolve etc.) do not stack with themselves.
  addNamed(name, effects, source) {
    if (this.named.has(name)) { this.dropped.push({ source, reason: `${name} already active from ${this.named.get(name)}` }); return; }
    this.named.set(name, source);
    for (const e of effects) this.add(e.stat, e.kind, e.value, `${source} (${name})`);
  }
  flat(stat) { return this.buckets.has(stat) ? this.buckets.get(stat).flat : 0; }
  override(stat) { return this.buckets.has(stat) ? this.buckets.get(stat).override : null; }
  pct(stat) { return this.buckets.has(stat) ? this.buckets.get(stat).percent : 0; }
  rows(stat) { return this.buckets.has(stat) ? this.buckets.get(stat).rows : []; }
}

// ------------------------------------------------------------ validation

export function validateBuild(build, data) {
  const errors = [];
  const warnings = [];
  const sets = data.effects.sets || {};
  if (!build || typeof build !== 'object') return { errors: ['build is not an object'], warnings };
  if (build.schemaVersion !== 1) errors.push('schemaVersion must be 1');
  if (!CLASS_LINES[build.class]) errors.push(`unknown class ${build.class}`);
  const a = build.attributes || {};
  const sum = (a.health || 0) + (a.magicka || 0) + (a.stamina || 0);
  if (sum > 64) errors.push(`attribute points exceed 64: ${sum}`);
  if (build.classSkillLines) {
    if (build.classSkillLines.length !== 3) errors.push('classSkillLines must hold exactly 3 lines');
    const all = new Set(Object.values(CLASS_LINES).flat());
    for (const l of build.classSkillLines) if (!all.has(l)) errors.push(`unknown class skill line ${l}`);
  }
  if (build.classMastery) {
    if (build.classMastery.length > 2) errors.push('classMastery: at most 2 passives (2 Class Mastery Points)');
    for (const n of build.classMastery) {
      const p = data.effects.skills.passives[n];
      if (!p || p.line !== 'Class Mastery') errors.push(`unknown Class Mastery passive ${n}`);
      else if (p.class && p.class !== build.class) errors.push(`${n} is a ${p.class} Class Mastery passive`);
    }
  }
  // CP
  const cp = build.championPoints || {};
  if (cp.enabled && cp.slotted) {
    const stars = new Map((data.constants.championPoints.stars || []).map((s) => [s.name, s]));
    for (const [constellation, list] of Object.entries(cp.slotted)) {
      if (list.length > 4) errors.push(`${constellation}: more than 4 slotted stars`);
      for (const name of list) {
        const s = stars.get(name);
        if (!s) errors.push(`unknown Champion star ${name}`);
        else if (!s.slottable) errors.push(`${name} is not slottable`);
        else if (s.constellation !== constellation) errors.push(`${name} belongs to ${s.constellation}, not ${constellation}`);
      }
    }
  }
  // bars
  if (!Array.isArray(build.bars) || build.bars.length !== 2) errors.push('bars must hold exactly two bars');
  else build.bars.forEach((bar, i) => {
    const mh = bar.mainHand; const oh = bar.offHand;
    if (mh && TWO_HANDED.has(mh.type) && oh) errors.push(`bar ${i + 1}: off hand must be empty with a two handed weapon`);
    if (mh && mh.type === 'shield') errors.push(`bar ${i + 1}: a shield cannot be in the main hand`);
    if (oh && oh.type !== 'shield' && TWO_HANDED.has(oh.type)) errors.push(`bar ${i + 1}: two handed weapon in the off hand`);
    if (!mh && oh) warnings.push(`bar ${i + 1}: off hand without a main hand`);
    if ((bar.skills || []).length > 5) errors.push(`bar ${i + 1}: more than 5 skill slots`);
    const filled = (bar.skills || []).filter(Boolean);
    if (new Set(filled).size !== filled.length) errors.push(`bar ${i + 1}: the same skill in two slots`);
  });
  // sets: piece counts, mythic, slot restrictions
  const mythics = new Set();
  const counts = countSetPieces(build);
  for (const [name, info] of Object.entries(counts.all)) {
    const meta = sets[name];
    if (!meta) { errors.push(`unknown set ${name}`); continue; }
    if (meta.mythic) mythics.add(name);
    if (info.total > meta.maxPieces) errors.push(`${name}: ${info.total} pieces equipped, set has ${meta.maxPieces}`);
    for (const slot of info.slots) {
      const cat = slotCategory(slot, build);
      if (meta.monster && !(slot === 'head' || slot === 'shoulders')) errors.push(`${name} is a monster set and cannot go on ${slot}`);
      if (meta.weaponSet && cat !== 'weapon') errors.push(`${name} is a weapon set and cannot go on ${slot}`);
      if (meta.settype === 'Jewelry' && cat !== 'jewelry') errors.push(`${name} is jewelry only and cannot go on ${slot}`);
      if (meta.mythic && meta.mythicSlot) {
        const ms = meta.mythicSlot;
        const ok = ms === slot || ms === cat || (ms === 'ring' && /^ring/.test(slot)) || (ms === 'weapon' && cat === 'weapon');
        if (!ok) errors.push(`${name} goes on ${ms}, not ${slot}`);
      }
    }
  }
  if (mythics.size > 1) errors.push(`more than one mythic equipped: ${[...mythics].join(', ')}`);
  for (const name of mythics) if (counts.all[name].total > 1) errors.push(`${name}: a mythic is one piece`);
  return { errors, warnings };
}

function slotCategory(slot, build) {
  if (ARMOR_SLOTS.includes(slot)) return 'armor';
  if (JEWELRY_SLOTS.includes(slot)) return 'jewelry';
  return 'weapon';
}

// Pieces per set, per bar. Weapons only count on their bar. Two handed = 2.
// Perfected and non perfected pieces of a trial or arena set count together for the set's bonuses; the
// perfected extra needs the full count of perfected pieces (data/patch-notes/html 103 (2021-06-08): "you can
// now wear perfected and non-perfected sets in combination with each other. Doing so will grant the bonuses
// associated with the non-perfected set until you wear all 5 pieces of perfected."). Pieces are counted under
// the base name; `perfected` says how many of them are the perfected version.
export const PERFECTED_PREFIX = 'Perfected ';
export function baseSetName(name) {
  const n = stripSetName(name);
  return n && n.startsWith(PERFECTED_PREFIX) ? n.slice(PERFECTED_PREFIX.length) : n;
}
export function countSetPieces(build) {
  const body = {};
  const addPiece = (target, rawName, slot, n = 1) => {
    const stripped = stripSetName(rawName);
    if (!stripped) return;
    const name = baseSetName(stripped);
    if (!target[name]) target[name] = { total: 0, slots: [], perfected: 0 };
    target[name].total += n; target[name].slots.push(slot);
    if (stripped !== name) target[name].perfected += n;
  };
  for (const slot of [...ARMOR_SLOTS, ...JEWELRY_SLOTS]) {
    const item = build.gear && build.gear[slot];
    if (item && item.set) addPiece(body, item.set, slot);
  }
  const perBar = (build.bars || []).map((bar, i) => {
    const t = JSON.parse(JSON.stringify(body));
    if (bar.mainHand && bar.mainHand.set) addPiece(t, bar.mainHand.set, `bar${i + 1}.mainHand`, TWO_HANDED.has(bar.mainHand.type) ? 2 : 1);
    if (bar.offHand && bar.offHand.set) addPiece(t, bar.offHand.set, `bar${i + 1}.offHand`, 1);
    return t;
  });
  // 'all' = max over bars, for validation of the whole build
  const all = {};
  for (const t of perBar) for (const [k, info] of Object.entries(t)) {
    if (!all[k] || info.total > all[k].total) all[k] = info;
  }
  for (const [k, info] of Object.entries(body)) if (!all[k]) all[k] = info;
  return { body, perBar, all };
}

// ------------------------------------------------------------ context per bar

function barContext(build, barIndex, strategies) {
  const bar = build.bars[barIndex];
  const pieces = countSetPieces(build).perBar[barIndex];
  const armor = { light: 0, medium: 0, heavy: 0 };
  for (const slot of ARMOR_SLOTS) {
    const it = build.gear[slot];
    if (it && it.weight) armor[it.weight] += 1;
  }
  const armorTypes = Object.values(armor).filter((n) => n > 0).length;
  const mh = bar.mainHand; const oh = bar.offHand;
  const weapons = [];
  if (mh) weapons.push(mh.type);
  if (oh) weapons.push(oh.type);
  const ctx = {
    bar, barIndex, armor, armorTypes,
    twoHanded: !!(mh && ['greatsword', 'battle axe', 'maul'].includes(mh.type)),
    bow: !!(mh && mh.type === 'bow'),
    destructionStaff: !!(mh && STAVES.has(mh.type)),
    restorationStaff: !!(mh && mh.type === 'restoration staff'),
    dualWield: !!(mh && oh && oh.type !== 'shield' && !TWO_HANDED.has(mh.type)),
    shield: !!(oh && oh.type === 'shield'),
    oneHandAndShield: !!(mh && oh && oh.type === 'shield'),
    weaponTypes: weapons,
    // skills is positional (slot 1 to 5 map to buttons); null is an empty slot
    slotted: new Set([...(bar.skills || []).filter(Boolean), ...(bar.ultimate ? [bar.ultimate] : [])]),
    slottedAnyBar: new Set((build.bars || []).flatMap((b) => [...(b.skills || []).filter(Boolean), ...(b.ultimate ? [b.ultimate] : [])])),
    battleSpirit: !!build.battleSpirit,
    vampireStage: build.vampireStage || 0,
    werewolf: !!build.werewolf,
    werewolfForm: !!build.werewolfForm,
    frostStaff: !!(mh && mh.type === 'ice staff'),
    strategies,
    setsWithPieces: (min) => Object.values(pieces).filter((p) => p.total >= min).length,
  };
  return ctx;
}

// Returns a multiplier (0 = condition false, n = repeat count) or null when the
// condition needs state the engine does not have (dropped).
function evaluateCondition(cond, ctx, data) {
  if (!cond) return 1;
  switch (cond.type) {
    case 'all': {
      let m = 1;
      for (const c of cond.of) { const r = evaluateCondition(c, ctx, data); if (r === null) return null; m *= r; if (m === 0) return 0; }
      return m;
    }
    case 'battleSpirit': {
      if (cond.scope === 'target' && ctx.strategies.battleSpiritTargetValues === 'sheet') return cond.active ? 0 : 1;
      return (!!cond.active) === ctx.battleSpirit ? 1 : 0;
    }
    case 'setsWithPieces': return ctx.setsWithPieces(cond.min);
    case 'outOfCombat': return 1;
    case 'perStage': return 1;
    case 'slotted': {
      if (cond.ability) return (cond.eitherBar ? ctx.slottedAnyBar : ctx.slotted).has(cond.ability) ? 1 : 0;
      if (cond.line || cond.class) {
        // "for each Sorcerer ability slotted" counts every ability of that class, whatever its line;
        // "for each Shadow ability slotted" counts one line. The ultimate slot counts too (ctx.slotted).
        const actives = data.effects.skills.actives;
        const want = (cond.line || cond.class).toLowerCase();
        let n = 0;
        for (const name of ctx.slotted) {
          const a = actives[name];
          if (!a) continue;
          const have = cond.class ? (a.class || '') : (a.line || '');
          if (have.toLowerCase() === want || have.toLowerCase() === want + 's') n += 1;
        }
        return cond.perAbility ? n : (n > 0 ? 1 : 0);
      }
      return 0;
    }
    case 'weapon': {
      const map = { 'two handed': ctx.twoHanded, 'bow': ctx.bow, 'destruction staff': ctx.destructionStaff, 'restoration staff': ctx.restorationStaff, 'dual wield': ctx.dualWield, 'one hand and shield': ctx.oneHandAndShield, 'shield': ctx.shield, 'frost staff': ctx.frostStaff, 'shield or frost staff': ctx.shield || ctx.frostStaff };
      return map[cond.weapon] ? 1 : 0;
    }
    case 'weaponTypeCount': return ctx.weaponTypes.filter((t) => t === cond.weaponType).length;
    case 'armorPieces': return ctx.armor[cond.weight] || 0;
    case 'armorPiecesEvery2': return Math.floor((ctx.armor[cond.weight] || 0) / 2);
    case 'armorTypes': return ctx.armorTypes;
    case 'armorAtLeast': return (ctx.armor[cond.weight] || 0) >= cond.count ? 1 : 0;
    case 'werewolfForm': return ctx.werewolfForm ? 1 : 0;
    case 'vampireStage': return ctx.vampireStage >= cond.min ? 1 : 0;
    case 'always': return 1;
    default: return null; // combat, target, sneaking, bracing, sprinting...
  }
}

// ------------------------------------------------------------ effect application

function applyEffects(acc, effects, ctx, data, source, strategies) {
  for (const e of effects || []) {
    if (!e || e.kind === 'proc' || e.kind === 'unparsed') { acc.dropped.push({ source, reason: e ? e.kind : 'empty', raw: e && e.raw }); continue; }
    if (e.buff) {
      const buff = data.effects.buffs[e.buff];
      if (!buff) { acc.dropped.push({ source, reason: `unknown buff ${e.buff}` }); continue; }
      const m = evaluateCondition(e.condition, ctx, data);
      if (m === null) { acc.dropped.push({ source, reason: `condition ${e.condition.type}` }); continue; }
      if (m > 0) acc.addNamed(e.buff, buff.effects, source);
      continue;
    }
    const m = evaluateCondition(e.condition, ctx, data);
    if (m === null) { acc.dropped.push({ source, reason: `condition ${e.condition.type}`, raw: e.raw }); continue; }
    if (m === 0) continue;
    let value = e.value * m;
    if (e.cap != null) value = Math.min(value, e.cap);
    acc.add(e.stat, e.kind, value, source, hasWeaponCondition(e.condition) ? 'weapon' : (hasArmorCondition(e.condition) ? 'armor' : undefined));
  }
}

function hasArmorCondition(c) {
  if (!c) return false;
  if (c.type === 'armorPieces' || c.type === 'armorPiecesEvery2') return true;
  if (c.type === 'all') return c.of.some(hasArmorCondition);
  return false;
}

function hasWeaponCondition(c) {
  if (!c) return false;
  if (c.type === 'weapon' || c.type === 'weaponTypeCount') return true;
  if (c.type === 'all') return c.of.some(hasWeaponCondition);
  return false;
}

function activePassives(build, data) {
  const lines = new Set(ALWAYS_LINES);
  // guild, Alliance War and world lines can be switched off; other lines can be switched on
  for (const [line, on] of Object.entries(build.skillLines || {})) { if (on) lines.add(line); else lines.delete(line); }
  for (const l of (build.classSkillLines || CLASS_LINES[build.class] || [])) lines.add(l);
  lines.add(build.race);
  if ((build.vampireStage || 0) > 0) lines.add('Vampire');
  if (build.werewolf) lines.add('Werewolf');
  // Class Mastery (Update 50): five passives per class, two Class Mastery Points, hidden while subclassing.
  const native = CLASS_LINES[build.class] || [];
  const subclassing = !!(build.classSkillLines && build.classSkillLines.some((l) => !native.includes(l)));
  const mastery = new Set(subclassing ? [] : (build.classMastery || []));
  const mode = (build.passives && build.passives.mode) || 'all';
  const exclude = new Set((build.passives && build.passives.exclude) || []);
  const include = new Set((build.passives && build.passives.include) || []);
  const out = [];
  for (const [name, p] of Object.entries(data.effects.skills.passives)) {
    if (p.line === 'Class Mastery') {
      if (mastery.has(name) && p.class === build.class) out.push([name, p]);
      continue;
    }
    if (!lines.has(p.line)) continue;
    if (p.class && p.class !== build.class && !(build.classSkillLines || []).some((l) => CLASS_LINES[p.class] && CLASS_LINES[p.class].includes(l))) continue;
    const names = [name, ...(p.aliases || [])];
    const on = mode === 'all' ? !names.some((n) => exclude.has(n)) : names.some((n) => include.has(n));
    if (on) out.push([name, p]);
  }
  return out;
}

function collect(build, data, barIndex, strategies) {
  const C = data.constants; const E = data.effects;
  const ctx = barContext(build, barIndex, strategies);
  const acc = new Accumulator();
  const notes = [];

  // passives
  for (const [name, p] of activePassives(build, data)) applyEffects(acc, p.effects, ctx, data, `passive ${name}`, strategies);

  // while slotted effects: every slotted ability is offered, its condition decides (active bar, or either bar)
  for (const name of ctx.slottedAnyBar) {
    const a = E.skills.actives[name];
    if (!a) { notes.push(`unknown ability ${name}`); continue; }
    const effs = ctx.slotted.has(name) ? a.whileSlotted : (a.whileSlotted || []).filter((e) => e.condition && evaluateCondition(e.condition, ctx, data) > 0);
    applyEffects(acc, effs, ctx, data, `slotted ${name}`, strategies);
  }

  // Champion Points
  const cp = build.championPoints || {};
  if (cp.enabled) {
    const slotted = new Set(Object.values(cp.slotted || {}).flat());
    // Passive (non slottable) stars are assumed at max rank unless listed in championPoints.notTaken
    // (fixture 005: Sprint Cost 470 = 500 x 0.94 with no Sprinter, where fixture 003 read 460 = 500 - 40 with it).
    const notTaken = new Set(cp.notTaken || []);
    // championPoints.points: stages bought in a star when fewer than the maximum (fixtures 002, 005 and 007: Sneak Cost
    // 34, 55 and 94 are Sustaining Shadows at 50, 31 and 10 of its 50 stages). Effects scale by points / stages.
    const points = cp.points || {};
    for (const star of E.championStars ? Object.values(E.championStars) : []) {
      if (!(star.slottable ? slotted.has(star.name) : !notTaken.has(star.name))) continue;
      const pts = points[star.name];
      const frac = pts != null && star.stages > 0 ? Math.max(0, Math.min(1, pts / star.stages)) : 1;
      const effs = frac === 1 ? star.effects : star.effects.map((e) => (e && e.value != null && !e.buff ? { ...e, value: e.value * frac } : e));
      applyEffects(acc, effs, ctx, data, `CP ${star.name}` + (frac < 1 ? ` (${pts} of ${star.stages})` : ''), strategies);
    }
    if (slotted.has('Expert Evasion')) notes.push('Expert Evasion is slotted: the sheet shows Roll Dodge Cost 0 while the free roll is primed (fixture 005). The regular cost is shown here.');
  }

  // sets
  const pieces = countSetPieces(build).perBar[barIndex];
  const setCounts = {}; const setPerfected = {};
  for (const [name, info] of Object.entries(pieces)) {
    const meta = E.sets[name];
    if (!meta) continue;
    setCounts[name] = info.total; setPerfected[name] = info.perfected || 0;
    for (const [n, bonus] of Object.entries(meta.bonuses)) {
      if (info.total >= Number(n)) applyEffects(acc, bonus.effects, ctx, data, `set ${name} (${n})`, strategies);
    }
    // the perfected extra ("5 perfected items: Adds ...") lives on the perfected set entry and needs that many perfected pieces
    const pmeta = E.sets[PERFECTED_PREFIX + name];
    if (pmeta && info.perfected) {
      for (const bonus of Object.values(pmeta.bonuses)) {
        if (bonus.perfected && info.perfected >= bonus.perfected.pieces) applyEffects(acc, bonus.perfected.effects, ctx, data, `set ${PERFECTED_PREFIX}${name} (${bonus.perfected.pieces} perfected)`, strategies);
      }
    }
  }

  // items: armor, traits, glyphs
  let divinesPercent = 0;
  const items = [];
  for (const slot of ARMOR_SLOTS) { const it = build.gear[slot]; if (it) items.push({ slot, cat: 'armor', it }); }
  for (const slot of JEWELRY_SLOTS) { const it = build.gear[slot]; if (it) items.push({ slot, cat: 'jewelry', it }); }
  if (ctx.bar.mainHand) items.push({ slot: 'mainHand', cat: 'weapon', it: ctx.bar.mainHand });
  if (ctx.bar.offHand) items.push({ slot: ctx.bar.offHand.type === 'shield' ? 'shield' : 'offHand', cat: ctx.bar.offHand.type === 'shield' ? 'shield' : 'weapon', it: ctx.bar.offHand });

  // Item quality: read only when flags.itemQuality is on, gold otherwise. Traits come from the UESP trait table
  // columns (verified); armor and weapon ratings scale by items.qualityFactor (unverified below gold).
  const qualityOn = !!(build.flags && build.flags.itemQuality);
  const qualityOf = (it) => (qualityOn && it && C.items.qualityFactor[it.quality] ? it.quality : 'gold');
  const qf = (it) => v(C.items.qualityFactor[qualityOf(it)]);
  const tq = (t, it) => (t && t.byQuality && t.byQuality[qualityOf(it)] != null ? t.byQuality[qualityOf(it)] : t.value);
  const wq = (t, it, two) => { const q = qualityOf(it); const m = two ? t.twoHandByQuality : t.oneHandByQuality; return m && m[q] != null ? m[q] : (two ? t.twoHand : t.oneHand); };
  for (const { slot, cat, it } of items) {
    const src = `item ${slot}` + (qualityOf(it) !== 'gold' ? ` (${qualityOf(it)})` : '');
    // base armor rating
    if (cat === 'armor' || cat === 'shield') {
      let armor = (cat === 'shield' ? v(C.items.shieldArmor) : v(C.items.armor[it.weight][slot])) * qf(it);
      if (it.trait === 'Reinforced') armor *= 1 + tq(C.traits.armor.Reinforced, it) / 100;
      acc.add('armor', 'flat', Math.round(armor), `${src} armor`);
    }
    // weapon rating
    if (cat === 'weapon') {
      const rating = v(C.items.weaponDamage) * qf(it) * (it.trait === 'Nirnhoned' ? 1 + wq(C.traits.weapon.Nirnhoned, it, TWO_HANDED.has(it.type)) / 100 : 1);
      if (slot === 'mainHand') acc.add('weaponAndSpellDamage', 'flat', Math.round(rating), `${src} rating`);
      else if (strategies.offHandRating === 'full') acc.add('weaponAndSpellDamage', 'flat', Math.round(rating), `${src} rating`);
      else acc.add('offHandRating', 'flat', Math.round(rating), `${src} rating`);
    }
    // traits
    if (it.trait) {
      if (cat === 'armor' || cat === 'shield') {
        const t = C.traits.armor[it.trait];
        if (t && t.stat === 'mundusEffect') divinesPercent += tq(t, it);
        else if (t && t.stat === 'blockCost') acc.add('blockCost', 'percent', -tq(t, it), `${src} ${it.trait}`);
        else if (t && t.stat === 'sprintAndRollDodgeCost') acc.add('sprintAndRollDodgeCost', 'percent', -tq(t, it), `${src} ${it.trait}`);
        else if (t && ['critResistance', 'allRecovery', 'physicalAndSpellResistance'].includes(t.stat)) acc.add(t.stat, t.kind, tq(t, it), `${src} ${it.trait}`);
      } else if (cat === 'weapon') {
        const t = C.traits.weapon[it.trait];
        const two = TWO_HANDED.has(it.type);
        const val = wq(t, it, two);
        if (t.stat === 'critChance') {
          if (strategies.preciseTrait === 'rating') acc.add('critRating', 'flat', val * v(C.base.critRatingPerPercent), `${src} Precise`);
          else acc.add('critChancePercent', 'percent', val, `${src} Precise`);
        } else if (['physicalAndSpellResistance', 'physicalAndSpellPenetration', 'healingDone'].includes(t.stat)) {
          // Defending is not armor: Balanced Warrior's 6% leaves it out (fixtures 005 and 006, the gap between the
          // bars is exactly 6% of 3276), so the row is flagged unscaled
          acc.add(t.stat, t.kind, val, `${src} ${it.trait}`, t.stat === 'physicalAndSpellResistance' ? 'weaponTrait' : undefined);
        }
      } else if (cat === 'jewelry') {
        const t = C.traits.jewelry[it.trait];
        if (t && !['weaponAndSpellDamageVsUnder90', 'synergyRestore', 'jewelryEnchantEffect'].includes(t.values[0].stat)) {
          for (const e of t.values) acc.add(e.stat, e.kind, tq(e, it), `${src} ${it.trait}`);
        }
      }
    }
    // glyphs
    if (it.enchant) {
      const infused = it.trait === 'Infused';
      if (cat === 'armor' || cat === 'shield') {
        const g = C.enchants.armor[it.enchant];
        if (g) {
          const size = LARGE_GLYPH_SLOTS.has(slot) ? 'large' : 'small';
          const mag = v(g[size]);
          const mult = infused ? 1 + v(C.traits.armor.Infused.value) / 100 : 1;
          g.values.forEach((e, i) => acc.add(e.stat, 'flat', Math.round((Array.isArray(mag) ? mag[i] : mag) * mult), `${src} glyph ${it.enchant}`));
        }
      } else if (cat === 'jewelry') {
        const g = C.enchants.jewelry[it.enchant];
        if (g && g.magnitude && g.magnitude.value != null) {
          const mult = infused ? 1 + C.traits.jewelry.Infused.values[0].value / 100 : 1;
          for (const e of g.values) acc.add(e.stat, e.kind || 'flat', Math.round(g.magnitude.value * mult) * (e.negative ? -1 : 1), `${src} glyph ${it.enchant}`);
        }
      }
      // weapon glyphs: procs, no sheet effect
    }
  }

  // mundus
  if (build.mundus) {
    const m = C.mundus.stones[build.mundus];
    if (m) {
      const mult = 1 + divinesPercent / 100;
      for (const e of m.values) acc.add(e.stat, e.kind, e.kind === 'flat' ? Math.round(e.value * mult) : Math.round(e.value * mult * 10) / 10, `mundus ${build.mundus}`);
    } else notes.push(`unknown mundus ${build.mundus}`);
  }

  // food
  const foodStats = resolveFood(build.food, C);
  if (foodStats) for (const [stat, val] of Object.entries(foodStats.stats)) if (val) acc.add(stat, 'flat', val, `food ${foodStats.name}`);

  // vampire stage
  if (ctx.vampireStage > 0) {
    const st = C.vampireStages.stages[String(ctx.vampireStage)];
    let hr = st.healthRecovery.value;
    const unnatural = activePassives(build, data).some(([n]) => n === 'Unnatural Resistance');
    if (unnatural) hr = { 1: -10, 2: 0, 3: -25, 4: -50 }[ctx.vampireStage];
    acc.add('vampireHealthRecoveryPenalty', 'percent', hr, `vampire stage ${ctx.vampireStage}`);
    acc.add('abilityCost', 'percent', st.regularAbilityCost.value, `vampire stage ${ctx.vampireStage}`);
    acc.add('flameDamageTaken', 'percent', st.flameDamageTaken.value, `vampire stage ${ctx.vampireStage}`);
  }

  return { ctx, acc, notes, setCounts, setPerfected, foodStats };
}

function resolveFood(food, C) {
  if (!food) return null;
  if (typeof food === 'object') return { name: food.name || 'custom', stats: { maxHealth: food.maxHealth || 0, maxMagicka: food.maxMagicka || 0, maxStamina: food.maxStamina || 0, healthRecovery: food.healthRecovery || 0, magickaRecovery: food.magickaRecovery || 0, staminaRecovery: food.staminaRecovery || 0 } };
  const item = (C.foods.items || []).find((f) => f.id === food);
  return item ? { name: item.name, stats: item.stats } : null;
}

// ------------------------------------------------------------ panel maths

function round1(x) { return Math.round(x * 10) / 10; }

function computeBar(build, data, barIndex, strategies) {
  const C = data.constants; const B = C.base;
  const { ctx, acc, notes, setCounts, setPerfected, foodStats } = collect(build, data, barIndex, strategies);
  const a = build.attributes;
  const pts = C.attributePoints;

  const maxStat = (stat, base, points, perPoint, extraFlat = 0) => {
    let flat = acc.flat(stat) + extraFlat;
    let after = 0;
    if (strategies.maxStatPercentBase === 'excludeFood' && foodStats) { after = foodStats.stats[stat] || 0; flat -= after; }
    let val = (v(base) + points * v(perPoint) + flat) * (1 + acc.pct(stat) / 100) + after;
    return val;
  };
  // Battle Spirit flat Max Health (1600, fixtures 001 and 002) goes in before percent bonuses, like the 2016 fix says
  // Battle Spirit adds no flat Max Health today: fixture 007 (Cyrodiil) lands exactly without it. flags.battleSpiritFlatHealth
  // true keeps the 1600 that fixtures 001 and 002 seemed to show (their difference sits on Yeets' back bar, still open).
  const bsFlatHealth = ctx.battleSpirit && build.flags && build.flags.battleSpiritFlatHealth === true ? v(C.battleSpirit.legacyFlatMaxHealth) : 0;
  let maxHealth = maxStat('maxHealth', B.maxHealth, a.health, pts.healthPerPoint, bsFlatHealth);
  const maxMagicka = maxStat('maxMagicka', B.maxMagicka, a.magicka, pts.magickaPerPoint);
  const maxStamina = maxStat('maxStamina', B.maxStamina, a.stamina, pts.staminaPerPoint);

  const recovery = (stat, base, penalties) => {
    let pct = acc.pct(stat);
    let mult = 1;
    for (const p of penalties) {
      if (strategies.recoveryPenalties === 'additive') pct += p; else mult *= 1 + p / 100;
    }
    return (v(base) + acc.flat(stat)) * (1 + pct / 100) * mult;
  };
  const hrPenalties = [];
  if (ctx.battleSpirit) hrPenalties.push(C.battleSpirit.effects.find((e) => e.stat === 'healthRecovery').value);
  if (acc.pct('vampireHealthRecoveryPenalty')) hrPenalties.push(acc.pct('vampireHealthRecoveryPenalty'));
  const healthRecovery = recovery('healthRecovery', B.healthRecovery, hrPenalties);
  const magickaRecovery = recovery('magickaRecovery', B.magickaRecovery, []);
  const staminaRecovery = recovery('staminaRecovery', B.staminaRecovery, []);

  // off hand rating through Dual Wield Expert: percentOfOffHand bucket holds the percent
  let offHandFlat = 0;
  if (acc.flat('offHandRating') && acc.pct('percentOfOffHandRating')) offHandFlat = acc.flat('offHandRating') * acc.pct('percentOfOffHandRating') / 100;
  const weaponDamage = (v(B.weaponDamage) + acc.flat('weaponDamage') + offHandFlat) * (1 + acc.pct('weaponDamage') / 100);
  const spellDamage = (v(B.spellDamage) + acc.flat('spellDamage') + offHandFlat) * (1 + acc.pct('spellDamage') / 100);

  const critOf = (stat) => v(B.critChancePercent) + acc.flat(stat) / v(B.critRatingPerPercent) + acc.pct('critChancePercent');
  const weaponCritChance = critOf('weaponCritRating');
  const spellCritChance = critOf('spellCritRating');
  // The character sheet shows Critical Damage as the bonus above the base (50%): a naked character reads 0%,
  // fixture 001 reads 33% for 5 + 8 + 12 + 8. The cap (125% total) is applied to the total, then the base removed.
  const critCap = v(B.critDamageCapPercent) + acc.flat('critDamageCap');
  const critDamage = Math.min(v(B.critDamagePercent) + acc.pct('critDamage') + acc.flat('critDamage'), critCap) - v(B.critDamagePercent);

  // Resistance: armor and armor-like flats times the armor percent (Balanced Warrior), plus the unscaled flats:
  // spell-only ones (fixture 005 reads Spell Resistance = Physical Resistance + 726 Spell Warding with Balanced
  // Warrior at 6%) and the weapon trait (fixture 006: Defending 3276 enters without the 6%).
  const resist = (stat) => {
    const rows = acc.bucket(stat).rows;
    const unscaled = rows.filter((r) => r.kind === 'flat' && (r.spellOnly || r.group === 'weaponTrait')).reduce((a, r) => a + r.value, 0);
    return (acc.flat(stat) - unscaled) * (1 + acc.pct(stat) / 100) + unscaled;
  };
  const physicalResistance = resist('physicalResistance');
  const spellResistance = resist('spellResistance');
  const mitigation = (r) => Math.min(r, v(B.resistanceCapRating)) / v(B.resistancePerPercent);

  const physicalPenetration = acc.flat('physicalPenetration');
  const spellPenetration = acc.flat('spellPenetration');

  const cost = (stat, base) => {
    const flat = acc.flat(stat);
    const weapon = acc.weaponPercents(stat);
    const additive = strategies.costWeaponPercent === 'additive';
    const pct = additive ? acc.pct(stat) : acc.pct(stat) - weapon.reduce((a, b) => a + b, 0);
    const mult = (1 + pct / 100) * (additive ? 1 : weapon.reduce((a, b) => a * (1 + b / 100), 1));
    if (strategies.costOrder === 'percentThenFlat') return v(base) * mult + flat;
    return (v(base) + flat) * mult;
  };
  const blockCost = cost('blockCost', B.blockCost);
  const rollDodgeCost = cost('rollDodgeCost', B.rollDodgeCost);
  const sprintCost = cost('sprintCost', B.sprintCostPerSecond);
  const breakFreeCost = cost('breakFreeCost', B.breakFreeCost);
  const bashCost = cost('bashCost', B.bashCost);
  // Block mitigation: the 50 base times the Champion Point percent, plus one point per heavy piece
  // (fixtures 003, 002 and 005: 52 naked with Fortification, 54 with two heavy pieces, 55 with three).
  const bmArmor = acc.bucket('blockMitigation').rows.filter((r) => r.group === 'armor' && r.kind === 'percent').reduce((a, r) => a + r.value, 0);
  let blockMitigation = strategies.blockMitigation === 'additive'
    ? v(B.blockMitigationPercent) + acc.pct('blockMitigation')
    : v(B.blockMitigationPercent) * (1 + (acc.pct('blockMitigation') - bmArmor) / 100) + bmArmor;
  if (acc.override('blockMitigation') != null) blockMitigation = acc.override('blockMitigation');

  const movementSpeed = Math.min(v(B.movementSpeedPercent) + acc.pct('movementSpeed'), v(B.movementSpeedCapPercent));
  // The sheet's Sprint Speed is the sprint base plus sprint bonuses only (fixture 003: 144 = 140 + Hasty 4 with Celerity slotted)
  const sprintSpeed = Math.min(v(B.sprintSpeedPercent) + acc.pct('sprintSpeed'), v(B.movementSpeedCapPercent));

  const bsPct = (stat) => {
    const e = C.battleSpirit.effects.find((x) => x.stat === stat);
    return ctx.battleSpirit && e ? e.value : 0;
  };
  const combinePct = (stat, bsStat) => {
    const base = acc.pct(stat);
    const bs = bsStat ? bsPct(bsStat) : 0;
    if (!bs) return base;
    return strategies.battleSpiritPercents === 'additive' ? base + bs : ((1 + base / 100) * (1 + bs / 100) - 1) * 100;
  };

  const critHealing = acc.pct('critHealing');
  // Sneak cost: every percent source multiplies on its own (fixtures 002 to 004: 118 x 0.5 Sustaining Shadows
  // x 0.8 Medium Armor Bonuses x 0.72 Improved Sneak = 34), unlike block where the armor passives add up.
  const sneakCost = (v(B.sneakCost) + acc.flat('sneakCost')) * (acc.bucket('sneakCost').rows.filter((r) => r.kind === 'percent').reduce((m, r) => m * (1 + r.value / 100), 1));
  const blockMoveSpeed = v(B.blockMoveSpeedPercent) + acc.pct('blockMoveSpeed');
  // Sneak speed: the 60% base already reflects the Champion Point passives (fixtures 003 and 004 read 60 naked with
  // Fleet Phantom in), so only non CP reductions of the 40 point penalty apply
  // and the penalty cannot go below zero: Dark Stalker removes it and the sheet reads 100 (fixture 005)
  const sneakPenaltyPct = Math.max(-100, acc.bucket('sneakSpeedPenalty').rows.filter((r) => r.kind === 'percent' && !/^CP /.test(r.source)).reduce((a, r) => a + r.value, 0));
  const sneakSpeed = 100 - (100 - v(B.sneakSpeedPercent)) * (1 + sneakPenaltyPct / 100);
  // The sheet lists a percent per damage type: general damage done, plus the single target CP star it folds in,
  // plus the type's own bonus (Energized). Flat is always 0 on the sheet so far.
  const typedDamage = {};
  for (const t of ['Physical', 'Bleed', 'Disease', 'Flame', 'Frost', 'Magic', 'Oblivion', 'Poison', 'Shock']) {
    typedDamage[t.toLowerCase() + 'DamagePercent'] = round1(acc.pct('damageDone') + acc.pct('damageDoneSingleTarget') + acc.pct('damageDone' + t));
  }
  // Per type resistance: the physical or spell rating plus any flat resistance of that type (fixture 005: Disease and
  // Poison 28.9 = (16765 + 2310 Resist Affliction) / 660 where Bleed reads the plain 25.4).
  const typeMit = (base, type) => round1(mitigation(base + acc.flat(type + 'Resistance')));
  const typedResistance = {
    flameResistancePercent: typeMit(spellResistance, 'flame'), frostResistancePercent: typeMit(spellResistance, 'frost'),
    shockResistancePercent: typeMit(spellResistance, 'shock'), magicResistancePercent: typeMit(spellResistance, 'magic'),
    diseaseResistancePercent: typeMit(physicalResistance, 'disease'), poisonResistancePercent: typeMit(physicalResistance, 'poison'),
    bleedResistancePercent: typeMit(physicalResistance, 'bleed'),
  };
  const esoPlus = !(build.flags && build.flags.esoPlus === false) ? v(B.esoPlusBonusPercent) : 0;

  const main = {
    maxHealth: Math.round(maxHealth), maxMagicka: Math.round(maxMagicka), maxStamina: Math.round(maxStamina),
    healthRecovery: Math.round(healthRecovery), magickaRecovery: Math.round(magickaRecovery), staminaRecovery: Math.round(staminaRecovery),
    weaponDamage: Math.round(weaponDamage), spellDamage: Math.round(spellDamage),
    weaponCritChance: round1(weaponCritChance), spellCritChance: round1(spellCritChance), critDamage: round1(critDamage),
    physicalPenetration: Math.round(physicalPenetration), spellPenetration: Math.round(spellPenetration),
    physicalResistance: Math.round(physicalResistance), spellResistance: Math.round(spellResistance),
    critHealing: round1(critHealing),
  };
  const advanced = {
    weaponCritChancePercent: round1(weaponCritChance),
    spellCritChancePercent: round1(spellCritChance),
    critDamagePercent: round1(critDamage),
    critResistance: Math.round(v(B.critResistance) + acc.flat('critResistance')),
    physicalPenetration: main.physicalPenetration,
    spellPenetration: main.spellPenetration,
    physicalResistance: main.physicalResistance,
    physicalMitigationPercent: round1(mitigation(physicalResistance)),
    spellResistance: main.spellResistance,
    spellMitigationPercent: round1(mitigation(spellResistance)),
    damageDonePercent: round1(acc.pct('damageDone')),
    healingDonePercent: round1(acc.pct('healingDone')),
    // The sheet leaves Battle Spirit out of these three (fixture 001 reads Healing Taken 4% in Cyrodiil);
    // the Battle Spirit adjusted values sit in advanced.battleSpirit when it is active.
    healingTakenPercent: round1(acc.pct('healingTaken')),
    damageTakenPercent: round1(acc.pct('damageTaken')),
    damageShieldStrengthPercent: round1(acc.pct('damageShieldStrength')),
    blockCost: Math.round(blockCost),
    blockMitigationPercent: round1(blockMitigation),
    rollDodgeCost: Math.round(rollDodgeCost),
    sprintCost: Math.round(sprintCost),
    breakFreeCost: Math.round(breakFreeCost),
    bashCost: Math.round(bashCost),
    bashDamageBonus: Math.round(acc.flat('bashDamage')),
    movementSpeedPercent: round1(movementSpeed),
    sprintSpeedPercent: round1(sprintSpeed),
    magickaCostPercent: round1(acc.pct('magickaCost')),
    staminaCostPercent: round1(acc.pct('staminaCost')),
    magickaCostFlat: Math.round(acc.flat('magickaCostReduction')),
    staminaCostFlat: Math.round(acc.flat('staminaCostReduction')),
    ultimateCostPercent: round1(acc.pct('ultimateCost')),
    sneakCost: Math.round(sneakCost),
    blockMoveSpeedPercent: round1(blockMoveSpeed),
    sneakSpeedPercent: round1(sneakSpeed),
    ...typedResistance,
    ...typedDamage,
    damageDoneSingleTargetPercent: round1(acc.pct('damageDoneSingleTarget')),
    damageDoneDirectPercent: round1(acc.pct('damageDoneDirect')),
    damageDoneAoePercent: round1(acc.pct('damageDoneAoe')),
    damageDoneDotPercent: round1(acc.pct('damageDoneDot')),
    healingDoneFlat: 0, healingTakenFlat: 0,
    critHealingPercent: round1(critHealing),
    experiencePercent: esoPlus, goldPercent: esoPlus, craftingInspirationPercent: esoPlus, telVarPercent: esoPlus, alliancePointsPercent: esoPlus,
    abilityRangeBonusMeters: ctx.battleSpirit ? bsPct('abilityRangeOver28m') : 0,
    battleSpirit: ctx.battleSpirit ? {
      healingTakenPercent: round1(combinePct('healingTaken', 'healingReceived')),
      damageTakenPercent: round1(combinePct('damageTaken', 'damageTaken')),
      damageShieldStrengthPercent: round1(combinePct('damageShieldStrength', 'damageShieldStrength')),
    } : null,
  };
  const breakdown = {};
  for (const [stat, b] of acc.buckets) breakdown[stat] = b.rows;
  return { main, advanced, breakdown, dropped: acc.dropped, notes, setCounts, setPerfected, context: { armor: ctx.armor, weapons: ctx.weaponTypes, dualWield: ctx.dualWield, twoHanded: ctx.twoHanded } };
}

// ------------------------------------------------------------ entry point

export function computeSheet(build, data, options = {}) {
  const strategies = { ...DEFAULT_STRATEGIES, ...(build.flags && build.flags.strategies), ...(options.strategies || {}) };
  for (const [k, val] of Object.entries(strategies)) {
    if (!STRATEGIES[k] || !STRATEGIES[k].includes(val)) throw new Error(`unknown strategy ${k}=${val}`);
  }
  const validation = validateBuild(build, data);
  if (validation.errors.some((e) => /bars must hold|build is not/.test(e))) return { validation, bars: [], strategies };
  const bars = [0, 1].map((i) => computeBar(build, data, i, strategies));
  return { validation, bars, strategies };
}

export default computeSheet;
