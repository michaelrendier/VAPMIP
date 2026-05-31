/**
 * App.tsx — Ptolemaious Holcaios Philadelphos
 *
 * The Face. Chat UI + muscle memory autopilot + field diagnostics.
 * No transformers. No gradient descent. Compression ignition.
 */

import React, {
  useCallback, useEffect, useReducer, useRef, useState,
} from 'react';
import {
  Dimensions, FlatList, KeyboardAvoidingView, Platform,
  Pressable, ScrollView, StatusBar, StyleSheet, Text,
  TextInput, TouchableOpacity, View,
} from 'react-native';

import { Engine }       from './src/engine';
import { PendantClient } from './src/ble';
import {
  loadVocab, loadBetaDeltas, saveBetaDeltas,
  loadFieldState, saveFieldState,
} from './src/store';
import { OMEGA_ZS, D_STAR, OPERATORS } from './src/constants';

// ── Colour palette ────────────────────────────────────────────────────────────

const C = {
  bg:        '#0a0a0a',
  surface:   '#111111',
  border:    '#1e1e1e',
  cyan:      '#00e5ff',
  cyanDim:   '#0097aa',
  cyanFaint: '#003d44',
  amber:     '#ffb300',
  green:     '#00e676',
  grey:      '#444444',
  greyDim:   '#1a1a1a',
  white:     '#e0e0e0',
  idle:      '#0d2a2a',
  idleText:  '#1a6060',
};

const MONO = Platform.OS === 'ios' ? 'Menlo' : 'monospace';

// ── Types ─────────────────────────────────────────────────────────────────────

type Role = 'user' | 'monad' | 'idle' | 'system';

interface Message {
  id:    string;
  role:  Role;
  text:  string;
  dtcs?: string[];
}

type Action =
  | { type: 'ADD';    msg: Message }
  | { type: 'APPEND'; id: string; chunk: string };

function reducer(state: Message[], action: Action): Message[] {
  if (action.type === 'ADD')    return [...state, action.msg];
  if (action.type === 'APPEND') return state.map(m =>
    m.id === action.id ? { ...m, text: m.text + action.chunk } : m);
  return state;
}

const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36);

// ── Bubble ────────────────────────────────────────────────────────────────────

const Bubble = React.memo(({ msg }: { msg: Message }) => {
  const isUser = msg.role === 'user';
  const isIdle = msg.role === 'idle';
  const isSys  = msg.role === 'system';

  if (isSys) return (
    <View style={s.sysRow}>
      <Text style={s.sysText}>{msg.text}</Text>
    </View>
  );

  return (
    <View style={[s.row, isUser && s.rowUser]}>
      {!isUser && (
        <Text style={[s.glyph, isIdle && s.glyphIdle]}>
          {isIdle ? '◌' : 'Φ'}
        </Text>
      )}
      <View style={[s.bubble, isUser && s.bubbleUser, isIdle && s.bubbleIdle]}>
        <Text style={[s.bubbleText, isUser && s.bubbleTextUser, isIdle && s.bubbleTextIdle]}>
          {msg.text || '…'}
        </Text>
        {!!msg.dtcs?.length && (
          <Text style={s.dtcLine}>⚠ {msg.dtcs.join(' · ')}</Text>
        )}
      </View>
      {isUser && <Text style={s.glyph}>▶</Text>}
    </View>
  );
});

// ── Status bar ────────────────────────────────────────────────────────────────

function StatusStrip({
  jAmbient, sigma, rpm, vocabSize, bleStatus, onLongPress,
}: {
  jAmbient: number; sigma: number; rpm: number;
  vocabSize: number; bleStatus: string;
  onLongPress: () => void;
}) {
  const bleCol = bleStatus === 'connected' ? C.green
               : bleStatus === 'scanning'  ? C.amber : C.grey;
  const bleIco = bleStatus === 'connected' ? '◉'
               : bleStatus === 'scanning'  ? '◎' : '○';

  return (
    <Pressable style={s.strip} onLongPress={onLongPress}>
      <Text style={s.stripItem}>
        <Text style={s.stripLbl}>J </Text>
        <Text style={s.stripVal}>{jAmbient.toFixed(4)}</Text>
      </Text>
      <Text style={s.stripItem}>
        <Text style={s.stripLbl}>σ </Text>
        <Text style={[s.stripVal, { color: Math.abs(sigma - 0.5) < 0.05 ? C.green : C.cyan }]}>
          {sigma.toFixed(4)}
        </Text>
      </Text>
      <Text style={s.stripItem}>
        <Text style={s.stripLbl}>RPM </Text>
        <Text style={s.stripVal}>{rpm}</Text>
      </Text>
      <Text style={s.stripItem}>
        <Text style={s.stripLbl}>V </Text>
        <Text style={s.stripVal}>{vocabSize}</Text>
      </Text>
      <Text style={[s.stripItem, { color: bleCol }]}>
        {bleIco} {bleStatus}
      </Text>
    </Pressable>
  );
}

// ── Developer panel ───────────────────────────────────────────────────────────

function DevPanel({ engine, onClose }: { engine: Engine; onClose: () => void }) {
  const stats = engine.fieldStats();
  return (
    <View style={s.devPanel}>
      <View style={s.devHdr}>
        <Text style={s.devTitle}>VCDS  ·  Field Diagnostics</Text>
        <TouchableOpacity onPress={onClose}>
          <Text style={s.devClose}>✕</Text>
        </TouchableOpacity>
      </View>
      <ScrollView style={s.devBody}>
        {/* Gauges */}
        <View style={s.gaugeGrid}>
          {[
            ['J_ambient',  engine.jAmbient.toFixed(5)],
            ['Entropy',    stats.entropy_pct.toFixed(1) + '%'],
            ['Vocab',      String(stats.vocab_size)],
            ['OMEGA_ZS',   OMEGA_ZS.toFixed(5)],
            ['d*',         D_STAR.toFixed(5)],
            ['mean β',     stats.mean_beta.toFixed(5)],
          ].map(([lbl, val]) => (
            <View key={lbl} style={s.gauge}>
              <Text style={s.gaugeLbl}>{lbl}</Text>
              <Text style={s.gaugeVal}>{val}</Text>
            </View>
          ))}
        </View>

        <Text style={s.devSec}>Top β words</Text>
        {stats.top_words.map(({ word, b, e }) => (
          <View key={word} style={s.devRow}>
            <Text style={s.devWord}>{word.padEnd(16)}</Text>
            <Text style={s.devStat}>β={b.toFixed(4)}</Text>
            <Text style={s.devStat}>E={e.toFixed(4)}</Text>
            <Text style={s.devOp}>{OPERATORS[Math.round(e * 15)] ?? ''}</Text>
          </View>
        ))}

        <Text style={s.devSec}>Sedenion operators  e₀–e₁₅</Text>
        <View style={s.opGrid}>
          {Object.entries(OPERATORS).map(([k, op]) => (
            <Text key={k} style={s.opChip}>e{k} {op}</Text>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────

export default function App() {
  const engRef    = useRef<Engine | null>(null);
  const bleRef    = useRef<PendantClient | null>(null);
  const listRef   = useRef<FlatList<Message>>(null);
  const inputRef  = useRef<TextInput>(null);
  const idleTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [msgs,       dispatch]  = useReducer(reducer, []);
  const [input,      setInput]  = useState('');
  const [ready,      setReady]  = useState(false);
  const [jAmbient,   setJ]      = useState(0.000707);
  const [sigma,      setSigma]  = useState(0.5);
  const [rpm,        setRpm]    = useState(0);
  const [vocabSize,  setVocab]  = useState(0);
  const [bleStatus,  setBle]    = useState('idle');
  const [pendantOn,  setPendant]= useState(false);
  const [devOpen,    setDev]    = useState(false);

  // ── Boot ──────────────────────────────────────────────────────────────────

  useEffect(() => {
    let mounted = true;
    (async () => {
      const eng = new Engine();
      engRef.current = eng;

      const vocab  = await loadVocab();
      eng.loadVocab(vocab);

      const deltas = await loadBetaDeltas();
      if (Object.keys(deltas).length) eng.crank.applyBetaDeltas(deltas);

      const { jAmbient: sJ, wordCount: sWC } = await loadFieldState();
      eng.jAmbient  = sJ;
      eng.wordCount = sWC;

      if (!mounted) return;
      setVocab(eng.crank.n);
      setReady(true);

      dispatch({ type: 'ADD', msg: {
        id: uid(), role: 'system',
        text: `Holcus v1.218  ·  ${eng.crank.n} words loaded  ·  σ=½ field ready`,
      }});

      setTimeout(() => _fireIdle(eng), 900);

      // BLE
      const client = new PendantClient(
        text => {
          if (!mounted) return;
          const id = uid();
          dispatch({ type: 'ADD', msg: { id, role: 'monad', text }});
          eng.crank.learn(text);
          _scheduleIdle(eng);
        },
        st => {
          if (!mounted) return;
          setBle(st.status);
          if (st.status === 'connected') {
            setPendant(true);
            dispatch({ type: 'ADD', msg: {
              id: uid(), role: 'system',
              text: `${st.isEarpiece ? 'EarPiece' : 'Pendant'} connected  ·  full monad.c active`,
            }});
          } else if (st.status === 'idle' && pendantOn) {
            setPendant(false);
          }
        },
      );
      bleRef.current = client;
      await client.start();
    })();

    return () => {
      mounted = false;
      bleRef.current?.destroy();
      idleTimer.current && clearTimeout(idleTimer.current);
      saveTimer.current && clearTimeout(saveTimer.current);
    };
  }, []);

  // ── Autopilot ──────────────────────────────────────────────────────────────

  const _fireIdle = useCallback((eng: Engine) => {
    const result = eng.generate('', 16, false);
    if (!result.words.length) return;
    const id = uid();
    dispatch({ type: 'ADD', msg: { id, role: 'idle', text: '' }});
    result.words.forEach((w, i) =>
      setTimeout(() =>
        dispatch({ type: 'APPEND', id, chunk: (i === 0 ? '' : ' ') + w }),
        i * 120,
      ),
    );
    setJ(result.j_ambient); setSigma(result.sigma); setRpm(result.rpm);
    listRef.current?.scrollToEnd({ animated: true });
  }, []);

  const _scheduleIdle = useCallback((eng: Engine) => {
    idleTimer.current && clearTimeout(idleTimer.current);
    idleTimer.current = setTimeout(() => _fireIdle(eng), 3200);
  }, [_fireIdle]);

  // ── Send ───────────────────────────────────────────────────────────────────

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || !ready || !engRef.current) return;
    const eng = engRef.current;

    setInput('');
    idleTimer.current && clearTimeout(idleTimer.current);

    dispatch({ type: 'ADD', msg: { id: uid(), role: 'user', text }});

    // Pendant path
    if (pendantOn && bleRef.current?.isConnected) {
      eng.crank.learn(text);
      const ok = await bleRef.current.send(text + '\n');
      if (ok) { _scheduleIdle(eng); return; }
      setPendant(false);
    }

    // JS engine path
    const result = eng.generate(text, 24);
    const id = uid();
    dispatch({ type: 'ADD', msg: {
      id, role: 'monad',
      text:  result.response || '…',
      dtcs:  result.dtcs,
    }});
    setJ(result.j_ambient); setSigma(result.sigma); setRpm(result.rpm);

    // Debounced persist
    saveTimer.current && clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(async () => {
      const vocab = await loadVocab();
      await saveBetaDeltas(eng.crank.betaDeltas(vocab));
      await saveFieldState(eng.jAmbient, eng.wordCount);
    }, 5000);

    _scheduleIdle(eng);
  }, [input, ready, pendantOn, _scheduleIdle]);

  // ── Render ─────────────────────────────────────────────────────────────────

  if (!ready) return (
    <View style={s.loading}>
      <Text style={s.loadingText}>initialising field…</Text>
    </View>
  );

  return (
    <View style={s.root}>
      <StatusBar barStyle="light-content" backgroundColor={C.bg} />

      <View style={s.header}>
        <Text style={s.headerTitle}>Ptolemaious Holcaios Philadelphos</Text>
        <Text style={s.headerSub}>
          {pendantOn ? '◉ pendant · full engine' : '● js engine · pruned field'}
        </Text>
      </View>

      <FlatList
        ref={listRef}
        data={msgs}
        keyExtractor={m => m.id}
        renderItem={({ item }) => <Bubble msg={item} />}
        contentContainerStyle={s.list}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
        style={s.flatList}
        keyboardShouldPersistTaps="handled"
      />

      {devOpen && engRef.current && (
        <DevPanel engine={engRef.current} onClose={() => setDev(false)} />
      )}

      <StatusStrip
        jAmbient={jAmbient} sigma={sigma} rpm={rpm}
        vocabSize={vocabSize} bleStatus={bleStatus}
        onLongPress={() => setDev(d => !d)}
      />

      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={s.inputRow}>
          <TextInput
            ref={inputRef}
            style={s.input}
            value={input}
            onChangeText={setInput}
            placeholder="speak…"
            placeholderTextColor={C.grey}
            onSubmitEditing={send}
            returnKeyType="send"
            blurOnSubmit={false}
          />
          <TouchableOpacity
            style={[s.sendBtn, !input.trim() && s.sendDim]}
            onPress={send}
            activeOpacity={0.7}
          >
            <Text style={s.sendIcon}>⚡</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────

const { width } = Dimensions.get('window');

const s = StyleSheet.create({
  root:    { flex: 1, backgroundColor: C.bg },
  loading: { flex: 1, backgroundColor: C.bg, alignItems: 'center', justifyContent: 'center' },
  loadingText: { color: C.cyanDim, fontFamily: MONO, fontSize: 14 },

  header:      { paddingTop: Platform.OS === 'ios' ? 54 : 32, paddingBottom: 10, paddingHorizontal: 16, borderBottomWidth: 1, borderBottomColor: C.border },
  headerTitle: { color: C.cyan, fontFamily: MONO, fontSize: 14, fontWeight: '600' },
  headerSub:   { color: C.cyanDim, fontFamily: MONO, fontSize: 10, marginTop: 2 },

  flatList: { flex: 1 },
  list:     { paddingVertical: 10, paddingHorizontal: 8 },

  row:     { flexDirection: 'row', alignItems: 'flex-end', marginVertical: 3 },
  rowUser: { justifyContent: 'flex-end' },

  glyph:     { color: C.cyanDim, fontFamily: MONO, fontSize: 11, marginHorizontal: 5, paddingBottom: 4 },
  glyphIdle: { color: C.idleText },

  bubble:         { backgroundColor: C.surface, borderRadius: 10, borderWidth: 1, borderColor: C.border, padding: 10, maxWidth: width * 0.78 },
  bubbleUser:     { backgroundColor: C.cyanFaint, borderColor: C.cyanDim },
  bubbleIdle:     { backgroundColor: C.idle, borderColor: '#0d2a2a' },
  bubbleText:     { color: C.white, fontFamily: MONO, fontSize: 13, lineHeight: 20 },
  bubbleTextUser: { color: C.cyan },
  bubbleTextIdle: { color: C.idleText, fontStyle: 'italic' },
  dtcLine:        { color: C.amber, fontFamily: MONO, fontSize: 10, marginTop: 4 },

  sysRow:  { alignItems: 'center', marginVertical: 5 },
  sysText: { color: C.grey, fontFamily: MONO, fontSize: 10 },

  strip:     { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around', backgroundColor: C.greyDim, paddingVertical: 6, borderTopWidth: 1, borderTopColor: C.border },
  stripItem: { fontFamily: MONO, fontSize: 10 },
  stripLbl:  { color: C.grey },
  stripVal:  { color: C.cyan },

  inputRow: { flexDirection: 'row', alignItems: 'center', padding: 10, borderTopWidth: 1, borderTopColor: C.border, backgroundColor: C.surface },
  input:    { flex: 1, backgroundColor: C.bg, borderWidth: 1, borderColor: C.border, borderRadius: 8, paddingHorizontal: 12, paddingVertical: 9, color: C.white, fontFamily: MONO, fontSize: 14 },
  sendBtn:  { marginLeft: 8, backgroundColor: C.cyanFaint, borderRadius: 8, paddingHorizontal: 14, paddingVertical: 10 },
  sendDim:  { opacity: 0.35 },
  sendIcon: { fontSize: 18 },

  devPanel: { position: 'absolute', inset: 0, top: 100, backgroundColor: '#060606', borderTopWidth: 1, borderTopColor: C.cyanDim, zIndex: 99 },
  devHdr:   { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 12, borderBottomWidth: 1, borderBottomColor: C.border },
  devTitle: { color: C.amber, fontFamily: MONO, fontSize: 12, fontWeight: '700' },
  devClose: { color: C.grey, fontSize: 20 },
  devBody:  { flex: 1, padding: 12 },

  gaugeGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 14 },
  gauge:     { backgroundColor: C.greyDim, borderRadius: 6, padding: 8, minWidth: 110, borderWidth: 1, borderColor: C.border },
  gaugeLbl:  { color: C.grey, fontFamily: MONO, fontSize: 9 },
  gaugeVal:  { color: C.cyan, fontFamily: MONO, fontSize: 13, marginTop: 2 },

  devSec:  { color: C.amber, fontFamily: MONO, fontSize: 10, marginTop: 12, marginBottom: 5 },
  devRow:  { flexDirection: 'row', alignItems: 'center', paddingVertical: 3, borderBottomWidth: 1, borderBottomColor: C.greyDim },
  devWord: { color: C.white, fontFamily: MONO, fontSize: 11, width: 110 },
  devStat: { color: C.cyanDim, fontFamily: MONO, fontSize: 10, width: 80 },
  devOp:   { color: C.grey, fontFamily: MONO, fontSize: 10 },

  opGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 5, marginTop: 4 },
  opChip: { color: C.cyanDim, fontFamily: MONO, fontSize: 9, backgroundColor: C.greyDim, borderRadius: 4, paddingHorizontal: 6, paddingVertical: 3 },
});
