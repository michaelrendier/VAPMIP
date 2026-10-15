LABEL = "14"
TITLE = "The Indifferent Medium"
DATE = "2026-06-12"
PAGE = "14_the_indifferent_medium.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## The one computable idea: the stationary path is not rewarded, it is where phases align
The page: "the stationary action path isn't rewarded for being stationary. The medium doesn't notice. It happens to be the path where the phases align and the integral converges."
That is stationary-phase (Fresnel) asymptotics, and it can be shown directly: `∫ e^{iλ f(x)} dx` is dominated by points with `f′(x)=0` and the rest cancels."""),
("code", """from scipy.integrate import quad
def Z(lam, f, df_zero_at=None, lo=-6, hi=6, n=400001):
    x = np.linspace(lo, hi, n); y = np.exp(1j*lam*f(x))
    return np.trapezoid(y, x)
f_stat = lambda x: (x-1.0)**2            # stationary point at x=1
f_mono = lambda x: x + 0.1*x**2          # no stationary point inside [-6,6] ... f' = 1+0.2x >= -0.2 -> zero at x=-5 : keep range clear
f_mono = lambda x: 3*x + 0.1*np.sin(x)   # f' = 3 + 0.1cos x > 0 everywhere: no stationary point
rows = []
for lam in (10, 40, 160, 640):
    zs, zm = Z(lam, f_stat), Z(lam, f_mono)
    pred = math.sqrt(math.pi/lam)
    rows.append((lam, abs(zs), pred, abs(zm)))
    print(f"  λ={lam:4d}   |Z| with stationary point = {abs(zs):.4f}   (√(π/λ)={pred:.4f})    |Z| without = {abs(zm):.2e}")
L.check("with a stationary point |Z| ≈ √(π/λ) (the aligned-phase contribution)", all(abs(a-b)/b < 0.05 for _, a, b, _ in rows))
L.check("without one, |Z| is exponentially/boundary-small — the paths cancel", rows[-1][3] < 1e-2*rows[-1][1])
L.check("the aligned contribution shrinks only as λ^(-1/2) while the cancelled case collapses faster", rows[-1][3]/rows[0][3] < rows[-1][1]/rows[0][1])"""),
("md", """## The war corpus 'reframed' — a measurement the page implies
If the medium is indifferent, the field should show no direction preference toward or away from the corpus content beyond what the counts give. A neutral check: β-field depth of corpus words after ingest scales with frequency alone (a monotone function of count), i.e. the engine imposes no extra valence of its own."""),
("code", """import rotary_monad as R, collections
H = R.Housing()
text = open(os.path.join(VAPMIP, "war-corpus.txt"), encoding="utf-8").read() + open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8").read()
H.ingest(text)
cnt = collections.Counter(w.lower().strip('.,!?;:"\\'-()[]') for w in text.split())
common = [w for w, c in cnt.most_common(400) if w in H._vocab]
c_ = np.array([cnt[w] for w in common], float); b_ = np.array([H._beta[H._vocab[w]] for w in common])
from scipy.stats import spearmanr
rho = spearmanr(c_, b_).correlation
print(f"Spearman ρ(count, β) over the 400 most frequent words = {rho:.3f}")
L.check("β depth is a monotone function of occurrence count (no valence added by the engine)", rho > 0.8, f"ρ = {rho:.3f}")"""),
("code", """for c in ["天地不仁，以萬物為芻狗 (Tao Te Ching 5): the universe is not benevolent — quotation and reading",
          "Pit = the indifference that surrounded the cruelty, not the cruelty itself (a definition by the author)",
          "σ=½ and indifference: the great circle is a geometric fact in an indifferent space, not a destination prepared for anyone",
          "'Ground floor' of the architecture: meaning is self-generated against a background that does not notice"]:
    L.prose(c, "philosophical framing; no executable counterpart")"""),
]
