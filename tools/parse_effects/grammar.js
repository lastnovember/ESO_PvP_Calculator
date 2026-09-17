/*
 * Prose to structured effects.
 *
 * parseText(text, options) -> { status, effects, sentences, prefixConditions }
 *
 * Effect shapes
 *   { stat, value, kind: 'flat' | 'percent', condition, raw }
 *   { buff: 'Major Resolve', condition, raw }              resolved through the named buff table
 *   { kind: 'proc', raw, condition }                        combat or target dependent, kept for later phases
 *   { kind: 'unparsed', raw }                               grammar gap, counted against coverage
 *
 * Conditions (null = always)
 *   { type: 'battleSpirit', active, scope: 'self' | 'target' }
 *   { type: 'slotted', ability } | { type: 'slotted', line, perAbility } | { type: 'slotted', class, perAbility }
 *   { type: 'weapon', weapon }   { type: 'weaponTypeCount', weaponType }
 *   { type: 'armorPieces', weight } { type: 'armorPiecesEvery2', weight } { type: 'armorTypes' } { type: 'armorAtLeast', weight, count }
 *   { type: 'werewolfForm' } { type: 'vampireStage', min } { type: 'outOfCombat' } { type: 'perStage' }
 *   { type: 'all', of: [...] }
 *   { type: 'combat' | 'target' | 'attackCategory' | 'abilityCategory' | 'state', detail }   dropped by the engine this phase
 */

const RANGE = '(\\d[\\d,]*(?:\\.\\d+)?|\\.\\d+)(?:\\s*-\\s*(\\d[\\d,]*(?:\\.\\d+)?))?';
const NUM = '(\\d[\\d,]*(?:\\.\\d+)?|\\.\\d+)';

function toNum(s) { return Number(String(s).replace(/,/g, '')); }
function rangeMax(a, b) { return b != null ? Math.max(toNum(a), toNum(b)) : toNum(a); }

// Stat phrases, matched case insensitively, longest first.
const STAT_PHRASES = [
  ['health recovery, magicka recovery, and stamina recovery', 'allRecovery'],
  ['health, magicka, and stamina recovery', 'allRecovery'],
  ['health, stamina, and magicka recovery', 'allRecovery'],
  ['health, magicka and stamina recovery', 'allRecovery'],
  ['health and magicka recovery', ['healthRecovery', 'magickaRecovery']],
  ['magicka and health recovery', ['healthRecovery', 'magickaRecovery']],
  ['magicka and stamina recovery', ['magickaRecovery', 'staminaRecovery']],
  ['magicka recovery and stamina recovery', ['magickaRecovery', 'staminaRecovery']],
  ['maximum health, magicka, and stamina', 'allMax'],
  ['max health, magicka, and stamina', 'allMax'],
  ['max health, stamina, and magicka', 'allMax'],
  ['max magicka and magicka recovery', ['maxMagicka', 'magickaRecovery']],
  ['max magicka and stamina', ['maxMagicka', 'maxStamina']],
  ['max magicka and max stamina', ['maxMagicka', 'maxStamina']],
  ['magicka and stamina', ['maxMagicka', 'maxStamina']],
  ['weapon damage, spell damage, and armor', ['weaponAndSpellDamage', 'armor']],
  ['weapon damage and spell damage', 'weaponAndSpellDamage'],
  ['weapon and spell damage', 'weaponAndSpellDamage'],
  ['spell damage and weapon damage', 'weaponAndSpellDamage'],
  ['weapon critical and spell critical rating', 'critRating'],
  ['spell critical and weapon critical rating', 'critRating'],
  ['weapon and spell critical', 'critRating'],
  ['weapon critical and spell critical', 'critRating'],
  ['spell critical rating', 'spellCritRating'],
  ['weapon critical rating', 'weaponCritRating'],
  ['spell critical', 'spellCritRating'],
  ['weapon critical', 'weaponCritRating'],
  ['critical strike chance', 'critChancePercent'],
  ['critical chance rating', 'critRating'],
  ['critical rating', 'critRating'],
  ['critical chance', 'critRating'],
  ['maximum critical damage and healing', 'critDamageCap'],
  ['critical damage and critical healing done', 'critDamageAndHealing'],
  ['critical damage and critical healing', 'critDamageAndHealing'],
  ['critical damage and healing done rating', 'critDamageAndHealing'],
  ['critical damage and healing done', 'critDamageAndHealing'],
  ['critical damage and healing', 'critDamageAndHealing'],
  ['critical damage done', 'critDamage'],
  ['critical damage', 'critDamage'],
  ['critical resistance', 'critResistance'],
  ['physical resistance and spell resistance', 'physicalAndSpellResistance'],
  ['spell resistance and physical resistance', 'physicalAndSpellResistance'],
  ['physical and spell resistance', 'physicalAndSpellResistance'],
  ['spell and physical resistance', 'physicalAndSpellResistance'],
  ['physical resistance', 'physicalResistance'],
  ['spell resistance', 'spellResistance'],
  ['armor', 'armor'],
  ['physical penetration and spell penetration', 'offensivePenetration'],
  ['spell and physical penetration', 'offensivePenetration'],
  ['physical and spell penetration', 'offensivePenetration'],
  ['offensive penetration', 'offensivePenetration'],
  ['physical penetration', 'physicalPenetration'],
  ['spell penetration', 'spellPenetration'],
  ['healing received and shield strength', ['healingTaken', 'damageShieldStrength']],
  ['healing received and damage shield strength', ['healingTaken', 'damageShieldStrength']],
  ['healing received', 'healingTaken'],
  ['healing taken', 'healingTaken'],
  ['healing done', 'healingDone'],
  ['maximum health', 'maxHealth'], ['max health', 'maxHealth'],
  ['maximum magicka', 'maxMagicka'], ['max magicka', 'maxMagicka'],
  ['maximum stamina', 'maxStamina'], ['max stamina', 'maxStamina'],
  ['health recovery', 'healthRecovery'],
  ['magicka recovery', 'magickaRecovery'],
  ['stamina recovery', 'staminaRecovery'],
  ['weapon damage', 'weaponDamage'],
  ['spell damage', 'spellDamage'],
  ['movement speed', 'movementSpeed'],
  ['mount speed', 'mountSpeed'], ['mounted speed', 'mountSpeed'],
  ['all damage done', 'damageDone'],
  ['damage done', 'damageDone'],
  ['damage taken', 'damageTaken'],
  ['damage shield strength', 'damageShieldStrength'],
  ['frost resistance', 'frostResistance'],
  ['cold resistance', 'frostResistance'],
  ['flame resistance', 'flameResistance'],
  ['poison and disease resistance', ['poisonResistance', 'diseaseResistance']],
  ['disease and poison resistance', ['poisonResistance', 'diseaseResistance']],
  ['stealth detection', 'stealthDetection'],
  ['damage you can block', 'blockMitigation'],
  ['damage you block', 'blockMitigation'],
  ['damage blocked', 'blockMitigation'],
  ['damage done with bash', 'bashDamage'],
  ['bash damage', 'bashDamage'],
  ['health', 'maxHealth'], ['magicka', 'maxMagicka'], ['stamina', 'maxStamina'],
];
const STAT_ALT = STAT_PHRASES.map(([p]) => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
function statFor(phrase) {
  const p = phrase.toLowerCase().trim();
  for (const [k, s] of STAT_PHRASES) if (k === p) return s;
  return null;
}
const CLASS_NAMES = ['Dragonknight', 'Sorcerer', 'Nightblade', 'Templar', 'Warden', 'Necromancer', 'Arcanist'];

function titleCase(s) {
  return s.trim().toLowerCase().split(/\s+/).map((w) => (w === 'of' || w === 'the') ? w : w[0].toUpperCase() + w.slice(1)).join(' ').replace(/'S\b/g, "'s");
}

// ---------------------------------------------------------- prefix conditions

function stripPrefixConditions(text) {
  const conds = [];
  let t = text.trim();
  const rules = [
    [/^\(?WITH (?:A|AN) ([A-Z' ]+?) ABILITY SLOTTED\)?\s*/i, (m) => ({ type: 'slotted', line: titleCase(m[1]) })],
    [/^While you have a ([A-Za-z' ]+?) ability slotted,?\s*/i, (m) => ({ type: 'slotted', line: titleCase(m[1]) })],
    [/^WHILE YOU HAVE A ([A-Z' ]+?) ABILITY SLOTTED\s*/i, (m) => ({ type: 'slotted', line: titleCase(m[1]) })],
    [/^WHEN SOUL ABILITY IS SLOTTED\s*/i, () => ({ type: 'slotted', line: 'Soul Magic' })],
    [/^\(?WITH TWO-HANDED WEAPON EQUIPPED\)?\s*/i, () => ({ type: 'weapon', weapon: 'two handed' })],
    [/^WHILE (?:USING )?DUAL WIELD(?:ING)?(?: ATTACKS)?\s*/i, () => ({ type: 'weapon', weapon: 'dual wield' })],
    [/^WITH BOW EQUIPPED\s*/i, () => ({ type: 'weapon', weapon: 'bow' })],
    [/^With Destruction Staff Equipped\s*/i, () => ({ type: 'weapon', weapon: 'destruction staff' })],
    [/^WITH RESTORATION STAFF EQUIPPED\s*/i, () => ({ type: 'weapon', weapon: 'restoration staff' })],
    [/^WITH ONE HAND WEAPON AND SHIELD EQUIPPED\s*/i, () => ({ type: 'weapon', weapon: 'one hand and shield' })],
    [/^WHILE YOU ARE IN WEREWOLF FORM\s*/i, () => ({ type: 'werewolfForm' })],
    [/^While you are at Vampire Stage (\d) or higher\s*/i, (m) => ({ type: 'vampireStage', min: Number(m[1]) })],
    [/^While you are at Vampire Stage (\d)\s*/i, (m) => ({ type: 'vampireStage', min: Number(m[1]) })],
    [/^\(WHILE YOU HAVE VAMPIRISM STAGE (\d) OR HIGHER\)\s*/i, (m) => ({ type: 'vampireStage', min: Number(m[1]) })],
    [/^WHEN ACTIVATING AN? [A-Z' ]+ ABILITY\s*/i, () => ({ type: 'combat', detail: 'on cast' })],
    [/^Current (?:Restore|amount|value|duration|penalty|bonus):\s*[^A-Z]*?(?=[A-Z][a-z])/, () => null],
    [/^Requires \d pieces of (light|medium|heavy) armor equipped\s*/i, (m) => ({ type: 'armorAtLeast', weight: m[1].toLowerCase(), count: 5 })],
    [/^(?:Cost|Duration): [^.]*?\.\s*/i, () => null],
  ];
  let changed = true;
  while (changed) {
    changed = false;
    for (const [re, fn] of rules) {
      const m = t.match(re);
      if (m && m[0].length) { const c = fn(m); if (c) conds.push(c); t = t.slice(m[0].length); changed = true; }
    }
  }
  return { text: t, conds };
}

// ---------------------------------------------------------- helpers

function mk(stat, value, kind, condition, raw) {
  return (Array.isArray(stat) ? stat : [stat]).map((s) => ({ stat: s, value, kind, condition: condition || null, raw }));
}
function ctxOf(conds) { let c = null; for (const x of conds) c = mergeCond(c, x); return c; }
export function mergeCond(a, b) {
  if (!a) return b || null;
  if (!b) return a;
  if (a.type === 'all') return { type: 'all', of: [...a.of, b] };
  return { type: 'all', of: [a, b] };
}
function lastOfBracket(s) { const parts = s.split('/').map((x) => toNum(x.trim())); return parts[parts.length - 1]; }
function conditional(raw, cond) { return { status: 'conditional', effects: [{ kind: 'proc', raw, condition: cond }] }; }

function perClause(tail) {
  let m;
  if ((m = tail.match(/^(?:for each|for every|per) piece of (light|medium|heavy) armor(?: equipped| worn)?/i))) return [{ type: 'armorPieces', weight: m[1].toLowerCase() }, tail.slice(m[0].length)];
  if ((m = tail.match(/^for every 2 pieces of (light|medium|heavy) armor(?: equipped| worn)?/i))) return [{ type: 'armorPiecesEvery2', weight: m[1].toLowerCase() }, tail.slice(m[0].length)];
  if ((m = tail.match(/^per type of armor \(heavy, medium, light\) that you have equipped/i))) return [{ type: 'armorTypes' }, tail.slice(m[0].length)];
  if ((m = tail.match(/^(?:for each|per) ([A-Za-z' ]+?) ability slotted/i))) {
    const name = titleCase(m[1]);
    if (CLASS_NAMES.includes(name)) return [{ type: 'slotted', class: name, perAbility: true }, tail.slice(m[0].length)];
    return [{ type: 'slotted', line: name, perAbility: true }, tail.slice(m[0].length)];
  }
  if ((m = tail.match(/^per stage/i))) return [{ type: 'perStage' }, tail.slice(m[0].length)];
  if ((m = tail.match(/^(?:for each|per) active crux/i))) return [{ type: 'state', detail: 'crux' }, tail.slice(m[0].length)];
  return [null, tail];
}

const PROC_HINTS = /\b(when|whenever|after|while|against|if\b|anytime|once every|chance|dealing damage|deals? \d|casting|activating|stacks?\b|for \d+ (?:seconds|minutes)|for 1 minute|for the duration|based on|in proportion|up to \d+ times|up to a maximum|missing (?:health|magicka|stamina)|current (?:health|amount|bonus|value)|targets?\b|enemies|enemy|ally|allies|group members|heavy attacks?|light attacks?|light or heavy|synerg|resurrect|potion|pickpocket|sneak|detection|experience|gold\b|inspiration|fall damage|mount|swimming|lava|fence|bounty|lock|harvest|fish|treasure|repair|wayshrine|duration|seconds|snare|immobiliz|crowd control|status effect|off balance|flanking|blocking players|ranged|melee|less damage|more damage|damage from|abilities? (?:cost|deal)|your next|soul gem|revive|invisib|ultimate\b|fury|heal(?:ed|s)?\b|restores?\b|shield|absorb|corpse|upgrades?|this (?:value|effect|bonus|portion)|scales? (?:off|with)|affected|range|meters?\b|bracing|traps?|guards?|crux|pets?\b|spent|cast time|channel|damage over time|direct damage|area of effect|per stack|every \d|stage|standing|within|resource|also gain|random|buffs|debuffs|ticks?\b|current [a-z]+:)/i;
const COMBAT_TAIL = /^(if|while|when|whenever|against|on |after|during|only|this|to |from |with |per active|based|for every \d|in |towards|and (?:its|your (?:next|damage))|up to a maximum)/i;

// ---------------------------------------------------------- sentence grammar

function parseSentence(sentenceIn, conds, depth = 0) {
  const raw = sentenceIn.trim().replace(/\s+/g, ' ');
  if (!raw) return { status: 'empty', effects: [] };
  let rest = raw;
  let m;
  const base = ctxOf(conds);

  // Battle Spirit alternate value: a whole sentence about the previous effect, or a clause on this one
  if ((m = rest.match(/^This (?:effect|value|bonus) is (?:reduced|halved) to ([\d.]+)%? (?:against targets with Battle Spirit|while Battle Spirit is active)\.?$/i))) {
    return { status: 'battleSpiritAlt', effects: [], alt: { value: toNum(m[1]), scope: /against targets/i.test(m[0]) ? 'target' : 'self' } };
  }
  let bsAlt = null;
  if ((m = rest.match(/,?\s*(?:reducing|reduced|which reduces|halving) to ([\d.]+)%? (?:against targets with Battle Spirit|while Battle Spirit is active|when Battle Spirit is active)\.?/i))) {
    bsAlt = { value: toNum(m[1]), scope: /against targets/i.test(m[0]) ? 'target' : 'self' };
    rest = (rest.slice(0, m.index) + '.' + rest.slice(m.index + m[0].length)).replace(/\.\./g, '.').trim();
  }
  const withBs = (effects) => {
    if (!bsAlt) return effects;
    const cond = (active) => ({ type: 'battleSpirit', active, scope: bsAlt.scope });
    const primary = effects.map((e) => (e.stat ? { ...e, condition: mergeCond(e.condition, cond(false)) } : e));
    const alt = effects.filter((e) => e.stat).map((e) => ({ ...e, value: bsAlt.value, condition: mergeCond(e.condition, cond(true)) }));
    return [...primary, ...alt];
  };
  const done = (effects, tail) => finish(effects, tail, raw, withBs, conds, depth);

  // Flavor: no digits, no buff, no stat phrase
  if (!/\d/.test(rest) && !/\b(Major|Minor) [A-Z]/.test(rest) && !/\b(increas|reduc|decreas|grant|gain|adds?\b|restor|ignore|allow|remove)/i.test(rest)) {
    return { status: 'flavor', effects: [] };
  }

  // Markyn Ring: "Gain 100 Weapon Damage and Spell Damage and 1157 Armor for every set you are wearing 3 or more pieces of."
  if ((m = rest.match(new RegExp(`^Gain ${NUM} (${STAT_ALT}) and ${NUM} (${STAT_ALT}) for every set you are wearing (\\d) or more pieces of`, 'i')))) {
    const cond = mergeCond(base, { type: 'setsWithPieces', min: Number(m[5]) });
    return { status: 'ok', effects: [...mk(statFor(m[2]), toNum(m[1]), 'flat', cond, raw), ...mk(statFor(m[4]), toNum(m[3]), 'flat', cond, raw)] };
  }
  // Deadly Bash: "Improves your standard Bash attacks, causing them to deal 500 more damage and cost 50% less Stamina."
  // (fixture 008: Bash Cost 257 = (765 x 0.5 - 90) x 0.88 with a shield)
  if ((m = rest.match(/^Improves your standard Bash attacks, causing them to deal ([\d.]+) more damage and cost ([\d.]+)% less Stamina/i))) {
    return { status: 'ok', effects: [...mk('bashDamage', toNum(m[1]), 'flat', base, raw), ...mk('bashCost', -toNum(m[2]), 'percent', base, raw)] };
  }
  // Dual Wield Expert: "Increases Weapon Damage and Spell Damage by 6% of off-hand weapon's damage."
  if ((m = rest.match(/^Increases Weapon Damage and Spell Damage by ([\d.]+)% of off-hand weapon's damage/i))) return { status: 'ok', effects: mk('percentOfOffHandRating', toNum(m[1]), 'percent', base, raw) };
  // Damage done by attack category (Deadly Aim, Master-at-Arms, Biting Aura, Thaumaturge): kept as their own stats;
  // the character sheet folds the single target one into every damage type (fixtures 001 to 004)
  if ((m = rest.match(/^Increases your damage done with (single target attacks|direct damage attacks|area of effect attacks|damage over time effects) by ([\d.]+)%/i))) {
    const stat = { 'single target attacks': 'damageDoneSingleTarget', 'direct damage attacks': 'damageDoneDirect', 'area of effect attacks': 'damageDoneAoe', 'damage over time effects': 'damageDoneDot' }[m[1].toLowerCase()];
    const [pc, rem] = perClause(rest.slice(m[0].length).trim().replace(/^\.$/, ''));
    return done(mk(stat, toNum(m[2]), 'percent', mergeCond(base, pc), raw), rem);
  }
  // Damage done by damage type (Energized): "Increases your Physical and Shock Damage by 5%."
  if ((m = rest.match(/^Increases your ((?:Physical|Bleed|Disease|Flame|Frost|Magic|Oblivion|Poison|Shock)(?:,? (?:and )?(?:Physical|Bleed|Disease|Flame|Frost|Magic|Oblivion|Poison|Shock))*) Damage by ([\d.]+)%\.?$/i))) {
    const types = m[1].split(/,? and |, /).map((t) => t.trim());
    return { status: 'ok', effects: types.flatMap((t) => mk('damageDone' + t[0].toUpperCase() + t.slice(1).toLowerCase(), toNum(m[2]), 'percent', base, raw)) };
  }
  // Skill specific damage: "Increases the damage Wall of Elements deals by 29-1250."
  if (/^Increases the damage [A-Z][\w' ]+ deals by/i.test(rest)) return conditional(raw, { type: 'attackCategory', detail: rest.slice(0, 80) });
  // Ancient Knowledge: "Equipping an Ice Staff reduces the cost of blocking by 36% and increases the amount of damage you block by 20%."
  if ((m = rest.match(/^Equipping an Ice Staff reduces the cost of blocking by ([\d.]+)% and increases the amount of damage you block by ([\d.]+)%/i))) {
    const cond = mergeCond(base, { type: 'weapon', weapon: 'frost staff' });
    return { status: 'ok', effects: [...mk('blockCost', -toNum(m[1]), 'percent', cond, raw), ...mk('blockMitigation', toNum(m[2]), 'percent', cond, raw)] };
  }
  // Staff type clauses: "Inferno Staves increases your damage done with ..."
  if (/^(?:Inferno|Lightning|Ice|Frost) Sta(?:ff|ves) /i.test(rest)) return conditional(raw, { type: 'attackCategory', detail: rest.slice(0, 80) });
  // Set bonus / CP: "Adds 6-300 Weapon Damage and Spell Damage", "Grants 34.6 Armor per stage", "Grants 100 Weapon and Spell Damage to Magical attacks"
  if ((m = rest.match(new RegExp(`^(?:Adds|Grants?|Gain) ${RANGE}(%)? (${STAT_ALT})(.*)$`, 'i')))) {
    const value = rangeMax(m[1], m[2]);
    const kind = m[3] ? 'percent' : 'flat';
    let tail = m[5].trim().replace(/^\.$/, '');
    if (COMBAT_TAIL.test(tail)) return conditional(raw, { type: 'attackCategory', detail: tail });
    const [pc, rem] = perClause(tail);
    return done(mk(statFor(m[4]), value, kind, mergeCond(base, pc), raw), rem);
  }

  // Named buffs
  if ((m = rest.match(/^(?:Gain|Gains|Grants you|Grants|You gain) ((?:Major|Minor) [A-Z][a-z]+(?:,? (?:and )?(?:Major |Minor )?[A-Z][a-z]+)*) at all times/i))) {
    return { status: 'ok', effects: parseBuffList(m[1]).map((b) => ({ buff: b, condition: base, raw })) };
  }
  if ((m = rest.match(/^Grants you ((?:Major|Minor) [A-Z][a-z]+(?:,? (?:and )?(?:Major |Minor )?[A-Z][a-z]+)*)(?:,| increasing| reducing|\.|$)/i))) {
    return { status: 'ok', effects: parseBuffList(m[1]).map((b) => ({ buff: b, condition: base, raw })) };
  }
  // "When slotted on either bar" applies from the other bar too (fixture 001: Merciless Resolve's Major Savagery
  // shows on the ice staff bar); plain "While slotted" needs the ability on the active bar (Bird of Prey's Minor Berserk does not).
  if ((m = rest.match(/^(?:While|When) slotted( on either (?:ability )?bar)?,?\s*(?:you )?gain ((?:Major|Minor) [A-Za-z]+(?:,? (?:and )?(?:Major |Minor )?[A-Z][a-z]+)*)(.*)$/i))) {
    const buffs = parseBuffList(m[2]);
    const cond = mergeCond(base, { type: 'slotted', ability: '$self', ...(m[1] ? { eitherBar: true } : {}) });
    const effs = buffs.map((b) => ({ buff: b, condition: cond, raw }));
    const extra = m[3].match(/your Max Magicka is increased by ([\d.]+)%/i);
    if (extra) effs.push(...mk('maxMagicka', toNum(extra[1]), 'percent', cond, raw));
    return { status: 'ok', effects: effs };
  }
  if ((m = rest.match(/^(?:While|When) slotted( on either (?:ability )?bar)?( and you have a shield equipped)?,?\s*(.+)$/i))) {
    let cond = { type: 'slotted', ability: '$self', ...(m[1] ? { eitherBar: true } : {}) };
    if (m[2]) cond = mergeCond(cond, { type: 'weapon', weapon: 'shield' });
    const inner = parseSentence(m[3], [...conds, cond], depth + 1);
    if (inner.effects.some((e) => e.stat || e.buff)) return inner;
    return conditional(raw, { type: 'combat', detail: m[3].slice(0, 80) });
  }

  // Explanatory sentence about a named buff: "Major Expedition increases your Movement Speed by 30%."
  if (/^(?:Major|Minor) [A-Z][a-z]+ (?:increases|reduces|grants)/i.test(rest)) return { status: 'flavor', effects: [] };
  // Flavor prefix with a lowercase verb: "Your excessive scholarship increases your Magicka and Stamina Recovery by 18%."
  if ((m = rest.match(/^(?:Your|The|Knowledge|Apocryphal|Mastery)[^.]*?\b(increases?|increasing|reduces?|reducing|grants?|granting) (your |the )/))) {
    const verb = { increasing: 'Increases', reducing: 'Reduces', granting: 'Grants' }[m[1].toLowerCase()] || (m[1][0].toUpperCase() + m[1].slice(1));
    const inner = parseSentence(verb + ' ' + rest.slice(m.index + m[0].length - m[2].length), conds, depth + 1);
    if (inner.effects.length) return inner;
  }
  // Gaze of Sithis: "Reduces your Block Mitigation to 0."
  if ((m = rest.match(/^Reduces your Block Mitigation to (\d+)\.?$/i))) return { status: 'ok', effects: [{ stat: 'blockMitigation', value: toNum(m[1]), kind: 'set', condition: base, raw }] };
  // "Gain Major Protection, reducing your damage taken by 10%." (no "at all times")
  if ((m = rest.match(/^Gain ((?:Major|Minor) [A-Z][a-z]+(?:,? (?:and )?(?:Major |Minor )?[A-Z][a-z]+)*), (?:reducing|increasing)/i))) {
    return { status: 'ok', effects: parseBuffList(m[1]).map((b) => ({ buff: b, condition: base, raw })) };
  }
  // Qualified damage or healing: "Increases your damage done with damage over time effects by 10%", "Increases healing with Restoration Staff spells by 5%"
  if ((m = rest.match(/^(?:Increases?|Reduces?) (?:your )?(?:damage done|healing done|healing|damage|critical strike chance|critical damage) (?:with|to|against|from) /i))) return conditional(raw, { type: 'attackCategory', detail: rest.slice(0, 80) });
  // Two handed weapon type bonuses: "Swords increase your Weapon Damage and Spell Damage by 258. Axes increase your Critical Damage done by 12%. Maces increase your Offensive Penetration by 2974."
  if ((m = rest.match(new RegExp(`^(Swords|Axes|Maces) increase your (${STAT_ALT})(?: rating)? by ${NUM}(%)?`, 'i')))) {
    const wt = { swords: 'greatsword', axes: 'battle axe', maces: 'maul' }[m[1].toLowerCase()];
    return { status: 'ok', effects: mk(statFor(m[2]), toNum(m[3]), m[4] ? 'percent' : 'flat', mergeCond(base, { type: 'weaponTypeCount', weaponType: wt }), raw) };
  }
  if ((m = rest.match(/^(Reduces?|Increases?|Decreases?) (?:your |the )?damage (?:you take|taken) from ([A-Za-z ]+?) by ([\d.]+)%/i)) && !/^(Magical|Martial) attacks$/i.test(m[2])) return conditional(raw, { type: 'attackCategory', detail: `damage taken from ${m[2]}` });

  // Passive voice: "the amount of damage you can block is increased by 10% and the cost of blocking is reduced by 10%", "your damage taken is reduced by 3%", "the cost of all your abilities are reduced by 3%"
  if ((m = rest.match(new RegExp(`^(?:your |the )?(?:amount of )?(?:(cost of (?:all (?:of )?)?your abilities|cost of blocking)|(${STAT_ALT})) (?:is|are) (increased|reduced|decreased) by ${NUM}(%)?(.*)$`, 'i')))) {
    const stat = m[1] ? (/blocking/i.test(m[1]) ? 'blockCost' : 'abilityCost') : statFor(m[2]);
    const sign = /^increased$/i.test(m[3]) ? 1 : -1;
    return done(mk(stat, toNum(m[4]) * sign, m[5] ? 'percent' : 'flat', base, raw), m[6]);
  }

  // Costs: "Reduces the cost of Roll Dodge by 120 Stamina per stage", "Reduces the Stamina cost of your One Hand and Shield abilities by 15%", "reduces the cost of blocking by 36%"
  if ((m = rest.match(/^(Reduces?|Reduced|Increases?|Decreases?|Lowers?) (?:the )?(?:(Health, Magicka, Stamina, and Ultimate|Health, Magicka, and Stamina|Magicka and Health|Magicka|Stamina|Health|Ultimate) )?costs? (?:of |for )?(.*?)\s*by ([\d.]+)(%| Stamina| Magicka)(.*)$/i))) {
    const sign = /^(Reduces?|Reduced|Decreases?|Lowers?)/i.test(m[1]) ? -1 : 1;
    const resource = (m[2] || '').toLowerCase();
    const what = m[3].trim().toLowerCase().replace(/^(?:your |all (?:of )?your |all |the |remaining in your )/, '');
    const value = toNum(m[4]) * sign;
    const kind = m[5] === '%' ? 'percent' : 'flat';
    let stat;
    if (/^(roll dodge|roll dodging)$/.test(what)) stat = 'rollDodgeCost';
    else if (/^(sprint|sprinting)$/.test(what)) stat = 'sprintCost';
    else if (/^(block|blocking)$/.test(what)) stat = 'blockCost';
    else if (/^break free$/.test(what)) stat = 'breakFreeCost';
    else if (/^bash$/.test(what)) stat = 'bashCost';
    else if (/^sneak$/.test(what)) stat = 'sneakCost';
    else if (/^(?:non core combat )?abilities(?: are)?$/.test(what) || what === '') {
      if (resource === 'magicka') stat = 'magickaCost';
      else if (resource === 'stamina') stat = 'staminaCost';
      else if (resource === 'ultimate') stat = 'ultimateCost';
      else if (resource.startsWith('health, magicka, stamina, and ultimate')) stat = ['abilityCost', 'ultimateCost'];
      else if (/non core combat/.test(what)) return conditional(raw, { type: 'abilityCategory', detail: 'non Core Combat abilities' });
      else stat = 'abilityCost';
    } else if (/^(magicka abilities)$/.test(what)) stat = 'magickaCost';
    else if (/^(stamina abilities)$/.test(what)) stat = 'staminaCost';
    else if (/^ultimate abilities$/.test(what)) stat = 'ultimateCost';
    else if (/^all abilities$/.test(what)) stat = 'abilityCost';
    else {
      const proc = [{ kind: 'proc', raw, condition: { type: 'abilityCategory', detail: what } }];
      const r = finish(proc, m[6], raw, (x) => x, conds, depth);
      return r.effects.some((e) => e.stat) ? { status: 'mixed', effects: r.effects } : { status: 'conditional', effects: proc };
    }
    const [pc, rem] = perClause(m[6].trim());
    return done(mk(stat, value, kind, mergeCond(base, pc), raw), rem);
  }
  if ((m = rest.match(/^(Reduces?|Increases?) the Movement Speed (bonus of Sprint|penalty of Sneak) by ([\d.]+)%(.*)$/i))) {
    const stat = /bonus of Sprint/i.test(m[2]) ? 'sprintSpeed' : 'sneakSpeedPenalty';
    const sign = /^Reduces?/i.test(m[1]) ? -1 : 1;
    const [pc, rem] = perClause(m[4].trim());
    return done(mk(stat, toNum(m[3]) * sign, 'percent', mergeCond(base, pc), raw), rem);
  }
  if ((m = rest.match(/^Ignore the Movement Speed penalty of Sneak/i))) return done(mk('sneakSpeedPenalty', -100, 'percent', base, raw), '');
  if ((m = rest.match(/^Increases your movement speed when Sprinting by ([\d.]+)%(.*)$/i))) {
    const [pc, rem] = perClause(m[2].trim());
    return done(mk('sprintSpeed', toNum(m[1]), 'percent', mergeCond(base, pc), raw), rem);
  }
  if ((m = rest.match(/^Increases? your out of combat Movement Speed by ([\d.]+)%(.*)$/i))) {
    const [pc, rem] = perClause(m[2].trim());
    return done(mk('movementSpeed', toNum(m[1]), 'percent', mergeCond(mergeCond(base, pc), { type: 'outOfCombat' }), raw), rem);
  }
  if ((m = rest.match(new RegExp(`^Each (axe|mace|sword|dagger) increases your (${STAT_ALT})(?: rating)? by ${NUM}(%)?`, 'i')))) {
    return { status: 'ok', effects: mk(statFor(m[2]), toNum(m[3]), m[4] ? 'percent' : 'flat', mergeCond(base, { type: 'weaponTypeCount', weaponType: m[1].toLowerCase() }), raw) };
  }
  if ((m = rest.match(/^Grants a bonus based on the type of weapon equipped:?\s*(.*)$/i))) {
    const effs = [];
    for (const p of m[1].split(/(?<=\.)\s+(?=(?:Each|Swords|Axes|Maces|Battle Axes|Mauls|Greatswords) )/)) effs.push(...parseSentence(p, conds, depth + 1).effects);
    return { status: effs.length ? 'ok' : 'unparsed', effects: effs };
  }
  if ((m = rest.match(/^Each piece of (Light|Medium|Heavy) Armor does the following:\s*(.*)$/i))) {
    const weight = m[1].toLowerCase();
    const effs = [];
    let anyStat = false; let anyGap = false;
    for (const p of m[2].split(/\s+(?=(?:Reduces|Increases|Decreases)\b)/)) {
      const r = parseSentence(p.trim().replace(/\.$/, ''), [...conds, { type: 'armorPieces', weight }], depth + 1);
      if (r.status === 'unparsed') anyGap = true;
      if (r.effects.some((e) => e.stat)) anyStat = true;
      effs.push(...r.effects);
    }
    return { status: anyGap ? 'partial' : (anyStat ? 'ok' : 'unparsed'), effects: effs };
  }
  // damage taken from a category of attack
  if ((m = rest.match(/^(Reduces?|Increases?|Decreases?) (?:your |the )?damage (?:you take|taken) from (Magical|Martial|non-player|Players|Area of Effect|area|single target|damage over time|direct damage) attacks by ([\d.]+)%(.*)$/i))) {
    const sign = /^Reduces?|^Decreases?/i.test(m[1]) ? -1 : 1;
    const cat = m[2].toLowerCase();
    const stat = cat === 'magical' ? 'damageTakenMagical' : cat === 'martial' ? 'damageTakenMartial' : null;
    if (!stat) return conditional(raw, { type: 'attackCategory', detail: `damage taken from ${cat} attacks` });
    const [pc, rem] = perClause(m[4].trim());
    return done(mk(stat, toNum(m[3]) * sign, 'percent', mergeCond(base, pc), raw), rem);
  }
  if ((m = rest.match(/^(Reduces?|Increases?) (?:your |the )?damage (?:you take|taken) from Players by ([\d.]+)%/i))) return conditional(raw, { type: 'target', detail: 'attacker is a player' });

  // Generic: "Increases your X by N[%] [per ...]" with optional second clause "and Y by M[%]"
  const VERB = '(?:Increases?|Grants?|Gain|Raises?|Reduces?|Decreases?|Lowers?|Improves?|Boosts?)';
  const GEN = new RegExp(`^${VERB} (?:your |the |you |all )?(?:(?:amount of )?)(${STAT_ALT})(?: rating)?(?: by (?:up to )?)${RANGE}(%)?(?: meters?)?(?:(?:,| and|, and) (?:your |the |its )?(?:amount of )?(${STAT_ALT})(?: rating)? by (?:up to )?${RANGE}(%)?)?(.*)$`, 'i');
  if ((m = rest.match(GEN))) {
    const negative = /^(Reduces?|Decreases?|Lowers?)/i.test(m[0]);
    const sign = negative ? -1 : 1;
    const stat = statFor(m[1]);
    const value = rangeMax(m[2], m[3]) * sign;
    const kind = m[4] ? 'percent' : 'flat';
    let tail = (m[9] || '').trim();
    const effs = mk(stat, value, kind, base, raw);
    if (m[5]) effs.push(...mk(statFor(m[5]), rangeMax(m[6], m[7]) * sign, m[8] ? 'percent' : 'flat', base, raw));
    if (COMBAT_TAIL.test(tail) && !/^(?:for each|per) /i.test(tail)) return conditional(raw, { type: /^(?:to|with|against|from|in|towards)/i.test(tail) ? 'attackCategory' : 'combat', detail: tail.slice(0, 80) });
    const [pc, rem] = perClause(tail);
    if (pc) effs.forEach((e) => { e.condition = mergeCond(e.condition, pc); });
    return done(effs, rem);
  }
  // "Increases your Weapon Damage and Spell Damage by up to 2000, based on ..."  (by up to) handled above
  if (/^Reduces the severity of the Health Recovery determent/i.test(rest)) return { status: 'ok', effects: [{ stat: 'vampireUnnaturalResistance', value: 1, kind: 'flat', condition: null, raw }] };
  if (/^(?:Increases?|Reduces?|Decreases?) (?:the )?(?:size of your detection area|detection radius|radius you can be detected|your detection radius)/i.test(rest)) return conditional(raw, { type: 'state', detail: 'stealth detection radius' });
  if (/experience gain|duration of any|Allows you|Increases your chance to successfully|swimming|inspiration|alliance points|gold gain|fall damage|lava|Consumed drinks duration|durability|Increases your gold|repairing|Wayshrine|treasure|fenced|furnishing|pickpocketing|Soul Gem|fish|resurrect|Mount Speed|harvest/i.test(rest)) return conditional(raw, { type: 'state', detail: 'non combat' });
  if (PROC_HINTS.test(rest)) return conditional(raw, { type: 'combat', detail: rest.slice(0, 80) });
  if (/(Physical|Flame|Frost|Shock|Magic|Poison|Disease|Bleed) Damage by \d+%/i.test(rest)) return conditional(raw, { type: 'attackCategory', detail: rest.slice(0, 80) });
  return { status: 'unparsed', effects: [{ kind: 'unparsed', raw }] };
}

function finish(effs, tail, raw, withBs, conds, depth) {
  const t = (tail || '').replace(/^[.,;]?\s*/, '').replace(/\.$/, '').trim();
  if (!t) return { status: 'ok', effects: withBs(effs) };
  // explanatory restatement: "..., increasing your chance to critically strike by 2% per ability"
  if (/^(?:increasing|reducing|decreasing|granting|meaning|which)\b/i.test(t) && !/\b(if|when|while|after|against)\b/i.test(t)) return { status: 'ok', effects: withBs(effs) };
  if (/^(?:and|but) (?:increases|reduces|decreases|grants|gain|its|the|your)/i.test(t) && depth < 4) {
    const r = parseSentence(t.replace(/^(?:and|but) /i, '').replace(/^(?:its|the) /i, ''), conds, depth + 1);
    if (r.effects.some((e) => e.stat || e.buff)) return { status: (r.status === 'ok' || r.status === 'mixed') ? (effs.every((e) => e.stat || e.buff) ? 'ok' : 'mixed') : 'partial', effects: withBs([...effs, ...r.effects]) };
    if (r.status === 'conditional') return { status: 'mixed', effects: withBs([...effs, ...r.effects]) };
  }
  if (COMBAT_TAIL.test(t) || PROC_HINTS.test(t)) {
    return { status: 'conditional', effects: effs.map((e) => ({ kind: 'proc', raw, condition: mergeCond(e.condition, { type: 'combat', detail: t.slice(0, 80) }) })) };
  }
  return { status: 'partial', effects: withBs(effs), remainder: t };
}

function parseBuffList(s) {
  const out = [];
  let tier = null;
  for (const tok of s.replace(/,/g, ' , ').split(/\s+/)) {
    if (tok === 'Major' || tok === 'Minor') tier = tok;
    else if (/^[A-Z][a-z]+$/.test(tok) && tier && !['Increases', 'Increasing', 'Reducing', 'The', 'Protection'].includes(tok)) out.push(`${tier} ${tok}`);
    else if (tok === 'Protection' && tier) out.push(`${tier} Protection`);
    else if (tok === 'and' || tok === ',') continue;
    else break;
  }
  return out;
}

export function resolveBrackets(text) {
  return text.replace(/\[\s*([\d.,]+(?:\s*\/\s*[\d.,]+)+)\s*\]/g, (_, inner) => String(lastOfBracket(inner)));
}
export function splitSentences(text) {
  return text.replace(/\s+/g, ' ').split(/(?<=\.)\s+(?=[A-Z("])/).map((s) => s.trim()).filter(Boolean);
}

/** Parse a tooltip or bonus text into effects. */
export function parseText(textIn) {
  const text = resolveBrackets(String(textIn || ''));
  const { text: stripped, conds } = stripPrefixConditions(text);
  const sentences = splitSentences(stripped);
  const results = [];
  for (const s of sentences) {
    const r = parseSentence(s, conds);
    if (r.status === 'battleSpiritAlt') {
      const prev = [...results].reverse().find((x) => x.effects.some((e) => e.stat));
      if (prev) {
        const cond = (active) => ({ type: 'battleSpirit', active, scope: r.alt.scope });
        const alt = prev.effects.filter((e) => e.stat).map((e) => ({ ...e, value: r.alt.value, condition: mergeCond(e.condition, cond(true)) }));
        prev.effects.forEach((e) => { if (e.stat) e.condition = mergeCond(e.condition, cond(false)); });
        prev.effects.push(...alt);
      }
      results.push({ text: s, status: 'ok', effects: [] });
      continue;
    }
    results.push({ text: s, status: r.status, effects: r.effects, remainder: r.remainder });
  }
  const effects = results.flatMap((r) => r.effects);
  const statuses = results.map((r) => r.status).filter((x) => x !== 'flavor' && x !== 'empty');
  let status;
  if (!statuses.length) status = 'empty';
  else if (statuses.some((x) => x === 'unparsed')) status = 'unparsed';
  else if (statuses.some((x) => x === 'partial')) status = 'partial';
  else if (effects.some((e) => e.stat || e.buff)) status = statuses.some((x) => x === 'conditional') ? 'mixed' : 'ok';
  else status = 'proc';
  return { status, effects, sentences: results, prefixConditions: conds };
}
