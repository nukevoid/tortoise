# Multiplayer plan

Two players in the same Hollow, over PeerJS (WebRTC, browser to browser). The
game stays one static HTML file on GitHub Pages; there is no server of ours.

## Status

**Built: S1 to S5, and part of S6.** All of it is in section 12c of
`tortoise.html`, plus small hooks in the creature, item, weather, raft,
death and main-loop code.

Tested with the host page and a guest in an iframe on one machine, both
driven from the console. Each line below was checked in the running game:

| What | Result |
|---|---|
| Lobby: code, link, third player refused, wrong code | as before |
| Start while the guest is still loading | guest joins when its load finishes |
| Poses both ways | each side has the other's exact position; guest starts 0.9 m beside the host |
| Partner's tortoise | drawn with a "Partner" tag, in first and third person |
| Thorn-maw 64 m from the host, next to the guest | host wakes it and targets the guest; guest sees all 41 parts animate; bites land (100 → 91); the shell refuses them |
| Glass | telegraph → fall → guest trapped; the spider bites through the forwarded hit; the trap releases |
| Cat | stalk → crouch → pounce on the guest; shoved at 2.7 m/s and flipped |
| Heron | telegraph → strike → seize → feed; the guest dies with the heron's death text |
| Crow | hunts the guest, strikes for 17, the guest's danger badge lights |
| Items | guest's berry goes to the guest; host's sunstone counts for both, with a "your partner found" message |
| Gate and win | three stones between them open both gates; one player through wins for both |
| After a win | both back to the lobby, the host starts again with a fresh world |
| Death | guest respawns at the start or their nest; the world carries on |
| Rafts | the guest's leaf moves on the host to within 2 cm; stepping off is seen |
| Weather | host's storm and lightning reach the guest |
| Host paused, or tab hidden | the world keeps running for the guest (the hidden-tab path ran the whole test) |
| Leaving | guest leaves from the pause screen → own menu; host plays on and creatures target only them. Host leaves → guest gets "The host left" |
| Bandwidth, host → guest | 61 KB/s beside a thorn-maw |
| Single player | thorn-maw bites, pickups work, no console errors |

**Seeds.** Starting a game reseeds `RNG` on both sides from the host's
seed, so anything each side still draws for itself — the crows' first
perches in `resetPlayer`, for one — comes out identical. It cannot keep the
creatures in step. They react to both players, each machine steps them at
its own frame rate, and `Math.sin` and friends are not guaranteed
bit-identical between browser engines. So the host simulates them and the
guest is sent the result.

**Not done:**

- Reconnecting after a dropped connection (S6). A guest who drops has to
  join again as a new game.
- The latency and loss test harness (S6), and any test between two real
  machines, on mobile data, or on iPad Safari.
- A TURN relay. Some networks will fail to connect directly.

**Known gaps:**

- You do not see your partner's dropped shell.
- The heron lifts the guest on the host's screen but not on the guest's
  own: the guest's position is sent, but its update puts the camera back on
  the ground.
- A paused player cannot be targeted. Pausing in a shared game makes you
  safe, since the world cannot stop for one player.
- Creature sounds reach the guest only when the creature is acting on them,
  or within 14 m of them.

## The facts that decide the design

Measured or read from the code, not assumed:

1. **The world cannot be simulated twice.** The seeded `RNG()` is drawn more
   than 100 times at run time (creature decisions, weather, set pieces). Two
   copies would drift apart within seconds. **One browser — the host — owns
   the world.**
2. **The map needs no syncing.** The level is baked into the file
   (`LEVEL_BAKED`) and generated from a fixed seed, so both players build an
   identical Hollow. Only what changes needs sending.
3. **The game assumes one player everywhere.** `P` appears 101 times, 46 of
   them in creature code: `mobDist(m)`, waking by `activeRange`,
   `mobStrike()` calling `hurt()`, the heron seizing `P`, the glass trapping
   `P`, the cat flipping `P`, `updateStage` reading `P.flipped`.
4. **Creature logic and animation are one function.** Each type's `think()`
   decides and animates in the same code, so the guest cannot run "only the
   animation" without splitting eight functions.
5. **Most creatures place parts in world space.** 7 of 8 types are
   `worldSpace`, and some add parts to the scene directly (the threat
   shadows), so mirroring `m.group` alone misses parts.
6. **Part counts are small.** Most objects per creature: thornmaw 41, glass
   55, cat 38, fish 30, wasp 22, heron 15, beetle 10, skater 9; plus 2 crows.
   Sending the parts of creatures near the guest, 16-bit quantised, is about
   3.5 KB a snapshot — **~50 KB/s at 15 Hz**, comfortable for WebRTC.
7. **The host stops when its tab is hidden.** The game runs on
   `requestAnimationFrame`, and a background tab gets none. Left alone, the
   host switching tabs freezes the world for both players.

## Architecture

- **Host** runs everything it runs today, for two players: creatures, crows,
  set pieces, items, gate, weather, rafts, time.
- **Guest** runs its own tortoise (movement, shell, flip rhythm, camera,
  HUD, sound) and shows the world the host sends. It does not run `think()`,
  weather or item logic.
- **Each player owns their own tortoise.** Movement is client-authoritative:
  it is co-op, cheating is not a concern, and it keeps controls instant.
- **Two channels.** The PeerJS connection is reliable and ordered, which is
  right for events (a pickup, a hit, a death) and wrong for snapshots: one
  lost packet stalls everything behind it. Open a second connection with
  `{reliable:false}` for poses and snapshots.
- **Binary snapshots.** JSON is fine for events. Snapshots use an
  `ArrayBuffer` with 16-bit quantised positions and quaternions. PeerJS
  sends binary as-is.
- **Interpolation.** Snapshots are drawn 100 ms behind, interpolated between
  the two nearest, so 15 Hz looks smooth.

### Messages

| Channel | Direction | Messages |
|---|---|---|
| reliable | both | `hello` `ping`/`pong` (done), `start`, `bye` |
| reliable | host → guest | `world` (full state on join), `picked`, `gate`, `nest`, `hurt`, `flip`, `toss`, `trap`/`untrap`, `seize`/`release`, `sfx`, `toast`, `lightning`, `win`, `restart` |
| reliable | guest → host | `pick` (request), `died`, `respawned`, `board`/`leave` (raft) |
| unreliable | both | `pose` (own tortoise, 20 Hz) |
| unreliable | host → guest | `snap` (creatures, crows, rafts, weather; 15 Hz) |

## Stages

Each stage is playable and testable on its own. Rough effort is in
focused working days, and is a guess.

### S1 — Start together, see each other (~1-2 days)

- The host's lobby gets a **Start** button once a partner is connected.
  `start` puts both into play at the start nest; the guest checks a hash of
  `LEVEL_BAKED` first, so mismatched builds refuse to start.
- **Refactor the tortoise into `makeTortoise()`.** It is built once at top
  level into `bodyRig` today. The factory returns the rig and its animated
  parts; the leg, head and shell animation takes (rig, pose) instead of
  reading `P`. The local player uses it exactly as before.
- `pose` at 20 Hz: position, yaw, speed, hideAmt, flipped + flipAngle,
  tumble, raft id, lantern on, alive.
- The partner is drawn from interpolated poses, with a small name tag and a
  dot on the minimap.
- Disconnect: the host plays on alone; the guest sees "The host left" and
  returns to the menu.
- Test: both walk; each sees the other in first and third person; pulling
  into the shell shows on the other side.

### S2 — One world state (~2 days)

- **Items.** The guest's pickup sends `pick {id}`; the host checks it is
  still there and broadcasts `picked {id, by}`. Whoever sent it gets the
  item.
- **Sunstones** count for both, and the gate opens for both at three.
- **Nests** are shared discoveries; each player respawns at the last nest
  *they* claimed.
- **Weather** comes from the host: state in the snapshot, lightning as an
  event. The guest's `updateWeather` does not run.
- **Time.** Set-piece timers read the host's play time, which is sent in
  the snapshot.
- **Saving.** Multiplayer sessions do not read or write the single-player
  save.
- **Joining late:** `world` carries everything at once: collected items,
  stones, gate, nests, weather, time, creature states.

### S3 — Creatures for two (~4-6 days, the big one)

On the host:

- **Two players in the creature code.** Players become a list of records:
  local `P` plus a remote record with the same field names (`pos`, `hidden`,
  `hideAmt`, `flipped`, `raft`, `vel`, `trap`...), kept up to date from
  `pose`. Existing expressions like `P.pos.x` become `tgt.pos.x`, so most
  edits are mechanical.
- **Each creature picks a target.** `mobTarget(m)` returns the nearest
  living player, preferring one out of its shell for the ones that give up
  on shells. `mobDist(m)` becomes the distance to that target.
- **A creature is awake if it is near either player.** Otherwise one
  player's corner of the map freezes whenever the other is far away.
- **Hits go to whoever was struck.** `mobStrike(m, …)` hurts the target: a
  local `hurt()` for the host, a `hurt` event for the guest.
- **Fairness under latency.** The host resolves a strike with a pose up to
  ~100 ms old, so a guest who shelled just in time could be hit. The guest
  checks its own clock and ignores a `hurt` if it was sheltered at the
  strike moment. It is co-op, so trusting the guest costs nothing.
- **Sound and messages.** A creature's `SFX` calls and `toast`s go to the
  player they concern: sounds as `sfx {name, x, z}`, played by the guest if
  within range.

On the guest:

- **Mirror parts, do not simulate.** At spawn, record every object the
  creature owns: its group subtree, plus anything its `build` added straight
  to the scene (found by comparing `scene.children` before and after). Each
  snapshot carries, for creatures near the guest: visibility, and position,
  rotation and scale for parts that moved, plus the few animated material
  values (shadow opacity, emissive glow). The guest applies them and runs no
  `think()`. This handles all eight types with no per-type code. That is
  why it comes before the alternative: a per-type `pack`/`unpack`, which
  needs `think()` split in eight places.
- Crows the same way.
- Test, per creature type: the guest walks into it alone, and it wakes,
  animates, strikes, and is refused by the shell, as it is for the host.

### S4 — What creatures do to a player (~2-3 days)

These change the *player*, so they become events to whoever was targeted:

- **Cat:** `toss` (skid direction and speed) and `flip` (rolls you over).
  The flip-out rhythm runs on the victim's own client.
- **Glass:** `trap`/`untrap`, including the spider inside it.
- **Heron:** `seize`/`release`. While seized, the victim's pose follows the
  beak, and the host sends the beak's position.
- **Set pieces:** `updateStage` holds the stage while *either* player is
  flipped. The set piece picks one of the two players.
- **Rafts:** the rider owns their raft's motion; the host hands ownership
  over on `board` and back on `leave`. Two on one raft: the first aboard
  owns it.

### S5 — Death, winning, restarting, pausing (~2 days)

- **Death is per player.** A dead player drops their own shell (so the
  dropped shell needs a second copy), waits, and respawns at their nest
  while the world carries on. Only both being dead at once shows the death
  screen for both and resets the world.
- **Winning:** decide (see below). The host broadcasts `win`.
- **Pausing** in multiplayer does not stop the world. It opens the menu
  over a running game.
- **Host tab hidden:** while a partner is connected, the host keeps
  simulating from a `MessageChannel`-driven tick, which is not throttled
  like timers or `requestAnimationFrame`, skipping rendering. The guest
  gets "Host is away" if snapshots stop anyway.

### S6 — Robustness (~2-3 days)

- **Reconnect:** a guest that drops can rejoin with the same code and
  receives `world`.
- **Latency test harness:** a delay and loss queue in `netSend` to play at
  150 ms / 5% loss on one machine.
- **Connection failures:** measure how often direct connection fails
  between two real networks. If it is often, add a TURN relay (an account
  with a provider) — the main thing that could make this cost money.
- **Performance:** the host renders one view but simulates both players'
  surroundings. Profile a host whose partner is at the far side of the map.

## Decisions for you

1. **Winning:** does one player reaching the Sun Gate win for both, or must
   both be through?
2. **Items:** berries and glowcaps go to whoever picks them up — fine? And
   the firefly jar exists once: only the one who finds it gets the lantern?
3. **Death:** respawn at your nest while the partner plays on (planned), or
   one death ends it for both?
4. **Difficulty:** two players make everything easier — more hands for
   sunstones, a second target to split the creatures. Scale anything up
   (more crows, shorter set-piece gaps)?

## Testing

Two copies of the game on one machine: the host page, and the guest in an
iframe opened from the join link. This is how the lobby was verified. A
driving tab in the background is throttled and eventually frozen by Chrome,
so the tab under test must stay the active one. Real two-device tests (PC +
phone) at the end of every stage.
