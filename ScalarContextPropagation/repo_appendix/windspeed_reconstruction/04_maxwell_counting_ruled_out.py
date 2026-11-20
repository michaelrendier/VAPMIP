# Maxwell counting, done exactly, for "the rigidity matrix of K_{2,2,2}
# with the three struts as bars, strut fixed, has dim(flex) = 1"
# (pencil_hyperstring.md's own acceptance test 1).

V = 6                    # the six Assessor vertices
d = 3                    # ordinary 3D embedding, the literal reading
rigid_motions = d + d*(d-1)//2   # translations + rotations = 3 + 3 = 6
B_struts_only = 3        # ONLY the 3 struts (non-edges) as length-fixing bars
B_all_15_pairs = 15      # every pair constrained (the complete graph K6)

def flex_dim(V, d, B):
    return d*V - rigid_motions - B

print(f"d={d}, V={V}, rigid_motions={rigid_motions}")
print(f"struts-only as bars (B={B_struts_only}):  dim(flex) = {flex_dim(V,d,B_struts_only)}")
print(f"all 15 pairs as bars (B={B_all_15_pairs}): dim(flex) = {flex_dim(V,d,B_all_15_pairs)}")
print()
print("For dim(flex)=1 in d=3, need B =", d*V - rigid_motions - 1, "bars -- i.e. 11 constraints, not 3.")
print()
# What if the configuration space isn't 3D Euclidean at all, but the
# pencil_hyperstring.md's OWN claimed '8 DOF' octonion space (e10 R2)?
d8 = 8
# no meaningful 'rotation group' analogue is asserted for that space in
# the source material -- so rigid_motions there is genuinely undefined,
# not just uncomputed. Flag rather than invent a number.
print("In the claimed 8-DOF octonion configuration space: rigid_motions is")
print("UNDEFINED in any source material found -- not a number I can supply")
print("without inventing one. This is the actual blocker, not d=3 arithmetic.")
