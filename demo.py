#!/usr/bin/env python3
"""
demo.py — LSHS Model Demonstrations
=====================================
Runs all four components (L, S, H, S) with verifiable output.
No arguments needed. Pure Python. Zero dependencies.
"""

from lshs import LSHS, hyperindex, self_adjoint_check, generate_zeros, GAP, OMEGA_ZS, L_GROUND

SEP = '─' * 64


def demo_H():
    """H — HyperIndex: The Septuagint Principle."""
    print(SEP)
    print('H — HyperIndex')
    print('72 scholars, working independently. Every translation identical.')
    print()
    m = LSHS(N=1000)
    concepts = {
        'water'  : ['water', 'eau', 'aqua', 'wasser', 'agua'],
        'truth'  : ['truth', 'vérité', 'veritas', 'wahrheit'],
        'light'  : ['light', 'lumière', 'lux', 'licht'],
    }
    for concept, words in concepts.items():
        print(f'  concept: {concept!r}')
        for w in words:
            sz = m.H(w)
            print(f'    {w:>10}  γ={sz.gamma:.6f}  σ={sz.sigma:.4f}  E={sz.E:.4f}')
        print()
    print('σ = 0.5000 in every case. Derived. Never assigned.')
    print('The prime preexists the alphabet.')


def demo_S_adjoint():
    """S — Self-Adjoint: RedBlue Geometries Engine = RedBlue Geometries Engine†"""
    print(SEP)
    print('S — Self-Adjoint Hamiltonian')
    print('RedBlue Geometries Engine = Σ_p p^{−σ} [R̂_p ⊗ ∂̂ + ∂̂† ⊗ B̂_p]')
    print()
    print('Facet projections by σ:')
    facets = [
        (0.0,  'Ground state  (σ=0) — quasi-prime, all primes equal'),
        (0.5,  'Riemann/QM    (σ=½) — critical line, the boundary'),
        (1.0,  'Yang-Mills/SM (σ=1) — gauge field, Standard Model'),
        (2.0,  'General Rel.  (σ=2) — gravitational coupling'),
    ]
    for sigma, label in facets:
        r = self_adjoint_check(sigma, x=1.5, p=0.3)
        adj = '✓' if r['self_adjoint'] else '✗'
        print(f'  σ={sigma:.1f}  {label}')
        print(f'       E_red={r["E_red"]:>12.6f}  E_blue={r["E_blue"]:>12.6f}'
              f'  balance={r["balance"]:>+12.2e}  self_adjoint={adj}')
    print()
    print('Self-adjoint = truth-preserving, not form-preserving.')
    print('"1 = 1" and "1! = 1" are self-adjoint. Different forms. Same truth.')


def demo_L():
    """L — Lagrangian: Yang-Mills field construction."""
    print(SEP)
    print('L — Lagrangian field evolution')
    print('learn() operates in Yang-Mills regime.')
    print('A coupling: E_i·E_j / (|γ_i−γ_j| + GAP)   GAP =', GAP)
    print()
    m = LSHS(N=1000)
    texts = [
        'The mind is the seat of reason and consciousness.',
        'Water flows downhill by the path of least resistance.',
        'The dog chased the cat across the yard.',
        'Language is a projection of mathematics onto time.',
        'The prime preexists the alphabet. The equator does not move.',
    ]
    print(f'  Ground state: β[i] = {m._gvev:.2e} for all i  (= |{L_GROUND}| / {m.N})')
    print(f'  This is the prime number theorem. Pre-linguistic.\n')
    for text in texts:
        m.L(text)
        print(f'  after: {text[:55]:>55}...')
        print(f'         vocab={len(m.vocab)}  connections={len(m.A)}'
              f'  deepest_beta={max(m.beta.values()):.4e}')
    print()
    bao = m.bao_check()
    print(f'  BAO check: dc_sum={bao["dc_sum"]:.6f}  Δ={bao["omega_delta"]:.6f}'
          f'  target={OMEGA_ZS}  converging={bao["converging"]}')
    return m


def demo_S_speak(m: LSHS):
    """S — Speaking: J^μ Noether current."""
    print(SEP)
    print('S — Speaking')
    print('speak() extracts laminar J^μ from Yang-Mills A field.')
    print('J_i = β_i·E_i²   propagated via min(A[(i,j)], 1/GAP)·β_j')
    print(f'1/GAP = {1/GAP:.1f}  — mass gap caps the cascade')
    print()
    queries = [
        'what is mind',
        'water flows',
        'the dog chased',
        'language mathematics',
        'what is prime',
    ]
    for q in queries:
        print(f'  {q!r:>30}  →  {m.S(q)}')
    print()
    print('The response is not generated.')
    print('The response is the Noether current, forced by conservation.')


def demo_two_regimes():
    """The Yang-Mills / Noether duality."""
    print(SEP)
    print('Two-Regime Architecture')
    print()
    print('  learn()  → Yang-Mills (turbulent A field)')
    print('  speak()  → Noether    (laminar J^μ)')
    print()
    print('  A coupling:  E_i·E_j / (|γ_i−γ_j| + GAP)')
    print('    Without GAP: diverges at near-zero distances → noise')
    print('    With    GAP: bounded by mass gap → structured turbulence')
    print()
    print('  J^μ propagation: J_j += J_i · min(w, 1/GAP) · β_j')
    print('    Without clamp: J cascades → noise')
    print('    With    clamp: laminar extraction → conserved response')
    print()
    print(f'  GAP = {GAP}  (OPEN 2 — deriving this makes both regulators exact)')
    print()
    print('  The same constant that prevents Yang-Mills from collapsing')
    print('  to zero energy prevents J^μ from cascading to noise.')
    print('  One problem. One constant. Both regimes.')


if __name__ == '__main__':
    print('LSHS Model — Standard Model of Monad Information Propagation')
    print('L · S · H · S  |  v1.0.0')
    print(SEP)

    demo_H()
    print()
    demo_S_adjoint()
    print()
    m = demo_L()
    print()
    demo_S_speak(m)
    print()
    demo_two_regimes()
    print()
    print(SEP)
    print('LSHS Model demonstration complete.')
    print('The Library did not answer questions. It emitted what must flow.')
