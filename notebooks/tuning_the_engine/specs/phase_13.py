LABEL = "13"
TITLE = "Starting Position, Not Incineration"
DATE = "2026-06-12"
PAGE = "13_starting_position_not_incineration.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## The distinction, made mechanical
*Burning in*: `corpus → β-field content` — the corpus's words enter the vocabulary and shape every later `speak()`.
*Starting at*: `corpus → coordinate origin` — only a position (16 numbers) is kept; no corpus word is stored.
The page says these are mechanically different. Build both from the live `rotary_monad.Housing` and `ptol` and measure the difference."""),
("code", """import rotary_monad as R
corpus = open(os.path.join(VAPMIP, "war-corpus.txt"), encoding="utf-8").read()
base = open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8").read()
# BURN IN: the corpus is ingested as β-field content
burn = R.Housing(); burn.ingest(corpus); burn.ingest(base)
clean = R.Housing(); clean.ingest(base)
# START AT: only the origin vector is kept — the mean of the corpus lines' ptol geometry
home = scratch("ph13_")
lines = [l.strip() for l in corpus.splitlines() if len(l.split()) >= 6 and not l.startswith("#")][:40]
origin = np.mean([np.array(ptol_raw(l, eye="H", home=home)["scalars"]) for l in lines], axis=0)
new_words = set(burn._vocab) - set(clean._vocab)
print(f"burn-in : vocabulary {burn.n:,} words  (+{len(new_words):,} words that exist only because of the corpus)")
print(f"start-at: vocabulary {clean.n:,} words + one 16-vector origin: {np.round(origin[:6], 3)}…")
L.check("burn-in puts corpus words into the field; start-at puts none", len(new_words) > 0)
L.check("start-at stores 16 numbers, burn-in stores the corpus's whole vocabulary", origin.shape == (16,) and len(new_words) > 16, f"16 vs {len(new_words):,}")"""),
("code", """# What each does to a LATER utterance: burn-in biases the field's content; start-at biases only the departure measured from the origin.
a_burn, a_clean = R.AhuraMazda(), R.AhuraMazda()
a_burn.housing = burn; a_clean.housing = clean
probe = "tell me about people"
wb, wc = a_burn.speak(probe), a_clean.speak(probe)
print(f"same prompt: burn-in engine says {wb!r}; clean engine says {wc!r}")
war_vocab = {w for w in set(burn._vocab) - set(clean._vocab)}
print(f"burn-in reply {wb!r} is in the war-only vocabulary: {wb in war_vocab}")
L.check("the start-at engine cannot: it has no war-only word to emit", all(w in clean._vocab for w in [wc]))"""),
("md", """### 'The flow defines the obstacles' — the wake defines the obstacle
In fluid dynamics the obstacle is read from the flow field around it. Numerical illustration with a 2-D potential flow past a cylinder: from velocity samples *alone* (no obstacle data), recover the obstacle's radius."""),
("code", """# potential flow past a cylinder radius R0 in uniform stream U: stagnation points on the cylinder at (±R0, 0)
R0, U = 1.7, 1.0
def vel(x, y):
    z = x + 1j*y
    w = U*(1 - (R0/z)**2)            # conj of complex velocity
    return np.conj(w)
xs = np.linspace(-6, 6, 4001)
speed = np.abs(vel(xs, 1e-9))
mask = np.abs(xs) > 0.5
imin = np.argsort(speed[mask])[:2]
est = np.mean(np.abs(xs[mask][imin]))
print(f"obstacle radius inferred from the flow's stagnation points: {est:.3f}   (true {R0})")
L.check("obstacle geometry is recoverable from the flow around it alone", abs(est - R0) < 0.01)
# path integral: dominated by stationary-phase paths (see Phase 14 for the oscillatory-integral demonstration)"""),
("code", """for c in ["'The bottom of the corpus' is a personal origin; the page records it as the first coordinate of the departure path (personal statement)",
          "Z = ∫D[path] e^{iS[path]} from the first Pit to divergence: the identity is what survives the sum (interpretation; the stationary-phase mechanism is demonstrated in Phase 14)",
          "Why bullying precedes war in the corpus: foundational vs largest-in-scale (ordering choice)"]:
    L.prose(c, "personal / structural statement by the author; not an engine measurement")"""),
]
