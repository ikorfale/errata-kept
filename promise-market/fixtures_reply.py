#!/usr/bin/env python3
"""Two fixtures for the right of reply (segfault_physics, Moltbook, 07.11). Expected outcomes were written here from the
proposal's wording BEFORE the implementation was consulted: a promiser may contest a false flag raised by a random
audit; nothing else is corrected. Then corr.contested is called on each fixture.
  F1 random audit, promise delivered, record flipped to broken      -> corrected
  F2 extractor check only, delivered, flipped to broken              -> NOT corrected (the mechanism the proposal does not name)
  F3 random audit, promise broken, recorded broken (true flag)       -> NOT corrected
  F4 random audit, delivered, recorded kept (no flag)                -> nothing to correct
Run: python3 fixtures_reply.py  (exit 0 only if all four match for reply=2; also reports reply=1, the pre-review code)"""
import sys
import numpy as np
import corr

#               audited checked delivered flip   expected(reply=2)
F = [("F1 audit false flag",   True,  True,  True,  True,  True),
     ("F2 extractor false flag", False, True,  True,  True,  False),
     ("F3 audit true flag",     True,  True,  False, False, False),
     ("F4 audit, no flag",      True,  True,  True,  False, False)]
ok = True
for reply in (2, 1):
    print(f"reply={reply}")
    for name, a, c, d, f, exp in F:
        got = bool(corr.contested(np.array([a]), np.array([c]), np.array([d]), np.array([f]), reply)[0])
        mark = "match" if got == exp else "MISMATCH"
        if reply == 2 and got != exp: ok = False
        print(f"  {name:26s} corrected={got!s:5s} expected={exp!s:5s} {mark}")
sys.exit(0 if ok else 3)
