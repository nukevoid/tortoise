# Optimisation plan

Measured, not guessed. Every number below was taken in-game on this machine
(integrated GPU) at 0.85 render scale, standing in a corridor at cell (6,6)
looking along it, medians of repeated runs. Absolute numbers on this box drift
between sessions, so all of it was taken back-to-back in one session and any
change must be re-measured interleaved against its parent commit.

## Where the frame goes

Frame at 0.85 scale: **41.4 ms** (~24 fps). 2.31M triangles, 349 draw calls.

Cost by scene layer, measured by hiding each layer and re-timing:

| Layer | Instances | Triangles | Cost |
|---|---:|---:|---:|
| **Hedge bush blobs** | 3197 | 1,023,040 | **12.07 ms** |
| Hedge crowns | 552 | 176,640 | 2.14 ms |
| Tree canopies | 418 | 133,760 | 1.14 ms |
| Hedge leaf cards | 3864 | 25,760 | 0.80 ms |
| Big broad leaves | 1575 | 25,200 | 0.67 ms |
| Meadow scrub | 46 | 14,720 | 0.48 ms |
| Ferns | 1417 | 7,557 | 0.20 ms |
| **Grass** | 7975 | 159,500 | **0.05 ms** |
| everything else | — | — | ≈0 |

Other whole-pass costs:

| Pass | Cost |
|---|---:|
| Shadow map render | 9.85 ms |
| SSAO + bounce (1/3 res) | 2.16 ms |
| Bloom chain | 1.15 ms |
| FXAA (in composite) | 0.36 ms |

Resolution sweep — 0.6 → 34.25 ms, 0.85 → 41.74 ms, 1.1 → 56.68 ms. Fitting
against pixel count gives **≈25 ms resolution-independent + ≈17 ms fill** at
0.85. So the frame is roughly half geometry/CPU and half fill rate; dropping
render scale alone cannot fix it.

## What this says

The four blob layers are **15.8 ms, 38% of the frame**, and the bush layer
alone is 29%. They are also most of what the shadow pass draws. Grass, ferns
and leaf cards — the things that *look* expensive — are noise.

The blobs got to 320 faces each because the bushes read as polygonal. That was
the right call for the silhouette, but the silhouette is now carried by the
alpha cutout at the rim, not by the polygon count, so most of those triangles
are buried inside the wall where nothing can ever see them.

## Plan, in order of measured gain per unit of risk

**P1 — Stop paying for buried triangles. Target −5 to −7 ms.**
Blobs come in two populations: the face/corner/crown ones that form the
visible surface, and the interior ones buried in the wall mass. Only the first
can ever be silhouetted.
- P1a. Split the bush layer into `surface` and `buried`; buried uses 80 faces
  (detail 1), surface keeps 320.
- P1b. Buried blobs stop casting shadows — they are inside a mass that already
  casts one.
- Risk: low. Verify by walking a hedge line and checking no new gaps appear.

**P2 — Shadow pass, 9.85 ms. Target −3 to −5 ms.**
- P2a. Drop the shadow map 2048 → 1536 and re-measure quality at the tortoise's
  eye height, where shadows are seen at a grazing angle anyway.
- P2b. Re-render the shadow map every other frame. The sun rig follows the
  player at ~2 m/s; a one-frame lag is 3 cm.
- Risk: P2b can shimmer if the player turns fast. Check while sprinting.

**P3 — Fill rate, ≈17 ms at 0.85. Target −2 to −4 ms.**
- P3a. SSAO to 1/4 resolution from 1/3 (−1 ms, blur already hides it).
- P3b. Pull fog in slightly so distant chunks fall out of the frustum sooner,
  and confirm against the Sunstone light shafts, which must stay visible.

**P4 — 349 draw calls. Target −80.**
Chunking is 26 m; many chunks hold a handful of instances. Merge chunks below a
threshold into a neighbour, or widen chunk size for layers with few instances.
- Risk: low, but measure — chunking measured as *not* paying before.

**P5 — Boot, ≈800 ms of the ~1.5 s is shader compilation** ("Settling the
shadows" phase, which is `renderer.compile` plus the first frame). Each
`patchFoliage` variant compiles its own program because the cache key differs.
Reduce the number of distinct variants.

## Explicitly not worth doing

These were tried or measured and did not pay. Do not redo them:

- **Per-chunk LOD twins** (320-face near / 80-face far, swapped by distance):
  built, measured, **0.6 ms saved for ~70 extra meshes**. Removed.
- **Removing the alpha cutout**: toggling `alphaMap` off changed the frame by
  **−0.5 ms**, i.e. nothing. The cutout is not what costs.
- **Thinning grass**: the whole grass layer is **0.05 ms**. There is nothing
  to win there, and it is a signature of the game's look.
- **Rendering without the post stack**: *slower*, 52.29 ms vs 41.74 ms,
  because the no-post path targets the MSAA default framebuffer. The post
  pipeline is already the cheap path.

## Budget

Target on this machine: **≤ 25 ms at 0.85 scale** (40 fps), from 41.4 ms.
P1 + P2 + P3 together are projected at −10 to −16 ms. If they land, the
adaptive scaler stops having to drop below 0.85 in normal play.
