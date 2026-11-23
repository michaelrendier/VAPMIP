"""Tests for user_state.py / user_state_console.py: the 15-layer object, the scalar, the code, the warming conversation (2026-11-22)."""
import math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import user_state as U
import user_state_console as C


def reading(**kw):
    r = U.Reading.zero()
    for k, (d, l) in kw.items():
        r[k.replace('HT5', '5HT')] = [d, l]
    return r


def test_fifteen_layers_seven_cursor_seven():
    assert len(U.LAYER_ORDER) == 15
    assert [l[1] for l in U.LAYER_ORDER] == ['dark'] * 7 + ['cursor'] + ['light'] * 7
    assert [l[0] for l in U.LAYER_ORDER[:7]] == list(reversed(U.NT)) and [l[0] for l in U.LAYER_ORDER[8:]] == list(U.NT)
    assert sorted(U.SED_INDEX.values()) == list(range(1, 16))              # e1..e15; the cursor is e8
    assert U.SED_INDEX[('', 'cursor')] == 8


def test_kite_order_is_rainbow_order():
    assert U.NT == ('OPI', 'GLU', 'GABA', 'DA', '5HT', 'NE', 'OXT')


def test_sedenion_has_sixteen_components_and_e0_is_the_scalar():
    r = reading(DA=(0.0, 0.7), NE=(0.4, 0.0))
    v = U.sedenion(r)
    assert len(v) == 16 and v[0] == U.scalar(r) and v[8] == U.net(r)


def test_zero_reading_is_all_zero_and_black():
    r = U.Reading.zero()
    assert U.code(r) == 0 and U.scalar(r) == 0.0 and all(x == 0 for x in U.digits(r).values())


def test_scalar_is_smooth_bounded_and_odd():
    base = reading(DA=(0.0, 0.3))
    assert -1 < U.scalar(base) < 1
    eps = 1e-6
    a, b = reading(DA=(0.0, 0.3)), reading(DA=(0.0, 0.3 + eps))
    assert 0 < U.scalar(b) - U.scalar(a) < 10 * eps                        # differentiable, increasing in a light pole
    flip = reading(DA=(0.3, 0.0))
    assert abs(U.scalar(base) + U.scalar(flip)) < 1e-12                    # dark and light are opposite


def test_code_round_trips_and_is_unique():
    r = reading(DA=(0.0, 0.7), NE=(0.4, 0.0), OXT=(0.2, 0.3))
    n = U.code(r)
    assert U.decode(n) == U.digits(r)
    r2 = reading(DA=(0.0, 0.7), NE=(0.4, 0.0), OXT=(0.2, 0.5))
    assert U.code(r2) != n


def test_dark_and_light_poles_stay_separate():
    r = reading(DA=(0.5, 0.5))
    d = U.digits(r)
    assert d[('DA', 'dark')] > 0 and d[('DA', 'light')] > 0 and U.net(r) == 0.0     # mixed feelings keep both poles


def test_inline_strip_has_fifteen_cells_and_digits():
    r = reading(DA=(0.0, 0.7), NE=(0.4, 0.0))
    s = C.inline(r, with_scalar=False)
    plain = re.sub(r'\x1b\[[0-9;]*m', '', s)
    assert len(plain) == 15 and plain[7] == '|'
    assert plain[7 + 1 + U.NT.index('DA')] == str(U.digits(r)[('DA', 'light')])


def test_upright_is_fifteen_rows_of_ten():
    rows = C.upright(reading(DA=(0.0, 0.7)))
    assert len(rows) == 15
    for row in rows:
        plain = re.sub(r'\x1b\[[0-9;]*m', '', row)
        assert plain[10:12] == '  ' and set(plain[:10]) <= {'┼', ' '}      # 10 columns, then the label


def test_foreground_contrast():
    assert C._fg((255, 255, 0)) == (0, 0, 0) and C._fg((0, 0, 128)) == (255, 255, 255)


def test_warming_cold_assigns_then_adds_and_drift_sign():
    st = U.UserEmotionalState()
    dark = reading(NE=(0.6, 0.0), GABA=(0.5, 0.0)); light = reading(DA=(0.0, 0.6), OXT=(0.0, 0.5))
    st.add(dark)
    assert st.state['NE'][0] == 0.6 and st.n == 1                          # the cold prompt ASSIGNS
    for _ in range(3):
        st.add(light)
    assert st.drift()['net_slope'] > 0 and U.net(st.state) > U.net(dark)   # warmed toward light


def test_two_readings_have_a_drift_not_a_crash():
    st = U.UserEmotionalState(); st.add(U.Reading.zero()); st.add(reading(DA=(0.0, 0.5)))
    assert st.drift()['net_slope'] > 0


def test_label_mix_keeps_poles():
    r = U.mix_labels({'anger': 1.0})
    assert r['NE'][0] > 0.7 and r['NE'][1] == 0.0 and r['DA'][1] == 0.0


def test_irony_swaps_only_with_incongruity_not_on_the_model_alone():
    warm = reading(DA=(0.0, 0.6), HT5=(0.0, 0.5))
    assert U.apply_irony(warm, 0.99, 0.0)['DA'] == warm['DA']              # the model alone never flips it
    flipped = U.apply_irony(warm, 0.99, 0.9)
    assert flipped['DA'][0] > flipped['DA'][1]                             # cold meaning wins with cues
    assert U.incongruity('Oh great, another brilliant answer. Really helpful.', 0.9) > 0.5
    assert U.incongruity('Thanks, that actually helped a lot.', 0.44) < 0.3


def test_bell_curve_engine_is_the_one_in_use():
    assert abs(U.BC.sigma_to_p(3.0) - 0.0026997960632602) < 1e-12
