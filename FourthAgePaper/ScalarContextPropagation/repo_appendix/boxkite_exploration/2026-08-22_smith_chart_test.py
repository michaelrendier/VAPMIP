#!/usr/bin/env python3
"""The Smith chart is the same Mobius structure as L_(I|O), independently
discovered in RF engineering (Phillip Smith, Bell Labs, 1939). Tested here;
engine relation: SedenionFactoralRelativity/engine/lineage.py,
pathway.smith_chart_is_the_same_mobius (PW8)."""
Z0 = 50.0
def gamma(Z): return (Z - Z0) / (Z + Z0)

print("1. anchors: Z=0 (short) ->", gamma(0+0j), " Z->inf (open) ->", gamma(1e12+0j),
      " Z=Z0 (matched) ->", gamma(Z0+0j), "(the fixed point)")

print("2. |Gamma|=1 <=> Re(Z)=0 (the lossless/reactive horizon):")
for Z in (10j, 50j, -30j, 5+0j, 5+50j):
    print(f"   Z={Z}: |Gamma|={abs(gamma(Z)):.4f}  Re(Z)={Z.real}")

print("3. conformal: constant-R, constant-X curves orthogonal at their crossing")
h = 1e-5
zR = lambda x: gamma(Z0 + 1j*x); zX = lambda r: gamma(r + 1j*Z0)
tR = (zR(Z0+h)-zR(Z0-h))/(2*h); tX = (zX(Z0+h)-zX(Z0-h))/(2*h)
print("   dot(tangent_R, tangent_X) =", tR.real*tX.real + tR.imag*tX.imag)

print("4. admittance Y=1/Z (inside-out) is a pi-rotation: Gamma_Y == -Gamma_Z")
def gamma_Y(Z):
    Y, Y0 = 1/Z, 1/Z0
    return (Y-Y0)/(Y+Y0)
for Z in (25+25j, 100-10j, 10+80j):
    print(f"   Z={Z}: Gamma_Z={gamma(Z):.4f}  Gamma_Y={gamma_Y(Z):.4f}  "
          f"match={abs(gamma_Y(Z)-(-gamma(Z)))<1e-9}")
