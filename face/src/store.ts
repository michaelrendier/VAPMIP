/**
 * store.ts — Monad state persistence
 *
 * Tier 1: AsyncStorage — β-delta overlay (fast, offline, per-device)
 * Tier 2: expo-file-system — full checkpoint .bin management (skill system)
 *
 * The checkpoint system IS the human Noether conservation law for skill state.
 * Skill burning is mathematically irreversible per instance; code-reversible
 * via checkpoint. base.bin = clean ground state; post_[skill].bin = skill burned.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
// expo-file-system v56 moved legacy API — import from legacy subpath
import {
  documentDirectory,
  getInfoAsync,
  makeDirectoryAsync,
  readDirectoryAsync,
  writeAsStringAsync,
  readAsStringAsync,
} from 'expo-file-system/legacy';
import type { VocabMap } from './engine';

const DELTA_KEY       = '@holcus/beta_deltas';
const J_AMBIENT_KEY   = '@holcus/j_ambient';
const WORD_COUNT_KEY  = '@holcus/word_count';
const SKILL_INDEX_KEY = '@holcus/skills';
const CHECKPOINTS_DIR = (documentDirectory ?? '') + 'checkpoints/';

// ── β-delta overlay ───────────────────────────────────────────────────────────

export async function saveBetaDeltas(deltas: Record<string, number>): Promise<void> {
  try {
    await AsyncStorage.setItem(DELTA_KEY, JSON.stringify(deltas));
  } catch (_) {}
}

export async function loadBetaDeltas(): Promise<Record<string, number>> {
  try {
    const raw = await AsyncStorage.getItem(DELTA_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (_) { return {}; }
}

export async function saveFieldState(jAmbient: number, wordCount: number): Promise<void> {
  try {
    await AsyncStorage.multiSet([
      [J_AMBIENT_KEY,  String(jAmbient)],
      [WORD_COUNT_KEY, String(wordCount)],
    ]);
  } catch (_) {}
}

export async function loadFieldState(): Promise<{ jAmbient: number; wordCount: number }> {
  try {
    const [[, j], [, wc]] = await AsyncStorage.multiGet([J_AMBIENT_KEY, WORD_COUNT_KEY]);
    return { jAmbient: j ? parseFloat(j) : 0.000707, wordCount: wc ? parseInt(wc) : 0 };
  } catch (_) { return { jAmbient: 0.000707, wordCount: 0 }; }
}

export async function clearFieldState(): Promise<void> {
  await AsyncStorage.multiRemove([DELTA_KEY, J_AMBIENT_KEY, WORD_COUNT_KEY]);
}

// ── Skill checkpoint management ───────────────────────────────────────────────

export interface SkillRecord {
  name:       string;
  operator:   string;   // e.g. 'allocate', 'query'
  burnDate:   string;
  pre:        string;   // filename of pre-burn checkpoint
  post:       string;   // filename of post-burn checkpoint
  deltaWords: number;   // how many β-values changed
}

async function ensureCheckpointsDir(): Promise<void> {
  const info = await getInfoAsync(CHECKPOINTS_DIR);
  if (!info.exists) await makeDirectoryAsync(CHECKPOINTS_DIR, { intermediates: true });
}

export async function listSkills(): Promise<SkillRecord[]> {
  try {
    const raw = await AsyncStorage.getItem(SKILL_INDEX_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (_) { return []; }
}

export async function saveSkillRecord(record: SkillRecord): Promise<void> {
  const skills = await listSkills();
  const idx = skills.findIndex(s => s.name === record.name);
  if (idx >= 0) skills[idx] = record; else skills.push(record);
  await AsyncStorage.setItem(SKILL_INDEX_KEY, JSON.stringify(skills));
}

// Save current β-deltas as a named checkpoint JSON
export async function saveCheckpoint(
  name: string,
  deltas: Record<string, number>,
  jAmbient: number,
): Promise<string> {
  await ensureCheckpointsDir();
  const filename = `${name}_${Date.now()}.json`;
  const path     = CHECKPOINTS_DIR + filename;
  await writeAsStringAsync(
    path,
    JSON.stringify({ name, jAmbient, deltas, saved: new Date().toISOString() }),
  );
  return filename;
}

export async function loadCheckpoint(
  filename: string,
): Promise<{ deltas: Record<string, number>; jAmbient: number } | null> {
  try {
    const path = CHECKPOINTS_DIR + filename;
    const raw  = await readAsStringAsync(path);
    const data = JSON.parse(raw);
    return { deltas: data.deltas ?? {}, jAmbient: data.jAmbient ?? 0.000707 };
  } catch (_) { return null; }
}

export async function listCheckpoints(): Promise<string[]> {
  try {
    await ensureCheckpointsDir();
    const result = await readDirectoryAsync(CHECKPOINTS_DIR);
    return result.filter(f => f.endsWith('.json'));
  } catch (_) { return []; }
}

// ── Vocab JSON loader ─────────────────────────────────────────────────────────

let _cachedVocab: VocabMap | null = null;

export async function loadVocab(): Promise<VocabMap> {
  if (_cachedVocab) return _cachedVocab;
  // In production the vocab is bundled as an asset.
  // require() resolves at bundle time; cast to avoid TS module issues.
  const raw = require('../assets/vocab.json') as VocabMap;
  _cachedVocab = raw;
  return raw;
}
