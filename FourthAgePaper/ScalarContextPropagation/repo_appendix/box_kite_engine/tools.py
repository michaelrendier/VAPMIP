"""
ainulindale_engine.modules.box_kite.tools
============================================
The Box-Kite Debugger -- Module Tools

Implements the EquationModule registry contract.
Provides: formulary, run(), viewer_data(), shell_commands()

The zero-divisor geometry, made visible and exactly enumerable. The
object is PSL(2,7) (order 168, Aut(Fano)), NOT G2 -- Moreno's G2 is the
continuous blow-up that forgets the labelling. See maths.py.

Version: 0.2
"""

from typing import Dict, List, Any

from ...engine.registry import EquationModule, Equation, CONFIDENCE
from .maths import (
    cd_multiplication_table, basis_mul, multiply, is_zero, basis_vector,
    associator, commutator, associator_defect, associator_census,
    diagonals, is_assessor, assessors, strut, box_kites,
    zero_divisor_pairs, verify_counts,
    assessors_adjacent, box_kite_graph, chart_spectrum,
    glued_graph, glued_spectrum, associator_field,
    eigenvalues_symmetric,
    pg32_points, pg32_lines, fano_planes, psl27_order, skeleton_counts,
    e0_is_outside, SEDENION_DIM,
    index_chart_membership, skeleton_overlap, fixed_point_gluing,
    norm, fixed_point_weight, energy_split, diagonal_amplitudes,
    assessor_coordinates, chart_projection, nearest_assessor,
    local_curvature, chart_of, address_census,
)


class BoxKiteModule(EquationModule):
    """The Box-Kite Debugger -- the zero-divisor geometry, made watchable."""

    @property
    def name(self):
        return "box_kite"

    @property
    def display_name(self):
        return "The Box-Kite Debugger (ZD Geometry)"

    @property
    def version(self):
        return "0.2"

    @property
    def description(self):
        return (
            "Makes the sedenion zero-divisor geometry visible and exactly "
            "enumerable. The object is PSL(2,7) -- order 168, Aut(Fano "
            "plane) -- NOT G2: Moreno's G2 homeomorphism is a blow-up that "
            "forgets which Fano line is which. Everything here derives from "
            "the Cayley-Dickson multiplication table: 42 Assessors (planes "
            "span(e_a, e_b+8) whose diagonals zero-divide; a==b never "
            "works, so 49-7=42), 84 diagonals, 168 primitive unit points, "
            "336 ordered annihilating pairs, and 7 box-kites of 6 Assessors "
            "each. Each box-kite is an OCTAHEDRON (K_2,2,2), verified from "
            "vanishing products, with Laplacian spectrum {0,4,4,4,6,6} -- "
            "the chart-level dispersion relation. The zero mode is e_0's "
            "signature: exists everywhere, propagates nowhere. The "
            "associator [a,b,c]=(ab)c-a(bc) is the curvature and the debug "
            "view. Agreement with ZD_PAIRS=84 / ZD_CLASSES=42 / 168 is a "
            "CHECK, not an input. v0.2 adds THE CHART OF ADDRESSES: given a "
            "monad sedenion address (VAPMIP/monad_sedenion_addresses.pkl), "
            "chart_of() reports which of the 7 charts it occupies, its "
            "nearest Assessor and diagonals, its local associator curvature, "
            "and its FIXED-POINT WEIGHT. And it resolves the disconnection: "
            "the charts touch in the SKELETON (every usable index sits in 6 "
            "of 7 charts; only e_0 and e_8 are orphans) even though they have "
            "zero cross-strut adjacency edges. The 7 zero modes are 7 copies "
            "of one constant, and they identify at e_0 -- the fixed point is "
            "where the boundary generator and the geometry coincide."
        )

    @property
    def confidence_floor(self):
        return "ESTABLISHED"

    # -- Formulary ---------------------------------------------------------

    def formulary(self) -> List[Equation]:
        return [
            Equation(
                name='verify_counts',
                display='THE HONEST CHECK: 42 / 84 / 168 / 336 / 7, all derived',
                latex=r'42 \text{ Assessors},\ 84 = 42{\times}2,\ 168 = 42{\times}4 = |PSL(2,7)|',
                radian_form='every count computed from the CD table; mismatch = bug here, not discovery',
                confidence='ESTABLISHED',
                code_verified=True,
                params=[],
                compute=lambda: verify_counts(),
                display_options=['text'],
            ),
            Equation(
                name='box_kites',
                display='The 7 box-kites, keyed by strut s = a XOR b',
                latex=r'7 \text{ struts} \times 6 \text{ Assessors} = 42',
                radian_form='box_kites()[s] = the 6 Assessors with a XOR b = s',
                confidence='ESTABLISHED',
                code_verified=True,
                params=[],
                compute=lambda: box_kites(),
                display_options=['text'],
            ),
            Equation(
                name='box_kite_graph',
                display='THE SHAPE: each chart is an octahedron K_2,2,2',
                latex=r'K_{2,2,2}:\ 6 \text{ vertices},\ 12 \text{ edges},\ 4\text{-regular}',
                radian_form='edges from vanishing products; 3 non-edges = the reversal pairs',
                confidence='ESTABLISHED',
                code_verified=True,
                params=['s'],
                compute=lambda s: box_kite_graph(s),
                display_options=['text'],
            ),
            Equation(
                name='chart_spectrum',
                display='THE DISPERSION RELATION, chart level: {0,4,4,4,6,6}',
                latex=r'\mathrm{spec}(L_{K_{2,2,2}}) = \{0,4,4,4,6,6\} = \omega^2(k)',
                radian_form='octahedral graph Laplacian; the 0 mode is e_0 -- everywhere, propagates nowhere',
                confidence='ESTABLISHED',
                code_verified=True,
                params=['s'],
                compute=lambda s: chart_spectrum(s),
                display_options=['text'],
            ),
            Equation(
                name='associator',
                display='THE CURVATURE: [a,b,c] = (ab)c - a(bc)',
                latex=r'[a,b,c] = (ab)c - a(bc)',
                radian_form='associator(i,j,k) -> 16-vector; 1848 of 4096 basis triples are nonzero',
                confidence='ESTABLISHED',
                code_verified=True,
                params=['i', 'j', 'k'],
                compute=lambda i, j, k: associator(i, j, k),
                display_options=['text'],
            ),
            Equation(
                name='associator_field',
                display='THE DEBUG VIEW: curvature painted on a box-kite',
                latex=r'\|[a,\, b{+}8,\, \cdot\,]\| \text{ per vertex and edge}',
                radian_form='where the field is large, the geometry is bending',
                confidence='ESTABLISHED',
                code_verified=True,
                params=['s'],
                compute=lambda s: associator_field(s),
                display_options=['text'],
            ),
            Equation(
                name='commutator',
                display='THE TORSION: [a,b] = ab - ba',
                latex=r'[a,b] = ab - ba',
                radian_form='commutator(i,j) -> 16-vector',
                confidence='ESTABLISHED',
                code_verified=True,
                params=['i', 'j'],
                compute=lambda i, j: commutator(i, j),
                display_options=['text'],
            ),
            Equation(
                name='glued_graph',
                display='The 42-vertex atlas — and its cross-strut edge count',
                latex=r'42 \text{ vertices},\ 84 \text{ edges} = 7 \times 12',
                radian_form='FIRST MODEL, not a derivation: transition maps are not yet written',
                confidence='THEORETICAL',
                code_verified=True,
                params=[],
                compute=lambda: glued_graph(),
                display_options=['text'],
            ),
            Equation(
                name='glued_spectrum',
                display='Laplacian spectrum of the whole atlas',
                latex=r'\mathrm{spec}(L_{42})',
                radian_form='7 disconnected octahedra => 7 zero modes; see glued_graph caveat',
                confidence='THEORETICAL',
                code_verified=True,
                params=[],
                compute=lambda: glued_spectrum(),
                display_options=['text'],
            ),
            Equation(
                name='chart_of',
                display='THE CHART OF ADDRESSES: where a monad address sits in the atlas',
                latex=r'v \in \mathbb{S} \mapsto (\text{strut},\ \text{Assessor},\ \kappa_{\text{local}})',
                radian_form='exhaustive: chart energies, nearest Assessor, diagonals, curvature, fixed-point weight',
                confidence='ESTABLISHED',
                code_verified=True,
                params=['v', 'check_zd'],
                compute=lambda v, check_zd=True: chart_of(v, check_zd),
                display_options=['text'],
            ),
            Equation(
                name='address_census',
                display='Exhaustive census over a corpus of monad addresses',
                latex=r'\{\text{name} \to v\} \mapsto \text{distribution over 7 charts, 42 Assessors}',
                radian_form='descriptive only — counts and distributions, no scoring against an expectation',
                confidence='ESTABLISHED',
                code_verified=True,
                params=['addresses', 'limit', 'check_zd'],
                compute=lambda addresses, limit=None, check_zd=False: address_census(addresses, limit, check_zd),
                display_options=['text'],
            ),
            Equation(
                name='skeleton_overlap',
                display='THE CHARTS DO TOUCH — in the skeleton, not the adjacency',
                latex=r'\text{every usable index lies in } 6 \text{ of } 7 \text{ charts}',
                radian_form='pairwise shared skeleton points = 10 for every chart pair; only e_0 and e_8 are orphans',
                confidence='ESTABLISHED',
                code_verified=True,
                params=[],
                compute=lambda: skeleton_overlap(),
                display_options=['text'],
            ),
            Equation(
                name='fixed_point_gluing',
                display='WHERE THE ATLAS GLUES: at e_0',
                latex=r'7 \text{ zero modes} = 7 \text{ copies of one constant} \to 1',
                radian_form='e_0 and e_8 are the only basis elements in no Assessor; identify the zero modes and the atlas connects',
                confidence='THEORETICAL',
                code_verified=True,
                params=[],
                compute=lambda: fixed_point_gluing(),
                display_options=['text'],
            ),
            Equation(
                name='fixed_point_weight',
                display='How much of an address is pure 0_RB',
                latex=r'w_0(v) = v_0^2 / \|v\|^2',
                radian_form='1.0 = pure identity, no geometry; measured mean over the monad book = 0.64',
                confidence='ESTABLISHED',
                code_verified=True,
                params=['v'],
                compute=lambda v: fixed_point_weight(v),
                display_options=['text'],
            ),
            Equation(
                name='skeleton_counts',
                display='PG(3,2): 15 points, 35 lines, 15 Fano planes (NOT 32)',
                latex=r'PG(3,2):\ 15\ \text{pts},\ 35\ \text{lines},\ 15\ \text{planes}',
                radian_form='the 15 pure imaginaries as projective points; each plane carries a PSL(2,7)',
                confidence='ESTABLISHED',
                code_verified=True,
                params=[],
                compute=lambda: skeleton_counts(),
                display_options=['text'],
            ),
            Equation(
                name='e0_is_outside',
                display='0_RB IS NOT THE GEOMETRY — checked, not asserted',
                latex=r'e_0 \notin PG(3,2),\ e_0 \notin \text{any Assessor},\ [e_0,\cdot,\cdot] = 0',
                radian_form='it generates the boundary and does not live on it',
                confidence='ESTABLISHED',
                code_verified=True,
                params=[],
                compute=lambda: e0_is_outside(),
                display_options=['text'],
            ),
            Equation(
                name='associator_census',
                display='How much of the algebra is curved',
                latex=r'\#\{(i,j,k) : [e_i,e_j,e_k] \neq 0\}',
                radian_form='1848 nonzero of 4096 basis triples',
                confidence='ESTABLISHED',
                code_verified=True,
                params=[],
                compute=lambda: associator_census(),
                display_options=['text'],
            ),
            Equation(
                name='zero_divisor_pairs',
                display='All 336 ordered annihilating diagonal pairs',
                latex=r'336 = 84 \times 4',
                radian_form='each of the 84 diagonals annihilates exactly 4 others',
                confidence='ESTABLISHED',
                code_verified=True,
                params=[],
                compute=lambda: zero_divisor_pairs(),
                display_options=['text'],
            ),
        ]

    # -- Run ---------------------------------------------------------------

    def run(self, equation_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        eq = next((e for e in self.formulary() if e.name == equation_name), None)
        if eq is None:
            raise KeyError(f"Equation '{equation_name}' not found in {self.name} module")
        result = eq.compute(**params) if params else eq.compute()
        return {'equation': eq, 'params': params, 'result': result, 'module': self.name}

    # -- Viewer data -------------------------------------------------------

    def viewer_data(self, equation_name: str, params: Dict[str, Any],
                    display_mode: str) -> Dict[str, Any]:
        return {'text': self._format_text(equation_name, self.run(equation_name, params))}

    def _format_text(self, equation_name: str, result: Dict) -> str:
        eq = result['equation']
        r = result['result']
        if isinstance(r, dict):
            body = '\n'.join(f"      {k:<28} {v}" for k, v in r.items()
                             if not isinstance(v, (list, dict)))
            summary = '\n' + body
        elif isinstance(r, list):
            summary = f"{r[:10]}{' ...' if len(r) > 10 else ''}  (n={len(r)})"
        else:
            summary = r
        return (
            f"  {eq.display}\n"
            f"  Status: {eq.confidence}  |  Code-verified: {eq.code_verified}\n"
            f"  Radian form: {eq.radian_form}\n"
            f"  Result: {summary}"
        )

    # -- Shell commands ----------------------------------------------------

    def shell_commands(self) -> Dict[str, Any]:
        return {
            'verify':     lambda: verify_counts(),
            'kites':      lambda: box_kites(),
            'kite':       lambda s: box_kite_graph(s),
            'spec':       lambda s: chart_spectrum(s),
            'assoc':      lambda i, j, k: associator(i, j, k),
            'defect':     lambda i, j, k: associator_defect(i, j, k),
            'field':      lambda s: associator_field(s),
            'comm':       lambda i, j: commutator(i, j),
            'atlas':      lambda: glued_graph(),
            'atlas_spec': lambda: glued_spectrum(),
            'skeleton':   lambda: skeleton_counts(),
            'lines':      lambda: pg32_lines(),
            'fano':       lambda: fano_planes(),
            'e0':         lambda: e0_is_outside(),
            'census':     lambda: associator_census(),
            'zds':        lambda: zero_divisor_pairs(),
            'mul':        lambda i, j: basis_mul(i, j),
            'chart':      lambda v: chart_of(v),
            'census':     lambda addrs, n=None: address_census(addrs, n),
            'overlap':    lambda: skeleton_overlap(),
            'glue':       lambda: fixed_point_gluing(),
            'fpw':        lambda v: fixed_point_weight(v),
            'split':      lambda v: energy_split(v),
            'assess':     lambda v: assessor_coordinates(v),
            'proj':       lambda v: chart_projection(v),
            'curv':       lambda v: local_curvature(v),
            'membership': lambda: index_chart_membership(),
        }

    def on_register(self, registry) -> None:
        pass
