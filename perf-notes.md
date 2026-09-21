# Where the frame goes

Measured with the in-game profiler (`F2`, `__game.profile`), which reads GPU
time from `EXT_disjoint_timer_query_webgl2`. Every figure below is an A/B run
**interleaved** — A B A B, two or three alternations, comparing the medians.

## Why interleaved, and why you should not trust anything else here

The GPU clocks up over a run. A sequence of probes taken one after another
produces times that fall steadily down the list whatever you are testing.
Twice in one session that turned a 1 ms change into an apparent 11 ms one and
had me about to ship "half the scene pass" as a finding. The absolute numbers
below still drift between alternations — the same setting measured 7.72, 8.76
and 10.00 ms across one sweep — so only the *differences* mean anything, and
only where they survive every alternation.

A second trap: one viewpoint is not the board. Widening the chunk-size test
from one viewpoint to seven reversed its conclusion completely.

## The baseline

One representative corridor viewpoint, 2.07 MPix (the capped budget), dry
weather, level as of the waterway commit:

```
frame            26.06 ms        38.4 fps
  scene            17.84         407 calls   1.40M triangles
  scene + shadow   25.94         588 calls   2.18M triangles
  ao                1.72
  composite         1.34
  bloom             1.10
```

The shadow map runs on alternate frames, so an average frame is the scene
pass plus half the shadow cost plus the post chain.

## What each piece costs

| | ms/frame | share | how |
|---|---|---|---|
| hedge blobs, all alpha-cut | 9.81 | 38% | 94 meshes hidden |
| — tree canopies alone | 6.20 | 15% | |
| — 320-face hedge foliage | 3.35 | 13% | 2,256 instances |
| shadow map | 4.05 | 16% | (scene+shdw − scene) ÷ 2 |
| SSAO | 2.71 | 9% | `POST.ao` |
| bloom | 2.21 | 8% | `POST.bloom` |
| grass | 2.12 | 9% | 26 meshes hidden |
| leaf cards | ~0 | — | inside the noise |
| **buried hedge core** | **−6.82** | — | hiding it costs 6.8 ms |

That last row is the interesting one. The core blob buried inside each hedge
tile is not overhead: it is opaque mass that occludes what is behind it, and
taking it away makes the frame *slower* because everything it was hiding then
gets shaded. The same effect showed up earlier when drawing the cutout
foliage opaque came out cheaper than not drawing it at all. **Occluders earn
their keep here; the instinct to delete geometry is often backwards.**

## What is not the problem

- **The alpha test.** Toggling `alphaTest` on and off on the cutout foliage,
  interleaved, showed no difference outside the noise. It is not `discard`
  breaking early-Z; it is raw shaded fill.
- **Draw calls.** 600-odd per frame looks alarming and batching makes things
  worse: widening the IB's spatial buckets from 28 m to 96 m cut a third of
  the calls and submitted 62% more geometry for it, because the frustum could
  no longer cull. Measured over seven viewpoints, 28 m won. See the table in
  `IB.build`.
- **Small meshes.** The ~810 mob and item parts are about 140 draw calls and
  cost ~4.6 ms *in total* — deleting every one of them is the ceiling, so
  merging them is worth a couple of ms at best.

## The one lever that actually moved

The renderer is **fill-bound**. Quartering the pixels roughly halves the
scene pass and cuts the post chain by five. That is why capping the pixel
budget to 1080p's worth was worth a third of the frame time on a large
window, and it is the first thing to reach for again.

## Ranked, what is left

1. **Shadow map resolution.** 1536² is 2.36 MPix — a bigger buffer than the
   screen it serves. At 1024² the shadow pass goes 8.76 → 5.66 ms, three
   alternations, i.e. 1.55 ms off the average frame. *Implemented.*
2. **SSAO and bloom, 4.9 ms for two effects.** AO already runs at quarter
   resolution; bloom does not. A half-resolution bright pass is the obvious
   next thing and is untested.
3. **Canopy overdraw, 6.2 ms.** The cheap fix is fewer polygons, and that is
   off the table: the 320-face crowns were raised to 320 on purpose and are
   not going back. Reducing the *number* of canopy blobs, or their size, is
   untested.
4. **A depth prepass for the cutout foliage.** Classic fix for exactly this
   shape of problem, and the measurement above suggests it would not help
   much, since the alpha test is not what is costing.

## Not measured

Frame rate on any machine but this one; what any of this does on an
integrated GPU; and whether the waterway changed the picture much — the
baseline above was taken after it went in, but there is no before.
