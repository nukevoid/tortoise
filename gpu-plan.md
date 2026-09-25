# GPU plan, round 3

Measured 2026-09-24 on the same Iris Xe as the earlier rounds, with the
built-in profiler (`__game.profile`, GPU timer queries). Every A/B figure is
**interleaved** (A B A B A B) and a difference is only claimed where it held in
every alternation; see `perf-notes.md` for why nothing else here can be trusted.

Viewpoint: the Southern Glade nest (-33.8, -32.65), yaw -π/2, looking down the
first corridor, dry weather, crows and set pieces parked. One viewpoint only —
`perf-notes.md` has the warning about what that did to an earlier conclusion.

What is new since round 2: the phone controls. The game now has to run on a
mobile GPU, and the frame there has a different shape from the desktop one.

## Where the frame goes now

```
1.93 MPix (budget cap)   31-35 ms   scene 27-30, shadow frames +3, post 3.8
1.24 MPix                27.9 ms
0.31 MPix (phone-sized)  17.6 ms    scene 15-16, post 0.5
```

Fitted over those points: **≈14 ms that does not scale with pixels, plus
≈10.8 ms per megapixel.** On the desktop that is roughly half and half. At a
phone's pixel count it is **80% fixed cost** — vertices, not fill — so the
levers that won the earlier rounds (fewer pixels, cheaper post) do almost
nothing on a phone. The post chain is 0.5 ms there.

Largest layers, by removing each one (`profileLayers`, drifting baseline
32-38 ms, so read as a ranking):

| Layer | Instances | Triangles | Removing it saves |
|---|---:|---:|---:|
| Hedge blobs (320-face, alpha-cut) | 2,810 | 899k | 14.6 ms |
| Branched bushes (5 layers: branches + leaves) | ~1,080 | 258k | 14.4 ms |
| Grass | 10,746 | 645k | 6.9 ms |
| Trunks (ground-blended cylinders) | 145 | 29k | 5.9 ms |
| Rocks | 736 | 59k | 4.5 ms |
| Tree canopies (320-face) | 318 | 102k | 2.9 ms |

Grass measured 0.05 ms in round 1's corridor view; here, at the meadow, it is
6.9 ms. The layer costs depend on where you stand.

## Found this round

**1. The point lights cost 9 ms on desktop, 30% of the frame.**
18 point lights are live: 3 sunstones, 9 glowcaps, the firefly jar, the
player's fill light and the 4 egg nests. three.js lights every fragment of
every standard material with *all* of them, whatever their distance —
they reach 3-8 m and most are 50 m away. Measured, all on vs all off:

| | on | off | difference |
|---|---:|---:|---:|
| 1.93 MPix | 30.9 / 30.7 / 28.6 | 21.2 / 20.6 / 21.2 | **−9.1 ms** (3/3) |
| 0.31 MPix | 14.3 / 15.0 | 13.1 / 13.2 | **−1.5 ms** (2/2) |

It is fragment work, so it scales with pixels. The 4 nests added in
`a6d9dcd`/`18527ec` put about 2 ms of it there.

**2. Changing the number of lights freezes the game for seconds.**
The light count is compiled into every lit shader. Hiding one glowcap light
took one frame **10.8 s** while the ~90 lit programs recompiled (104 → 188
programs; showing it again was 32 ms, from the cache). Pickups already dodge
this by zeroing a light's intensity instead of hiding it — which keeps paying
for the light, see (1). The dropped shell does not dodge it: its glow is in a
group that is hidden until you die, so **the first death of every session
changes the count from 18 to 19 and recompiles everything.** Not yet timed in
play; the 10.8 s is a hidden tab and a real frame will be shorter, but it is
seconds either way.

**3. 1.1 M triangles are drawn at zero size.**
Grass and the branched bushes dissolve past 15 m by being scaled to nothing
in the vertex shader. Their chunks still get submitted, so every vertex still
runs. 122 meshes with 1.1 M triangles lay *entirely* past their dissolve
distance from this viewpoint. Hiding them on the CPU:

| | drawn | culled | difference |
|---|---:|---:|---:|
| 0.31 MPix | 14.2 / 14.3 / 14.7 | 12.0 / 12.1 / 12.0 | **−2.3 ms** (3/3) |
| 1.93 MPix | 31.4 / 36.9 / 31.9 | 33.0 / 29.0 / 28.7 | ≈ −3 ms (2/3 — within the noise) |

On a phone, where the frame is vertex-bound, this is the one that matters.

## Plan, in order

**G1 — A fixed pool of point lights.** *Target −6 to −7 ms desktop, −1 ms
phone, and removes the recompile freezes.*
- Keep exactly K = 4 real `PointLight`s in the scene, always visible, so
  the shader's light count never changes.
- Every emitter (sunstone, glowcap, jar, nest, dropped shell, fill) becomes
  a record: position, colour, intensity, distance. Each frame, hand the pool
  to the K nearest emitters whose range reaches the camera's surroundings;
  unused pool lights get intensity 0.
- Fade a light in and out over ~0.3 s when it changes emitter, so a light
  swapping owner never pops.
- Delete `hideItemMesh`'s intensity-zero trick and the dropped shell's own
  light: both are covered by the pool.
- The halo sprites and emissive cores stay, so an emitter outside the pool
  still glows at a distance; only its light on the ground goes.
- Check: the nest you stand at, a sunstone's ground pool and the jar in the
  gloom all look unchanged. First death: no freeze. K = 4 is a guess — count
  how many emitters are ever within 8 m of each other; K = 3 may do.

**G2 — Cull what has dissolved.** *Target −2.3 ms phone, ~−3 ms desktop.*
- For each chunk of a layer with a dissolve distance, hide it when its
  bounding sphere is entirely past that distance. The shader has already made
  it invisible, so there is no visual change.
- The shadow pass draws the same chunks, so it gets the saving too.
- Follow-up, measured separately: smaller chunks for the dissolving layers
  only. 28 m buckets won the draw-call trade in `perf-notes.md`, but that was
  measured for layers that do not dissolve. For grass, a smaller chunk culls
  more of what is already invisible.

**G3 — A phone tier.** *Needs numbers from a real phone first.*
- Step 0: get the F2 overlay from an actual phone. Mobile browsers often lack
  `EXT_disjoint_timer_query_webgl2`; the profiler falls back to sync mode,
  which gives proportions but pessimistic totals. Everything below is
  unmeasured until then.
- Candidates, in the order the desktop numbers suggest:
  - Shorter dissolve distances on touch devices: 15 m → 10 m roughly halves
    what G2 leaves drawn.
  - Shadow map every 3rd frame instead of every 2nd.
  - `POST.adaptive` on by default for touch devices. It was turned off on
    desktop because the picture went soft for no visible reason; on a phone
    a steady frame rate may be the better trade.
- Not proposed: fewer faces on the blobs or canopies, or thinner bushes. The
  320-face canopies were raised on purpose and the branched bushes are a
  look the game keeps. A reduced-geometry phone tier would be a design
  decision, not an optimisation.

**G4 — Re-measure the hedge blobs after G1.** The largest single layer at
14.6 ms, and all of it fill. Some of that fill is the 18-light loop G1
removes, so its cost after G1 is unknown. Decide from the new number, not
this one.

**G5 — Find out why the trunks are expensive.** 145 cylinders, 29k
triangles, 5.9 ms: about 40 µs each, far more than anything else per
instance. Possibly the ground-blend shader over a large screen area near the
camera. A resolution sweep with only the trunks toggled will say whether it
is fill or vertices.

## Budget

| | now | after G1 + G2 (projected) |
|---|---:|---:|
| Desktop, 1.93 MPix | 31-35 ms | 22-25 ms (40+ fps) |
| Phone-sized, 0.31 MPix, this GPU | 17.6 ms | 14-15 ms |

A phone GPU is several times slower than this one, and mostly on vertices, so
G2 and G3 are what decide whether the phone version is playable. That can
only be judged on a phone.

## Measuring in a hidden tab

The profiler yields with `setTimeout(0)`, and Chrome throttles timers in a
background tab to about once a minute. A 20-frame profile that takes 0.7 s in
a foreground tab never finished, and `profileLayers` stalled for minutes.
Routing short timeouts through a `MessageChannel` for the duration of the
measurement fixes it. Also: anything that changes the light count costs a
full recompile, so a light on/off A/B has to be one alternation per call.

---

# Results

Same machine, same viewpoint, same protocol. Where a change needs a
recompile to switch (the light pool) it was one alternation per call; the
rest alternated inside one call.

| Change | 1.93 MPix | 0.31 MPix | Alternations |
|---|---:|---:|---|
| **G1** light pool, K = 4 | 33.6 / 28.6 / 28.4 → 23.5 / 26.6 / 21.9 ms, **≈ −5 ms** | — | 3/3 |
| **G2** dissolve cull | 24.6 → 21.7 ms, **−2.9 ms** | 13.6 → 10.5 ms, **−3.1 ms** | 3/3 each |
| G2 follow-up: 12 m chunks for dissolving layers | 21.7 → 21.2 ms | 10.6 → 10.1-11.2 ms | within the noise |
| **G3** phone tier (shadow every 3rd frame) | — | 10.1 → 9.7 ms, **−0.4 ms** | 3/3 |

Put together: **about 33 ms → 21-22 ms at 1.93 MPix, and 17.6 → about
9.7 ms at a phone's pixel count**, on this GPU. The desktop budget of 22-25 ms
was met.

G1 saved less than the 9 ms that removing every light did, as it should:
four lights are still paid for on every pixel. It also removed both
recompile freezes. The first death was a full recompile and is now a
normal frame (39 ms against 40 ms before it, no stall), after the dropped
shell was compiled at boot as well — its own shaders had cost 366 ms on
first use once the light count was fixed.

`hideItemMesh`'s intensity-zero trick was kept rather than deleted, as the
plan said: an emitter at zero intensity is simply never picked for the pool,
so it is now the right way to switch one off, not a workaround.

Checked by eye at the Lake Haven nest in third person, pool against the old
lighting: the nest's glow on the ground and the fill on the tortoise are the
same.

**G2 did better than the plan said** because it also takes the far chunks
out of the shadow pass, which was drawing them full-size (the depth material
does not dissolve) and casting shadows of grass that was not there.

**G3, corrected.** Pulling the dissolve distance in from 15 m to 10.5 m was
built and measured: 13k of 1.55M triangles, nothing measurable. It was taken
out rather than change the look for nothing. What is left in front of the
camera is layers that do not dissolve:

```
751k  hedge blobs, 320 faces          (49%)
125k  unnamed, 70 faces
 82k  tree canopies, 320 faces
 81k  unnamed, 20 faces
 65k  ground
```

**G4.** After G1 the hedge blobs cost 7.3-8.8 ms at 1.93 MPix (was 14.6 ms)
and **5.4 ms of a 10 ms frame at 0.31 MPix**, most of it vertices. On a phone
they are the frame. The one lever is their face count, and 320 faces is a
look the game has chosen; round 1 found 180 faces still read as leaves at
0.58 m. A 180-face hedge for touch devices only would be the next step, and
it is a design decision, not an optimisation.

**G5.** The trunks cost 0.05-0.6 ms, not 5.9. The round-3 layer sweep ran
with the 18 lights still in and a drifting baseline; nothing to do.

Also measured and not worth doing: camera far plane 400 m → 110 m (fog is
99% at 110 m) changed nothing — 556 triangles, 2 calls. The Hollow is small
enough that nearly everything is inside 110 m anyway.

Not measured: any real phone. The phone numbers above are this Iris Xe at a
phone's pixel count, which tells you the shape of a phone frame, not its
length.

## G6 — Shared vertices on the blobs

Found after the round, looking for anything left that costs nothing to the
picture. `IcosahedronGeometry` is a triangle soup: every face carries its own
three corners. The blobs' normals are a function of position, so the copies
are bit-identical and can be shared through an index. Where they are not —
the uv seam — they stay separate. `blobGeo` now returns the indexed form.

| Blob | Vertices | Instances |
|---|---:|---:|
| 320 faces (hedges, canopies) | 960 → 183 | 3,128 |
| 180 faces | 540 → 101 | 642 |
| 80 faces (buried cores) | 240 → 57 | 388 |

Measured against the soup, swapped at runtime with `__game.setBlobSoup`, 3/3:

| | soup | indexed | |
|---|---:|---:|---:|
| 0.31 MPix | 16.0 / 15.7 / 16.6 | 10.7 / 10.4 / 10.8 | **−5.4 ms, −34%** |
| 1.93 MPix | 25.8 / 26.6 / 25.7 | 21.8 / 20.8 / 20.8 | **−4.9 ms** |

Picture: a readback of the whole frame differs from the soup by 2.785/255 on
average, against 2.767 soup-to-soup and 2.789 indexed-to-indexed — the film
grain's own noise — and mean luminance is the same.

On a phone, this is most of what G4 was asking for — half the hedge cost
at phone resolution was vertices — and it did not need a single face
removed. The absolute numbers in this tab ran about 5 ms higher than in
the earlier one; only the differences carry over.

The rocks are the one other soup and do not merge: they are flat-shaded, so
every face has its own normals.
