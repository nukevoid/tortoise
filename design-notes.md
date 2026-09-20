# Pacing the Hollow

Research for the task *"how to play mobs and realm and other items using Game
Design techniques and keep player attention + give player emotional swing."*

Everything in section 1 is measured from the shipping build on the baked level,
not estimated. Sections 2-4 are the argument. Section 5 is the work.

---

## 1. What the run actually is

**Length.** A nearest-neighbour tour of the three Sunstones is 364 m of
corridor: 88 m to the first, 52 m to the second, 224 m to the third. At
`WALK_SPEED` 1.35 m/s that is 270 s of pure walking with no mistakes and no
looking around. A real first run in a maze with no map of its own is two to
four times that, so a run is roughly **8-20 minutes**.

**The board.** 572 open cells. Four biomes, evenly held: bramble 84, birch 65,
fen 57, hollow 50. 16 berries, spread 42-224 m along the route by corridor
distance. 9 glowcaps. 12 standing threats (7 thorn-maws, 5 wasp nests).

**How much of it is dangerous.** Distance from each open cell to the nearest
standing threat:

| | |
|---|---|
| 10th percentile | 4.8 m |
| median | 11.2 m |
| 90th percentile | 24.5 m |
| within 4 m of a threat | 8.4% of cells |
| beyond 12 m of any threat | **43.5% of cells** |

**The clocks.** Nothing on this list changes over the course of a run:

| | first | then every |
|---|---|---|
| cat | 55 s | 70-140 s |
| heron | 62 s | 95-170 s |
| falling glass | 80 s | 85-150 s |
| crow dive | on sight, 15 m, line of sight | 6-7 s cooldown |

With the set-piece arbiter serialising them, that is about **one set piece
every 35-45 seconds**, from one minute in until the end.

**What damage costs.** 100 hp shown as five hearts.

| | |
|---|---|
| thorn-maw, 5 s inside it | 18-35 |
| crow strike | 17 |
| wasp sting | 6 every 2.17 s |
| heron | the run |
| berry | +32, and there are 16 of them |
| passive regen | 2.4 hp/s after 6 s without being hit |

Sprint drains stamina 23/s (4.3 s from full) and refills at 9/s walking, 16/s
standing, 26/s in the shell.

---

## 2. The techniques worth borrowing

- **The interest curve.** Attention over a session is not flat. It wants a
  hook, then a sawtooth of tension and release whose *baseline rises*, then a
  peak near the end, then a short fall. Each tooth can repeat; the baseline
  must not.
- **Tension and release.** The release is what makes the tension mean
  anything. Quiet that the player can *recognise* as quiet is worth more than
  quiet that merely happens.
- **Anticipation beats surprise.** A threat you see coming produces dread,
  which lasts; a threat that arrives produces a jolt, which does not. This
  game already knows this inside an encounter — the heron's shadow, the
  thorn-maw's windup, the wasp's rear-back. It does not do it at the scale of
  the run.
- **Consequence.** An emotional swing needs the down-swing to persist a while.
  If every loss is repaid in thirty seconds of standing still, the shape is a
  sawtooth with no trend and the player stops caring about the teeth.
- **One verb, one answer is one encounter.** Threats that share a solution are
  the same threat wearing different models, however different they look.
- **Variable and risk-gated reward.** Uniformly scattered pickups are wallpaper.
  Reward that is *placed* — clustered, and behind something — turns a danger
  map into a map of choices.

---

## 3. Diagnosis

**D1 — nothing carries.** Passive regen is 2.4 hp/s, berries are worth 512 hp
against a 100 hp pool, stamina refills at 16/s standing still. There is no
state a player can be in at minute nine that minute eight put them in. This is
the single biggest flattener: the game has teeth but no trend.

**D2 — the curve has no build.** The clocks in section 1 are constant from
62 s to the end of an 8-20 minute run. The tenth heron is the first heron. The
baseline never rises, so attention decays even though the content keeps coming.

**D3 — the quiet is accidental.** 43.5% of the board is more than 12 m from
anything standing. That is a lot of room to breathe, which is correct — but it
is wherever the generator happened not to place, so the player cannot tell a
rest from a lull, and gets the cost of the empty space without the benefit.

**D4 — there is no climax.** The third stone opens the gate; then the player
walks to a meadow and wins. The last leg is 224 m — the longest stretch of the
run — and the game is *quieter* there than in the middle. The most memorable
moment should be last and currently the last moment is a walk.

**D5 — the shell answers almost everything.** Thorn-maw, crow, heron,
glass-spider: hold Space. The wasp is the only threat that argues with that,
and it was added a day ago. Five threats, one verb.

**D6 — no foreshadowing above the encounter.** Inside three seconds the game
telegraphs beautifully. Across three minutes it telegraphs nothing. Nothing
ever tells the player that the Hollow is getting worse, because it isn't.

**D7 — reward is wallpaper.** 16 berries and 9 glowcaps scattered on open
cells with no relation to where the danger is. Nothing is a find. Nothing is a
decision.

---

## 4. What not to do

Not more mobs — there are six types and the board is 572 cells; adding a
seventh addresses none of the above. Not more damage — the problem is that
damage does not persist, and raising the numbers only raises the sawtooth.
Not a longer maze — 364 m is already past what a first run needs.

---

## 5. The work, in order

Each of these is small, measurable, and independent of the others.

**W1 — damage leaves a mark.** Passive regen stops at the top of the heart the
player is in, rather than climbing to full. Lose a heart and it stays lost until
a berry buys it back. Berries become an economy instead of a formality, a bad
encounter is felt for the next ten minutes, and the player is never dead-ended,
because there are 16 of them.
*Test:* take 45 damage, stand still 60 s, expect hp to settle at the heart
boundary (60) and not 100.

**W2 — the Hollow reacts to being robbed.** Multiply every set-piece cooldown
by a factor of the stones collected: ×1.0 at none, ×0.78 at one, ×0.58 at two.
Tied to progress rather than to the clock, so a slow explorer is not punished
for exploring and a fast one still gets the build.
*Test:* measure mean seconds between set pieces at 0, 1 and 2 stones; expect
roughly 40 s, 31 s, 23 s.

**W3 — give it a climax.** Taking the third stone opens the gate *and* wakes
the Hollow: an immediate heron pass, and the crows stop waiting for line of
sight for the rest of the run. The 224 m walk back becomes the hardest part of
the run instead of the safest.
*Test:* from the third stone to the gate, count threat events before and after.

**W4 — design the quiet.** Find the largest pockets that are already far from
everything and mark them: a shaft of light, a clear floor, a berry. A rest the
player can *see* is a rest; the same cells unmarked are just corridor.
*Test:* the marked cells are the ones section 1 measures as beyond 12 m.

**W5 — a second answer.** At least one existing threat should be beaten by
moving rather than by hiding, so the shell is a choice and not a reflex. The
wasp does this. The thorn-maw is the candidate: give its windup a readable tell
and let a sprint through the gap beat it, so the corridor becomes a timing
problem rather than a waiting problem.
*Test:* sprinting through a maw on the tell takes less damage than sheltering
through it.

**W6 — foreshadow the run.** One distant heron call and a shadow crossing far
off, thirty seconds before its first visit. A rising insect drone as the stone
count climbs. Cheap, and it converts D6 into dread.
*Test:* the cue fires before the first telegraph, not with it.

**W7 — put the reward behind the risk.** Move a third of the berries and most
of the glowcaps into the cells section 1 identifies as within 4 m of a standing
threat, in clusters rather than singly. The danger map becomes a choice map.
*Test:* the share of pickups within 4 m of a threat rises from roughly 8% to
around 40%, and total pickup count does not change.

---

*Measurements in section 1 were taken in-game on the baked level; the raycast
and BFS probes used to take them are not part of the build.*
