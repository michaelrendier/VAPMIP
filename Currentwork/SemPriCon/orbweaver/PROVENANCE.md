# orbweaver/ — code copied in for the sentence-constructor basin

`LorenzStirling.py` is a **byte-for-byte copy** (never edited here) of `PtolemyDesktop/Archimedes/Maths/LorenzStirling.py`
(last commit touching it in PtolemyDesktop: `8bd006f`, 2026-07-17; sha256 `8134790f1027f8b63b874390002797df2d219988c87a9503bcb63981031dbef8`, 319 lines, stdlib + numpy).

Copied 2026-10-20 on Cody's instruction: the sentence constructor's **basin** gets the Lorenz–Stirling attractor code. It is to be part of the **pathway mechanism for the orbweaver**.

What it is (its own docstring): Stirling V=10 inversion-step iteration defines the **basin boundaries** (which basin); a Lorenz system defines the **trajectory inside a basin**; `LorenzStirling.classify(z)` returns `basin_id`, `lorenz_pos`, `extinct`, `uncertainty`. Bailout `|z| < bail` is inside, escape is **extinction**.

Not wired to anything yet. Smoke test 2026-10-20: imports from this path, `classify(0.3 − 0.7i)` runs, `lorenz_trajectory(steps=2000)` runs.
Its docstring's `from Archimedes.Maths.LorenzStirling import …` is the original package path; here, import it by file path.
