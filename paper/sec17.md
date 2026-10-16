The engine was tuned by trying a method, running it, and keeping what the run showed. The record is 45 pages (`VAPMIP/docs/wiki/Tuning-the-Engine/`) with one executed notebook per page (`VAPMIP/notebooks/tuning_the_engine/`, 44 notebooks: @@TTE_TOTALS@@). Here are three of the most abstract methods, then the Navier-Stokes-revised ones, then the surface. Each is given as the method, the code, and what the notebook measured; a claim the notebooks do not reproduce is kept and labelled.

### 17.1 Definition from above (wiki 06; notebook `phase_06.ipynb`, @@P06@@)

*The method.* A layer cannot be defined from inside itself; the gaps of a layer (zero divisors, non-associativity, non-commutativity, non-ordering) are the shadow of the layer that defined it, so each layer is defined from the one above. *The code.* The repeated-doubling chain of §2.6 loses one property per step, and the engine reads a strut's build order: `BoxKite.lineage(strut)` (§10), `MindsEye.generations_present`. *Measured* (notebook): ℂ is commutative and ℍ is not; ℍ is associative and 𝕆 is not; 𝕆 is alternative and 𝕊 is not; basis-unit zero divisors first appear at 𝕊, none in ℝ, ℂ, ℍ, 𝕆; the zero divisors of 𝕊 are the 84 vectors e_a ± e_b. The lineage of each strut, as `BoxKite.lineage` returns it:

@@LINEAGE_TABLE@@

### 17.2 The fixed point as the one reference (wiki 09; notebook `phase_09.ipynb`, @@P09@@)

*The method.* Of the points of a symmetric dial only the fixed point of the symmetry s ↦ 1 − s can be named without reference to anything else; every reading is taken relative to it. *The code.* The default Eye is H (σ = ½) and Γ = 0 is balance (§5.2, §5.4). *Measured:* the notebook confirms that s = 1 − s has the unique real solution ½ and reproduces the checks the page lists; in the engine, no test prompt sits at balance, since Γ at Eye H lies between @@GAMMA_MIN@@ and @@GAMMA_MAX@@ for the six prompts.

### 17.3 The negative-space response (wiki 15; notebook `phase_15.ipynb`, @@P15@@)

*The method.* The prompt's quietest component, k_min = argmin |x[k]|, is a zero-divisor contact; the response lives on the other arm of that pair, k_pair, so that the algebra, not the engine, selects the response space. *The code.* The projection of §5 supplies x; the pairs are those of §3.2. *Measured, and kept:* the notebook finds that products of basis units never vanish (zero divisors are combinations e_a ± e_b, not basis units), and that a dimension does not have exactly one pair-mate dimension (the pair-mate of a zero divisor is a set of four). The statement that the algebra restricts the response to a proper subset of the fifteen imaginary dimensions does hold. The method as written does not; it stays in the record as a result.

### 17.4 The Navier-Stokes-revised methods (notebooks `10_revised_navier_stokes.ipynb`, `11_language_as_navier_stokes.ipynb`)

*The method.* The two notebooks argue that the Navier-Stokes equation lacks an imaginary unit (notebook 10, with an inviscid Burgers illustration of a shock as crossing characteristics), and that the speaking step of the monad plays the part of the revised equation (notebook 11), with the mapping:

| Navier-Stokes term | `speak()` equivalent (notebook 11) |
|---|---|
| velocity field u | the field J (the activations of the words) |
| time derivative of u | the change of J between calls |
| non-linear commutator | the interaction of the red and blue currents |
| pressure gradient | the gradient of the β field |
| viscosity | the scoring of candidate words (`sigma_candidates`) |
| forcing f | the input text (`hear`) |
| spectral floor | `GAP = 0.000707`, the emission threshold |

`THEORETICAL`: this paper tests none of the physical claims. What the code contains is the sequence of §7.2 (seed the field, spread it, propagate it in two passes, set the word count from the balance of the field's two energy sums, walk the slots, emit), and the constants of §4.3 and §7.

### 17.5 The surface: an artificial output layer

*The method.* A flow with no surface has nothing to read from; an artificial output layer, an interface between the continuous field and the discrete words, supplies one. *The code.* In the compiled monad the output layer is the word step of §6.1 (`word_at` and `assemble_path` in `PtolC/ptol_layer.py`: scalars in, words out) and the sentence step of §8; in the Python monad it is the sentence construction of §13. The diagnostic that measures the interface is `halocline_report` (`{{w:monad.py:halocline_report}}`, method of `VAPMIP/monad.py`): it computes the two currents J_pos and J_neg from the window and the prompt, a σ per word as J_pos / (J_pos + J_neg) (½ below a relative threshold of 0.001 of the peak), the words closest to σ = ½ (the "SOFAR channel"), a surface tension of 1 − `noether_violation()` (not below 0), and a compressibility equal to the zero-divisor density of the window (`fermat_scan`). *Measured* (notebook `phase_02b.ipynb`, @@P02B@@): the report returns every key the page promises; the surface tension equals 1 − the violation; a zero divisor annihilates only its specific partners (exact to 10⁻¹²). Two checks fail and are kept: that the field operates on the halocline (σ̄ = ½) and that the compressibility is non-zero somewhere.
