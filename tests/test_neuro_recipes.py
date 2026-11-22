import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import neuro_recipes as n


def test_every_recipe_has_seven_axes_in_range():
    for name, r in n.R.items():
        assert set(r['vec']) == set(n.AXES), name
        assert all(0.0 <= v <= 1.0 for v in r['vec'].values()), name


def test_every_recipe_cites_known_sources_and_has_a_test():
    for name, r in n.R.items():
        assert r['ev'], name
        assert all(k in n.SRC for k, _ in r['ev']), name
        assert r['test'] and r['use'] and r['lang'], name


def test_silks_cover_the_seven_axes_once():
    assert sorted(n.SILKS.values()) == sorted(['ANCHOR', 'SPAN', 'SCAFFOLD', 'ELABORATE', 'HOOK', 'WRAP', 'SHELL'])
    assert set(n.SILKS) == set(n.AXES) == set(n.COLOURS)


def test_cancelled_states_end_closer_to_receptive():
    for name, r in n.R.items():
        if r['group'] == n.G3:
            continue
        d0 = n.dist(r['vec'], n.RECEPTIVE)
        d1 = n.dist(n.conjugate(r['vec']), n.RECEPTIVE)
        assert d1 <= d0 + 1e-9, name
        if d0 >= n.BAND:
            assert d1 < d0, name


def test_hyperarousal_is_cancelled_to_a_lower_arousal_index():
    for name in ('RAGE', 'FEAR', 'PANICKED', 'OVERWHELMED', 'VICIOUS'):
        v = n.R[name]['vec']
        assert n.arousal(n.conjugate(v)) < n.arousal(v) - 1.0, name


def test_receptive_neighbours_are_held():
    for name in ('SEEKING', 'PLAY', 'VIBRANT'):
        v = n.R[name]['vec']
        assert n.conjugate(v) == {a: round(v[a], 2) for a in n.AXES}, name


def test_meet_then_lead_starts_at_user_and_arrives_at_target():
    u, t = n.R['RAGE']['vec'], n.RECEPTIVE
    tr = n.meet_then_lead(u, t, 5)
    assert tr[0] == {a: round(u[a], 3) for a in n.AXES} and tr[-1] == {a: round(t[a], 3) for a in n.AXES}
    ds = [n.dist(x, t) for x in tr]
    assert all(ds[i] >= ds[i + 1] for i in range(len(ds) - 1))


def test_nearest_dispensation_for_panic_is_a_brake_recipe():
    assert n.nearest(n.conjugate(n.R['PANICKED']['vec']))[0] in ('ENCOURAGE', 'GUIDE', 'SETTLE', 'DEFLATE')


def test_book_is_written_from_the_data():
    b = n.book()
    assert '# Neurochemical Recipe Book' in b and all(name in b for name in n.R)


def test_every_plan_names_known_states_and_dispensations_and_ends_at_receptive():
    for state, steps in n.PLANS.items():
        assert state in n.R and n.R[state]['group'] != n.G3, state
        assert all(d in n.R and n.R[d]['group'] == n.G3 for d in steps), state
        pl = n.plan(state)
        assert pl[0] == n.R[state]['vec'] and pl[-1] == n.RECEPTIVE


def test_plans_never_step_far_away_from_receptive():
    r, _ = n.max_rise()
    assert r < 0.35


def test_defensive_states_start_with_disarm_not_rebuttal():
    for st in ('DEFENSIVE', 'DOUBLING_DOWN', 'ASHAMED', 'GUILTY', 'VINDICTIVE', 'CYNICAL', 'PONTIFICATING', 'PARANOIA'):
        assert 'DISARM' in n.PLANS[st][:2], st


def test_every_common_behaviour_has_a_plan():
    for name, r in n.R.items():
        if r['group'] == n.G4:
            assert name in n.PLANS, name


def test_image_rows_agree_with_the_book():
    assert n.R['DESPAIR']['vec']['DA'] < .2 and n.R['DESPAIR']['vec']['5HT'] < .3          # depression tubes: DA and 5HT low
    assert n.R['ANXIOUS']['vec']['DA'] < .2                                              # anxiety tube: DA low
    assert n.R['PSYCHOSIS']['vec']['DA'] > .9                                            # schizophrenia tube: DA full
    assert n.R['FIGHT_OR_FLIGHT']['vec']['NE'] > .9                                      # fight or flight: NE full
    love = n.R['ATTACHMENT']['vec']
    assert love['DA'] > .7 and love['5HT'] > .6 and love['OXT'] > .9                     # love: DA, 5HT, OXT high
