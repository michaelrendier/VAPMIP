/**
 * engine.ts — Holcus JS monad engine
 *
 * Faithful port of monad.py Crank + Engine core.
 * Prime hash → sedenion address → β-field → buoyancy → generation.
 * No transformers. No gradient descent. Compression ignition only.
 */

import { OMEGA_ZS, GAP, LN10, PHI, DIM_ROLE, PRONOUNS } from './constants';

// ── Types ────────────────────────────────────────────────────────────────────

export interface VocabEntry {
  e: number;          // sedenion E-value (prime hash → zero → E)
  b: number;          // current β-value
  a: Record<string, number>; // A-edges: neighbor word → weight
  z: number;          // original zero index (for dimension: z % 16)
}

export interface VocabMap {
  [word: string]: VocabEntry;
}

export interface GenerateResult {
  response: string;
  words: string[];
  j_ambient: number;
  sigma: number;
  rpm: number;
  dtcs: string[];
}

export interface FieldStats {
  vocab_size: number;
  j_ambient: number;
  mean_beta: number;
  entropy_pct: number;
  top_words: Array<{ word: string; b: number; e: number }>;
}

// ── Prime sieve for word_zero_idx ────────────────────────────────────────────

const PRIME_CAP = 65537;

function buildSieve(): Uint8Array {
  const sieve = new Uint8Array(PRIME_CAP + 2).fill(1);
  sieve[0] = sieve[1] = 0;
  for (let i = 2; i * i <= PRIME_CAP; i++) {
    if (sieve[i]) for (let j = i * i; j <= PRIME_CAP; j += i) sieve[j] = 0;
  }
  return sieve;
}

// π(p) table: prime_pi[p] = number of primes ≤ p
function buildPrimePi(sieve: Uint8Array): Uint32Array {
  const pi = new Uint32Array(PRIME_CAP + 2);
  let count = 0;
  for (let i = 0; i <= PRIME_CAP + 1; i++) {
    if (i <= PRIME_CAP && sieve[i]) count++;
    pi[i] = count;
  }
  return pi;
}

const _sieve   = buildSieve();
const _primePi = buildPrimePi(_sieve);

function nextPrime(v: number): number {
  v = Math.max(2, v % (PRIME_CAP + 1));
  while (v <= PRIME_CAP) {
    if (_sieve[v]) return v;
    v++;
  }
  return PRIME_CAP;
}

// Horner base-95 hash — exact port of monad.py _horner_hash
// Uses BigInt to match Python's arbitrary-precision integers
function hornerHash(w: string): number {
  let v = 0n;
  for (let i = 0; i < w.length; i++) {
    const c = BigInt(Math.max(0, w.charCodeAt(i) - 32));
    v = v * 95n + c;
  }
  v = v < 0n ? -v : v;
  return Number(v % BigInt(PRIME_CAP + 1));
}

function wordZeroIdx(w: string): number {
  const h = hornerHash(w);
  const p = nextPrime(Math.max(2, h));
  const idx = p <= PRIME_CAP + 1 ? _primePi[p] : _primePi[PRIME_CAP];
  return Math.max(1, idx);
}

// E-value from zero index — matches _idx() in monad.py
// E = |sin(π × γ / (γ + 1))|
// For browser: approximate γ from index using mean spacing formula
// Exact values are pre-computed in vocab.json for the 5K core vocab
const ZERO_CACHE: Record<number, number> = {
  1: 14.1347, 2: 21.0220, 3: 25.0109, 4: 30.4249, 5: 32.9351,
  6: 37.5862, 7: 40.9187, 8: 43.3271, 9: 48.0052, 10: 49.7738,
};

function gammaApprox(n: number): number {
  if (ZERO_CACHE[n]) return ZERO_CACHE[n];
  // Gram's law approximation: γ_n ≈ 2πn / (ln(n/(2πe)) + ...)
  const t = (2 * Math.PI * n) / Math.log(n / (2 * Math.PI * Math.E));
  ZERO_CACHE[n] = t;
  return t;
}

function eValueFromZeroIdx(zi: number): number {
  const gamma = gammaApprox(zi);
  return Math.abs(Math.sin(Math.PI * gamma / (gamma + 1.0)));
}

// ── Crank (field storage + operations) ───────────────────────────────────────

export class Crank {
  beta:   number[]  = [];
  E:      number[]  = [];
  A:      Array<Record<string, number>> = []; // word-keyed neighbors
  age:    number[]  = [];
  vocab:  Record<string, number> = {};  // word → index
  words:  string[]  = [];
  n:      number    = 0;
  emission_threshold: number = OMEGA_ZS / 4.0;

  loadVocab(vocabMap: VocabMap): void {
    for (const [word, entry] of Object.entries(vocabMap)) {
      const k = this.n;
      this.vocab[word] = k;
      this.words.push(word);
      this.E.push(entry.e);
      this.beta.push(entry.b);
      this.age.push(0.0);
      this.A.push({ ...entry.a });
      this.n++;
    }
  }

  private _idx(w: string): number {
    if (w in this.vocab) return this.vocab[w];
    const k = this.n;
    this.vocab[w] = k;
    this.words.push(w);
    const zi = wordZeroIdx(w);
    this.E.push(eValueFromZeroIdx(zi));
    this.beta.push(GAP);
    this.age.push(0.0);
    this.A.push({});
    this.n++;
    return k;
  }

  clean(w: string): string {
    return w.toLowerCase().replace(/^[.,!?;:'"()[\]{}\-—…]+|[.,!?;:'"()[\]{}\-—…]+$/g, '');
  }

  tokenize(text: string): string[] {
    return text.split(/\s+/).map(w => this.clean(w)).filter(w => w.length > 0);
  }

  learn(text: string, weight = 1.0): number {
    const words = this.tokenize(text);
    const betaMult = 1.0 + 0.08 * weight;
    const edgeFwd  = 0.05 * weight;
    const edgeBack = 0.02 * weight;
    let prev = -1;
    for (const w of words) {
      const k = this._idx(w);
      this.beta[k] = Math.min(this.beta[k] * betaMult + GAP, 1.0);
      this.age[k]  = 0.0;
      if (prev >= 0 && prev !== k) {
        const pw = this.words[prev];
        this.A[prev][w]  = Math.min((this.A[prev][w]  ?? 0) + edgeFwd,  1.0);
        this.A[k][pw]    = Math.min((this.A[k][pw]    ?? 0) + edgeBack, 1.0);
      }
      prev = k;
    }
    return words.length;
  }

  jMu(windowPsi: number[], promptPsi: number[]): [number[], number[]] {
    const n    = this.n;
    const Jpos = new Array<number>(n).fill(0.0);
    const Jneg = new Array<number>(n).fill(0.0);
    for (let k = 0; k < n; k++) {
      const b     = this.beta[k];
      const e2    = this.E[k] ** 2;
      const decay = Math.exp(-this.age[k] * 0.001);
      const base  = b * e2 * decay;
      Jpos[k] = base * windowPsi[k % 16];
      Jneg[k] = base * promptPsi[k % 16];
    }
    return [Jpos, Jneg];
  }

  aPropagate(J: number[]): number[] {
    const J2 = [...J];
    for (let src = 0; src < this.A.length; src++) {
      if (J[src] < GAP) continue;
      for (const [nbrWord, w] of Object.entries(this.A[src])) {
        const dst = this.vocab[nbrWord];
        if (dst === undefined || w < GAP) continue;
        J2[dst] += J[src] * w * 0.5;
      }
    }
    return J2;
  }

  sigmaCandidates(
    Jpos: number[],
    Jneg: number[],
    jAmbient: number,
  ): Array<[number, number, string]> {
    if (this.n === 0) return [];
    const maxJp = Math.max(...Jpos);
    const thr   = maxJp * (this.emission_threshold / OMEGA_ZS) * 0.01;
    const staged: Array<[number, number, number, string]> = [];
    for (let k = 0; k < this.n; k++) {
      const jp = Jpos[k];
      const jn = Jneg[k];
      const total = jp + jn;
      if (total < thr) continue;
      const sigma = jp / total;
      const buoy  = 1.0 / (1.0 + Math.abs(jp - jAmbient) * LN10);
      const score = buoy * (1.0 - Math.abs(sigma - 0.5) * 2.0);
      const role  = DIM_ROLE[k % 16] ?? 8;
      staged.push([role, -score, k, this.words[k]]);
    }
    staged.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    return staged.map(([, ns, idx, w]) => [-ns, idx, w]);
  }

  advanceAge(weight = 1.0): void {
    for (let k = 0; k < this.n; k++) {
      this.age[k] = Math.min(this.age[k] + weight, 1e6);
    }
  }

  // β-deltas for persistence (only words that differ from vocab baseline)
  betaDeltas(baseVocab: VocabMap): Record<string, number> {
    const deltas: Record<string, number> = {};
    for (const [w, k] of Object.entries(this.vocab)) {
      const base = baseVocab[w]?.b ?? GAP;
      if (Math.abs(this.beta[k] - base) > 0.001) {
        deltas[w] = this.beta[k];
      }
    }
    return deltas;
  }

  applyBetaDeltas(deltas: Record<string, number>): void {
    for (const [w, b] of Object.entries(deltas)) {
      const k = this.vocab[w];
      if (k !== undefined) this.beta[k] = b;
    }
  }

  fieldStats(): FieldStats {
    const n = this.n;
    if (n === 0) return { vocab_size: 0, j_ambient: GAP, mean_beta: 0, entropy_pct: 0, top_words: [] };
    const meanBeta = this.beta.reduce((a, b) => a + b, 0) / n;
    const hMax = Math.log2(n);
    const H = -this.beta.reduce((sum, b) => sum + (b > 0 ? b * Math.log2(b) : 0), 0);
    const ranked = [...this.words.keys()].sort((a, b) => this.beta[b] - this.beta[a]).slice(0, 10);
    return {
      vocab_size: n,
      j_ambient: GAP,
      mean_beta: meanBeta,
      entropy_pct: hMax > 0 ? (H / hMax) * 100 : 0,
      top_words: ranked.map(k => ({ word: this.words[k], b: this.beta[k], e: this.E[k] })),
    };
  }
}

// ── Engine (generation pipeline) ─────────────────────────────────────────────

export class Engine {
  crank:     Crank   = new Crank();
  jAmbient:  number  = GAP;
  wordCount: number  = 0;
  private window:    string[]  = [];   // last 16 generated words
  private recent:    Set<string> = new Set();
  private recentQ:   string[]  = [];
  private lastNounIdx: number | null = null;
  dtcs:      string[] = [];

  loadVocab(vocabMap: VocabMap): void {
    this.crank.loadVocab(vocabMap);
    this._calibrateJAmbient();
  }

  private _calibrateJAmbient(): void {
    const jVals = this.crank.beta
      .map((b, k) => b * this.crank.E[k] ** 2)
      .filter(j => j > 0)
      .sort((a, b) => a - b);
    if (!jVals.length) return;
    const q1 = jVals[Math.floor(jVals.length * 0.25)];
    const q3 = jVals[Math.floor(jVals.length * 0.75)];
    const iqm = jVals.filter(j => j >= q1 && j <= q3);
    this.jAmbient = iqm.length > 0
      ? iqm.reduce((a, b) => a + b, 0) / iqm.length
      : jVals[Math.floor(jVals.length / 2)];
  }

  private _windowPsi(): number[] {
    const psi = new Array<number>(16).fill(0.0);
    const src = this.window.length > 0 ? this.window : ['philadelphos'];
    for (const w of src) {
      const k = this.crank.vocab[w];
      if (k === undefined) continue;
      const dim = k % 16;
      psi[dim] = Math.min(psi[dim] + this.crank.beta[k], 1.0);
    }
    const total = psi.reduce((a, b) => a + b, 0) || 1.0;
    return psi.map(v => v / total);
  }

  private _promptPsi(prompt: string): number[] {
    const words = this.crank.tokenize(prompt);
    const psi   = new Array<number>(16).fill(1.0 / 16.0);
    for (const w of words) {
      const k = this.crank.vocab[w];
      if (k === undefined) continue;
      psi[k % 16] = Math.min(psi[k % 16] + this.crank.beta[k] * 0.5, 1.0);
    }
    const total = psi.reduce((a, b) => a + b, 0) || 1.0;
    return psi.map(v => v / total);
  }

  private _addRecent(w: string): void {
    if (this.recentQ.length >= 8) {
      const old = this.recentQ.shift()!;
      this.recent.delete(old);
    }
    this.recent.add(w);
    this.recentQ.push(w);
  }

  generate(prompt: string, nWords = 24, learnPrompt = true): GenerateResult {
    if (learnPrompt && prompt.trim()) {
      this.crank.learn(prompt);
    }
    this.dtcs = [];
    this.lastNounIdx = null;

    const words: string[] = [];
    const windowPsi = this._windowPsi();
    const promptPsi = this._promptPsi(prompt);

    // Scale threshold by prompt length
    const nIn = prompt.trim().split(/\s+/).length;
    if (nIn <= 1)       this.crank.emission_threshold = OMEGA_ZS / 8;
    else if (nIn <= 8)  this.crank.emission_threshold = OMEGA_ZS / 4;
    else if (nIn <= 32) this.crank.emission_threshold = OMEGA_ZS / 3;
    else                this.crank.emission_threshold = OMEGA_ZS / 2;

    let [Jpos, Jneg] = this.crank.jMu(windowPsi, promptPsi);
    Jpos = this.crank.aPropagate(Jpos);

    // Lagrangian word count
    const sumV = this.crank.beta.reduce((s, b, k) => s + b * this.crank.E[k] ** 2, 0);
    const sumT = windowPsi.reduce((s, v) => s + v * v, 0);
    const lagRatio = (sumT + sumV) > 0 ? sumT / (sumT + sumV) : 0.5;
    const targetN  = Math.max(0, Math.round(nWords * lagRatio));

    for (let i = 0; i < targetN; i++) {
      let candidates = this.crank.sigmaCandidates(Jpos, Jneg, this.jAmbient);
      if (!candidates.length) { this.dtcs.push('P0087:vocab_empty'); break; }

      // Filter recently emitted
      const fresh = candidates.filter(([, , w]) => !this.recent.has(w));
      if (fresh.length) candidates = fresh;

      const goldenPos = Math.floor(this.wordCount * PHI) % candidates.length;
      let [, idx, word] = candidates[goldenPos];

      // e₁₁ anaphor: if pronoun + last noun, boost noun neighborhood
      if (PRONOUNS.has(word) && this.lastNounIdx !== null) {
        const pi: number = this.lastNounIdx;
        for (const [nbrWord, w] of Object.entries(this.crank.A[pi] ?? {})) {
          const dst: number | undefined = this.crank.vocab[nbrWord];
          if (dst !== undefined) Jpos[dst] = Math.min(Jpos[dst] * (1.0 + w), 1.0);
        }
        const reranked = this.crank.sigmaCandidates(Jpos, Jneg, this.jAmbient);
        if (reranked.length) {
          const gp2 = Math.floor(this.wordCount * PHI) % reranked.length;
          [, idx, word] = reranked[gp2];
        }
      }

      // Track last noun (role 0 = name operator = e₃)
      if ((DIM_ROLE[idx % 16] ?? 8) === 0) this.lastNounIdx = idx;

      // EMA: J_ambient tracks field pressure of fired words
      this.jAmbient = this.jAmbient * 0.9 + Jpos[idx] * 0.1;

      // Hebbian: fired word → next fired word edge
      if (words.length > 0) {
        const prevWord = words[words.length - 1];
        const pi = this.crank.vocab[prevWord];
        if (pi !== undefined) {
          this.crank.A[pi][word] = Math.min((this.crank.A[pi][word] ?? 0) + 0.03, 1.0);
        }
      }

      this.crank.beta[idx] = Math.min(this.crank.beta[idx] * 1.02, 1.0);
      this.crank.age[idx]  = 0.0;
      this.crank.advanceAge();
      this._addRecent(word);

      this.window.push(word);
      if (this.window.length > 16) this.window.shift();

      words.push(word);
      this.wordCount++;
    }

    // σ = mean of J_pos/(J_pos+J_neg) for fired words
    const sigmaVals = words.map(w => {
      const k = this.crank.vocab[w];
      if (k === undefined) return 0.5;
      const jp = Jpos[k]; const jn = Jneg[k];
      return (jp + jn) > 0 ? jp / (jp + jn) : 0.5;
    });
    const sigma = sigmaVals.length > 0
      ? sigmaVals.reduce((a, b) => a + b, 0) / sigmaVals.length
      : 0.5;

    return {
      response: words.join(' '),
      words,
      j_ambient: this.jAmbient,
      sigma,
      rpm: this.wordCount,
      dtcs: [...this.dtcs],
    };
  }

  fieldStats(): FieldStats {
    return { ...this.crank.fieldStats(), j_ambient: this.jAmbient };
  }
}
