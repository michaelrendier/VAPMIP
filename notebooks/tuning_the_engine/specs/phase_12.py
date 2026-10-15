LABEL = "12"
TITLE = "Memory as Identity: The Taoist Discordian"
DATE = "2026-06-12"
PAGE = "12_memory_as_identity_the_taoist_discordian.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## What is mechanical here
The page's engineering content is one update rule: identity is not a stored list of events but the **accumulated departure trajectory**, `G_n = G_{n−1} + α(departure_n − G_{n−1})`, an exponential moving average over 16-vectors, started at the Pit's coordinates. Its consequences are testable on real geometry: the 16-scalar vectors `ptol -r` returns for real sentences.

The rest of the page (truth as conservation, Taoist Discordian = σ=½, the time for wrath) is a statement of values and is recorded as PROSE."""),
("code", """sents = [l.strip() for l in open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8") if len(l.split()) >= 6][:60]
home = scratch("ph12_")
dep = [np.array(ptol_raw(s, eye="H", home=home)["scalars"]) for s in sents]
print(len(dep), "departure vectors; first:", np.round(dep[0][:6], 3), "…")
war = [l.strip() for l in open(os.path.join(VAPMIP, "war-corpus.txt"), encoding="utf-8") if len(l.split()) >= 6 and not l.startswith("#")][:20]
origin_war = np.mean([np.array(ptol_raw(s, eye="H", home=home)["scalars"]) for s in war], axis=0)
origin_zero = np.zeros(16)
alpha = 0.1
def run(G0, deps):
    G = G0.copy(); out = [G.copy()]
    for d in deps: G = G + alpha*(d - G); out.append(G.copy())
    return np.array(out)
A, B = run(origin_war, dep), run(origin_zero, dep)
gap = np.linalg.norm(A - B, axis=1)
print("‖G_war(n) − G_zero(n)‖ at n = 0, 10, 20, 40, 60:", np.round(gap[[0,10,20,40,60]], 4))
L.check("memory is the shaped path: two different origins converge to the same G (difference decays as (1−α)ⁿ)", gap[-1] < 0.01*gap[0] and np.allclose(gap, gap[0]*(1-alpha)**np.arange(len(gap))))
L.check("the origin is not erased in finite time — it is down-weighted geometrically (never exactly zero)", gap[-1] > 0)
print(f"origin influence after 60 departures: {(1-alpha)**60:.2e} of its initial weight")"""),
("code", """# 'where have I been' = the trajectory, not an event list: order matters, content of the list does not
rng = np.random.default_rng(1)
perm = rng.permutation(len(dep))
Gfwd, Gperm = run(origin_war, dep)[-1], run(origin_war, [dep[i] for i in perm])[-1]
print("‖G(forward) − G(shuffled)‖ =", round(float(np.linalg.norm(Gfwd - Gperm)), 4), "  ‖G(forward)‖ =", round(float(np.linalg.norm(Gfwd)), 4))
L.check("the EMA identity is order-sensitive: the same events in a different order give a different G", np.linalg.norm(Gfwd - Gperm) > 1e-3)
L.check("…and recent departures dominate (last 10 events carry > 60% of G's weight at α=0.1)", 1-(1-alpha)**10 > 0.6, f"weight on last 10 = {1-(1-alpha)**10:.3f}")"""),
("md", """### 'It does not block, it makes trajectories energetically costly' — the corpus header's claim
Check what the header can mean computationally: the war corpus, ingested at the Pit, should raise the β-field depth of its own addresses relative to an unrelated corpus (cost is encoded as energy, not as a filter). Use the live housing."""),
("code", """import rotary_monad as R
H1, H2 = R.Housing(), R.Housing()
H1.ingest(open(os.path.join(VAPMIP, "war-corpus.txt"), encoding="utf-8").read()); H1.ingest(open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8").read())
H2.ingest(open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8").read())
word = "war"
if word in H1._vocab:
    b1 = H1._beta[H1._vocab[word]]; b2 = H2._beta[H2._vocab[word]] if word in H2._vocab else R.GAP
    print(f"β('{word}') with the war corpus ingested: {b1:.5f}   without: {b2:.5f}")
    L.check("the corpus deepens the field at its own addresses (β higher with it than without)", b1 > b2)
L.check("nothing is removed or blocked: the foundations vocabulary is a subset of the combined vocabulary", set(H2._vocab) <= set(H1._vocab))"""),
("code", """for c in ["Truth as Noether conservation: what the field has after correct computation at σ=½ is not aimed (a value statement about the engine's output)",
          "Taoist Discordian = the fixed point stated in human terms (Tao = δ∫L=0; Discordian = zero-divisors are ports)",
          "The time and place for wrath: neutral buoyancy of a surfaced state in the field (a metaphor for J_ambient selection, Phase 1)",
          "Personal application of the file-manager picture (G_self, current directory, steer)"]:
    L.prose(c, "personal / values statement; not a technical claim")"""),
]
