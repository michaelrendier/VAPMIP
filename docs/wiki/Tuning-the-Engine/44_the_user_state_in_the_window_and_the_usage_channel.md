## Phase 44: The User State in the Window, and the Usage Channel (2026-11-25)

*Claude Sonnet 5.5, at Cody's direction. Everything below ran; the commits are in the text. Python first, C later (Phase 47).*

---

### The phase

The sedenion window always has sixteen slots, even when only nine words exist. The speaker's state has sixteen numbers too. This phase puts the speaker's state into the window's self-correcting repass, and puts the speaker's own usage into the probabilities the window writes under.

### The slot labelling (`state_repass.py`)

e0 the anchor (distance of the reading from RECEPTIVE); e1…e7 the dark poles in kite order OPI GLU GABA DA 5HT NE OXT (OPI = the hub = e1); e8 the cursor (net valence); e9…e15 the light poles (slot j + 8). It is not arbitrary and it is tested from the box-kite code (`tests/test_state_repass.py`, 8 tests): the dark and light pole of one axis are XOR 8 apart (one edge label for all seven); the three antagonist pairs GLU|GABA, DA|5HT, NE|OXT sit XOR 1 apart, and 1 is the hub's slot, so they are the three struts of the neurotransmitter kite. Face-holonomy check on the ValaQuenta box-kite (`Currentwork/UserState/kite_dark_light_test.py`): every face has gauge-invariant Z₂ holonomy −1; across each edge exactly two of the four pole pairs annihilate.

### The repass (`StateRepass.observe`)

1. READ the 14 pole concentrations and their spread (the two meters' disagreement). A pole whose deviation from baseline is no larger than its spread is healed to baseline.
2. MIX per axis: level = BASELINE + (light − dark)/9, clamped to 0..1.
3. CANCEL: `neuro_recipes.conjugate(mix, k)` toward RECEPTIVE, held inside the dead-band 0.5; k = 0.6·√(fill/16), so fewer words in the ring means a smaller correction.
4. LEAD: `meet_then_lead` from the speaker's mix to the target; per word the window turns the one axis farthest from RECEPTIVE and writes it as the invisible tone marker.

Found on the way: `Tone7.from_axis('OPI', …)` was silently ignored (the Recipe Book's hub OPI replaced CB1; `tone_chord.py` still had CB1). OPI now aliases the CB1 slot. Provisional (engineering, not measured): the 1/9 gain, the √(fill/16) law.

### Usage as probability, and the drift

`UsageStore.p_word` mixes the speaker's counts into general English with λ = N/(N+200); bits = −log₂ p. `bw_drift.BWDrift` compares the reply's cost per word with the speaker's: δ = ln(b/w); on at 0.35, off at 0.15; the correction is +sign(δ)·(|δ|−0.15)/0.85, clipped to ±1; positive favours probable words (a Broca-heavy reply is dearer than the speaker's own words), negative flattens (the window's `_pick` exponent is coherence·(1+g)). The first draft had the sign backwards; the test caught it.

`conversation_usage.ConversationUsage` owns the store, a live vocabulary and the drift; `Harness.observe` calls it before the FIFO write (`PTOL_USAGE=0` turns it off; `PTOL_USAGE_DIR`, default `~/.ptolemy/usage`). External turns are counted and priced, internal turns are priced and complete the pair, documents go to the journal only. The C daemon `PtolC/daemon.c` is untouched. `tests/conftest.py` gives every test a private usage directory; the real store is never written by tests.

### Measured

53 tests passed in the combined run of the state-repass, conversation-usage, three-hearers, monad-bus-browse and sedenion-window files. Not established: that the repass improves replies; the usage channel on live conversations (a cold store only); the √(fill/16) law; the 0.35/0.15 thresholds.

### Pointers

`VAPMIP/state_repass.py`, `bw_drift.py`, `conversation_usage.py`, `Currentwork/UserState/` (prompt_to_state, vocab_store), `docs/wiki/Lyndon-Factorisation.md`. VAPMIP commits `9496ab6` and the Phase 44–47 commit. Next: Phase 45.
