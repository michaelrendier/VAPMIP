// Ainulindale field constants — match monad.py exactly
export const OMEGA_ZS = 0.56714;   // Lambert W fixed point W(1) — VEV, idle RPM
export const D_STAR   = 0.24600;   // natural unit of Universal Native Space
export const LN10     = Math.LN10; // decimal↔prime impedance bridge
export const GAP      = 0.000707;  // information-theoretic gap (OMEGA_ZS - d*×LN10)
export const PHI      = 1.6180339887498948; // golden ratio — word walk step

export const OPERATORS: Record<number, string> = {
  0: 'identity', 1: 'negate',      2: 'bind',        3: 'name',
  4: 'apply',    5: 'abstract',    6: 'branch',       7: 'iterate',
  8: 'recurse',  9: 'allocate',    10: 'query',       11: 'dereference',
  12: 'compose', 13: 'parallelize',14: 'interrupt',   15: 'emit',
};

// Grammatical role → firing priority (piston order, v1.3)
export const DIM_ROLE: Record<number, number> = {
  3: 0,  // noun      — fires first  (name)
  4: 1,  // verb                     (apply)
  5: 2,  // descriptive              (abstract)
  6: 3,  // predicate/negation       (branch)
  2: 4,  // connective               (bind)
  7: 5,  // temporal                 (iterate)
  8: 5,  // pronominal               (recurse)
  9: 5,  // discourse thread         (allocate)
  10: 6, // question/thematic        (query)
  11: 6, // anaphor                  (dereference)
  12: 6, // presupposition           (compose)
  13: 7, // gestalt/weight           (parallelize)
  14: 7, // affect                   (interrupt)
  15: 7, // meta-discourse           (emit)
  0: 8,  // scalar bias — last       (identity)
  1: 8,  // gematria — last          (negate)
};

export const PRONOUNS = new Set([
  'he','she','it','they','them','him','her','his','hers','its','their',
  'theirs','this','that','these','those','i','me','my','mine','we','us','our',
]);
