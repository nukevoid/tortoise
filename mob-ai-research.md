# Mob AI Research: An Autonomous Living Ecosystem for the Hollow

Research for the task *"do research for more interesting AI for all mobs (don't implement, only research in MD). They have to interact and feel like they live their life."*

Like [design-notes.md](file:///D:/temp/tortoise/design-notes.md), this document is grounded directly in the shipping architecture, coordinate system, tick mechanics, and performance budgets of `tortoise.html`. Section 1 diagnoses how mobs function today and why the Hollow feels like a clockwork diorama. Section 2 establishes the ecological design pillars. Section 3 covers all eight species in granular biological, mechanical, and mathematical detail. Section 4 defines the multi-species interaction matrix. Section 5 details internal homeostatic drives and autonomous routines. Section 6 maps weather and biome integration. Section 7 specifies a zero-allocation, 60 FPS runtime architecture for Three.js.

---

## 1. What Mobs Do Today: The Solipsism Diagnosis

### The Current Roster and Spatial Footprint
In the current baked level (`LEVEL_BAKED`, 572 open hexagonal cells across a 92×92 m clearing, `HALF = 46`):

| Mob | Count / Spawning | `activeRange` | Sense / Reach | Speed | Current Behavior |
|---|---|---|---|---|---|
| **Thornmaw** | 11 placed (6 gloom, 5 woods) | 24 m | sense 3.15 m / reach 1.95 m | 0 m/s (rooted) | Staggers 3 shoots; snaps at player; sleeps after 2.2 s of shell |
| **Heron** | 1 (director set-piece) | $\infty$ (worldSpace) | first visit 172 s, cd 95–170 s | airborne / hover | Drops shadow over player; kills outright unless sheltered |
| **Cat** | 1 (director set-piece) | $\infty$ (worldSpace) | first visit 55 s, cd 70–140 s | 2.4 m/s (sprint 5.2 m/s) | Stalks player, pounces, flips tortoise onto back |
| **Wasps** | 5 nests (1 worker per nest) | 26 m | wake 5.0 m / leash 11.0 m | 3.1 m/s | Hovers over player, stings for 6 dmg every 1.5 s; ignores shell |
| **Beetles** | 9 placed in open cells | 18 m | shy 1.6 m | walk 0.55 m/s, scuttle 2.4 m/s | Wanders randomly; swerves along hedges away from player |
| **Pond Skaters**| 26 placed on waterway | 16 m | shy 1.5 m | glide 1.35 m/s | Shove-and-glide on lake water; scatters from player |
| **Crows** | 2 spawned in open air | $\infty$ (global array) | sight 15 m (LOS), reach 0.95 m | patrol 3.0 m/s, dive 5.4 m/s | Waypoint patrol; dives at player for 17 dmg; flees shell |
| **Large Fish** | 0 (unimplemented) | N/A | N/A | N/A | Planned lake creature; absent from current loop |

### The Three Structural Flaws

1. **Player-Centric Solipsism (`O(1)` against Player, `0` against World).**
   Every single tick function in `tortoise.html` evaluates only one distance vector:
   $$\vec{d}_{\text{mob}} = \mathbf{P}_{\text{pos}} - \mathbf{M}_{\text{pos}}$$
   The cat has no pointer to beetles. The heron cannot see fish or skaters. Crows ignore the cat. Wasps never leave their nest radius except to chase the tortoise. The mobs do not inhabit an ecosystem; they inhabit an obstacle course where every actor is wired directly to the player's gamepad.

2. **The "Frozen in Amber" Problem (`activeRange` Sleep).**
   In `updateMobs(dt)` (lines 5278–5294), if `mobDist(m) > m.def.activeRange`, `m.awake` becomes `false`. The mob's mesh is hidden, `m.t` stops incrementing, and `m.def.think` is never invoked. When the player walks within 16–26 metres, the mob awakens with its timers freshly unpaused. You never catch a beetle halfway through rolling a piece of moss, a cat grooming on a warm sun-warmed stone, or a heron swallowing a silver fish—mobs only exist when they are performing for the lens.

3. **Total Indifference to the Elements.**
   The game now features rich, dynamic atmospheric systems: dense fog, wetness transitions (`WEATHER.wet` 0.0 to 1.0), and violent thunderstorms with rolling Web Audio thunder and multi-stroke lightning flashes (`WEATHER.storm`). Yet during a violent thunderstorm, pond skaters skate blithely across rain-lashed water, wasps hover through torrents that would shred insect wings, and cats wander through sodden mud despite their established abhorrence of water.

---

## 2. Core Ecological Design Pillars

To make the fauna feel like they live their own lives without compromising the tight game-feel established in `design-notes.md`, four design pillars must govern every addition:

1. **Uninterrupted Rule of the Shell.**
   Nothing in the expanded AI may undermine the player's core verb:
   > *"The shell is the answer to everything, so nothing is allowed to route around it."* (`tortoise.html:5171`)
   Inter-mob conflicts must never create impossible checkmates for the player. If a crow mobbing a cat causes the cat to bolt, the cat's collision with the player must still honor `playerSheltered()`.

2. **Vivid Environmental Telegraphy.**
   An animal pursuing its own life is more interesting to observe than a homing missile. When a heron is fishing at the lake, its posture must communicate its focus: a stationary S-curve neck, poised beak, and rhythmic foot-lifts. If the player approaches, its transition from "fishing" to "noticing the tortoise" must have an unmistakable tell (frozen neck, ruff flare, low warning croak).

3. **Emergent Storytelling via Food Webs.**
   Instead of scripted set-pieces, drama should emerge systemically. A crow dropping out of the sky to steal a berry cache, getting chased off by a defensive wasp, and knocking a beetle off a rock onto its back creates an unscripted, memorable moment that costs zero hand-crafted animation frames.

4. **Zero-Allocation 60 FPS Budget.**
   The game runs in a browser tab at 60 FPS on integrated GPUs. Mobs cannot allocate closures, object literals, or temporary `THREE.Vector3` instances in their update loops. Proximity queries between mobs must use spatial binning or flat array iteration without invoking the garbage collector.

---

## 3. Deep Coverage of All Mobs

```
               [ CROW ] ──(aerial mobbing)──> [ HERON ]
               ▲   │                            │
  (steals food)│   │(dives at)                  │(spear-fishes)
               │   ▼                            ▼
  [ WASP ] <── [ CAT ] ──(pounces on)──> [ LARGE FISH ]
     │             │                            │
(defends)     (paws at)                         │(surfaces for)
     ▼             ▼                            ▼
[ BERRY ]     [ BEETLE ] ──(drifts into)──> [ SKATER ]
                   │
             (snapped by)
                   ▼
             [ THORNMAW ]
```

---

### 3.1 Thornmaw (*Vorax spinosa*) — The Ambush Carnivorous Flora

Rooted pitcher-plant with three thorny serpentine shoots (`GEO_THORN_STEM`, `GEO_THORN_JAW`). Currently 11 placed specimens acting as static damage corridors.

```
       DORMANT ──(ground vibration)──> PRIMED
          ▲                               │
    (digest 60s)                    (reach < 1.95m)
          │                               ▼
      ENGORGED <──(swallow prey)──── STRIKE
          ▲                               │
          └────────(heavy storm)──────────┘
```

#### Biology and Internal State
The Thornmaw is not an automaton; it is a metabolic predator with a digestive cycle:
- `dormant`: Bulb resting on ground (`bulb.scale.y = 0.50`), shoots swaying passively in the wind (`len = 0.45`), jaws relaxed (`open = 0.08`).
- `primed / agitated`: Senses ground vibrations. Shoots coil back in an S-curve (`len = 0.38`), jaws gaping wide (`open = 0.85`), emitting a low rhythmic hiss.
- `strike`: Snaps forward at lightning speed (`len = 1.36`).
- `engorged / digestive slumber`: Triggered after successfully snapping a prey entity (beetle or bird). The bulb swells (`bulb.scale.set(1.25, 0.95, 1.25)`), its emissive core pulses with deep bioluminescent purple-green (`emissiveIntensity` oscillating 0.4 to 1.2 at 0.5 Hz), and all three shoots droop limply to the ground (`len = 0.30`, jaws slack). Lasts 45–75 seconds. During this window, the corridor is completely safe to traverse.
- `wilting / protected`: Triggered by heavy rain (`WEATHER.wet > 0.80`) or thunderstorms. Excess water floods the digestive cup. Shoots coil tightly around the bulb like closed sepals, refusing to open.

#### Vibration Sensitivity (Footstep Acoustics)
Instead of a simple geometric sphere (`mobDist < 3.15`), the plant senses acoustic vibrations propagated through the soil:
- Tortoise crawling (crouched/slow, $< 0.8\text{ m/s}$): Seismic range = 1.8 m (player can sneak past).
- Tortoise walking (normal, $1.05\text{ m/s}$): Seismic range = 3.2 m.
- Tortoise sprinting ($2.75\text{ m/s}$): Seismic range = 5.5 m (shoots awaken early and snap proactively).
- Beetle scuttling ($2.4\text{ m/s}$): Seismic range = 1.4 m.

#### Inter-Mob Interactions
- **Beetle Trapping**: Beetles wandering within `THORN.reach` (1.95 m) trigger an immediate single-shoot strike. The shoot snaps down, scoops the beetle into its jaw cone, and retracts back into the central bulb with a wet squelch (`SFX.thornBite(true)`). The beetle is despawned, and the plant transitions immediately into `engorged` slumber for 60 seconds.
- **Baiting Mechanics**: A clever player can deliberately herd a wandering beetle into a Thornmaw corridor, wait for the plant to strike and swallow the beetle, and then safely walk through the sleeping maw without taking damage or spending stamina.

---

### 3.2 Heron (*Ardea titan*) — Aerial / Lake Apex Hunter

The Hollow's apex avian predator. Currently an abstract off-screen entity that projects a shadow and neck rig (`HERON.firstVisit = 172`, `HERON.descend = 0.95`, `HERON.seize = 0.45`).

#### Natural Habitat & Perching Routine
The Heron should not only exist as an orbital airstrike summoned by a timer; it has an ecological home: the Central Lake (`WAY`, `LAKE_R = 12.5m`):
- `lake perching`: Spawns visibly on top of dead tree trunks (`GEO_TRUNK`) or high mossy rocks surrounding the water basin. It perches motionless for 60–120 seconds, head tucked into an S-curve (`heronNeck`), wings folded.
- `wading / stalking`: Descends from the perch to the lake margin where water depth is shallow ($0.04 < \text{depth} < 0.22\text{ m}$). It wades with excruciating, glacial deliberation (0.25 m/s), lifting each yellow leg (`matHeronB`) high out of the water to minimize ripples, eyes locked on the water surface.
- `water strike`: When a pond skater or large fish approaches within 2.8 m, the neck uncoils with terrifying velocity: the beak penetrates the waterline, generating a ring splash and water spray particle burst. If successful, the Heron rears back with a wriggling fish or skater in its beak, tilts its skull upward (`pitch = -0.6`), jerks its throat to swallow, and settles back into vigilance.

#### Player & Corridor Encounters
- When the set-piece clock triggers a hunt, the Heron takes flight from the lake, circling overhead at 12 m altitude. Its flight shadow sweeps across the maze hedges before locking onto an exposed player in a clearing.
- **Carapace Reaction**: When the strike hits a sheltered tortoise (`mobStrike` returns `false`), the beak clatters violently against the marginal scutes (`SFX.heronMiss`). Instead of immediately vanishing, the bird recoils, hops backward two steps flapping its huge wings, delivers two indignant diagnostic pecks at the hard shell (`clack-clack`), emits a rasping, guttural croak, and takes off vertically into the sky.

#### Weather and Storm Response
Herons rely on optical clarity and aerodynamic lift.
- In fog or mist (`fog.density > 0.035`), its strike accuracy degrades: its telegraph shadow becomes diffuse and wider (`radius = 4.2m`, `opacity = 0.35`).
- During thunderstorms (`WEATHER.storm`): High gust velocities and lightning flash blinds avian retinas. The Heron will never take flight. If caught aloft when a thunderstorm starts, it immediately abandons the hunt, gliding steeply down to shelter within the densest birch tree canopy near the lake.

---

### 3.3 Cat (*Felis silvestris*) — Curious Opportunist & Undergrowth Hunter

A leggy, curious feline (`SH = 0.33m`, `matCat`, 4 articulating legs, swishing 6-segment tail). Currently an antagonist that circles and flips the tortoise every 70–140 seconds.

#### The Curious Life of the Cat
A real cat does not spend its existence waiting in an ether dimension to push a tortoise. It has routines:
- `patrolling / scent marking`: Wanders the open hex corridors at a relaxed trot (1.2 m/s). Periodically stops at birch tree bases or corner rocks, arches its spine, rubs its cheek scent glands against the bark (`muzzle.position.x` tilt), and claws at root bark.
- `sunbathing & grooming`: In dry, sunny weather (`WEATHER.wet < 0.15`), the cat seeks out open, sunlit hexagonal clearings or rest pockets (`REST`, cells > 20 m from hazards). It curls into a loaf or side-pose, licking its raised forepaw and washing its ears, tail flicking lazily.
- `undergrowth stalking`: If a beetle is detected within 6.0 m:
  1. *Freeze*: Ears swivel forward, pupils dilate.
  2. *Low Stalk*: Body lowers until chest and belly brush the grass (`SH -> 0.14m`), moving forward at 0.4 m/s only when the beetle is moving away.
  3. *The Butt Wiggle*: Rear haunches elevate (`haunch.position.y += 0.06`), tail tip twitching sharply with rapid oscillation (6 Hz) for 1.2 seconds.
  4. *The Pounce*: Explosive spring covering 2.5 m in 0.35 s, landing front paws over the beetle.
  5. *Play with Prey*: Unlike the Thornmaw, the cat does not immediately consume the beetle. It bats the beetle with left and right paw swipes, sending it spinning across the path, watches it right itself, and bats it again until bored.
- `leaf chasing`: When falling leaves (`leafData`) tumble past in wind gusts (`gustU.value > 0.7`), the cat will rear up on hind legs to swat at swirling foliage particles.

#### Interaction with the Tortoise
- If the tortoise is in its shell: The cat does not pounce with hostile force. It approaches inquisitively, sniffs the shell opening (`SFX.catMew`), sits on its haunches, and occasionally bats the dome with a soft paw, trying to find a purchase to tip it over.
- If the tortoise is walking: The cat stalks parallel in the flanking brush, dashes ahead, and lies across the corridor path belly-up, demanding attention or setting an ambush.

#### Hydrophobia & Storm Terror
Cats despise getting wet:
- `catAshore(m)` is already in code: it refuses water deeper than 0.02 m.
- At `WEATHER.wet > 0.25`: The cat's walking posture changes: it lifts each paw with exaggerated disgust, shaking droplets from its feet on every fourth stride.
- At `WEATHER.wet > 0.70` or `WEATHER.storm`: The cat enters a panicked gallop (4.5 m/s), fleeing open corridors to squeeze beneath the low overhang of the Gloom Grove canopy or the hollow roots of ancient birch trees. While sheltering, it remains completely inactive as a threat to the player.

---

### 3.4 Wasps & Nest (*Vespula silvatica*) — Eusocial Colony

Currently 5 hanging paper nests spawning solitary workers with an 11 m leash and 6 dmg stings.

#### Colony Architecture & Worker Roles
A wasp nest should be an active eusocial hub rather than a proximity mine:
- **The Nest Hub**: Modeled as an active hexagonal papery spire attached under tree branches. It possesses an internal population count (3–4 workers) and a colony alarm index ($0.0 \le \text{alarm} \le 1.0$).
- **Worker Foraging Flights**:
  - Rather than hovering static inside the nest, 1–2 worker wasps leave the nest on foraging excursions.
  - They fly low along corridors (altitude 0.8–1.4 m) seeking sugar sources: ripe berry bushes (`items.type === 'berry'`), weeping birch sap, or mushroom caps.
  - When a worker finds a berry bush, it lands on the fruit for 6–10 seconds, wings folded, feeding. It then takes off, flying a direct vector back to the nest.
- **Pheromone Alarm Pulse**:
  - If a foraging wasp is attacked or if the player approaches within 4.5 m of the central nest, the sentinel raises its abdomen, vibrates its wings with a high-pitched whine (120 Hz tone via Web Audio), and emits an invisible alarm pheromone pulse (radius 10 m).
  - All foraging workers within the radius break off their peaceful tasks and enter defensive swarm mode, rallying to defend the nest with coordinated hit-and-run stings.

#### Inter-Mob Interactions
- **Cat Deterrence**: If the wandering cat approaches within 3.5 m of a wasp nest, sentinels target the cat's exposed wet nose and ears. The cat lets out a sharp yowl (`SFX.catMew` at high pitch), leaps straight into the air, and flees at full sprint, shaking its head.
- **Detritus Competition**: Wasps and beetles frequently dispute fallen berries. A wasp will hover 5 cm above a beetle, buzzing aggressively and darting down to headbutt the beetle until the beetle turns around.
- **Weather Grounding**: Raindrops are catastrophic to an insect weighing 80 milligrams. At `WEATHER.wet > 0.35`, all foragers abandon their routes and cluster inside the protected undersides of the nest paper comb. In a downpour or storm, wasp nests are 100% docile, opening safe pathways through normally hazardous birch groves.

---

### 3.5 Beetles (*Geotrupes forestis*) — Undergrowth Navigators & Detritivores

Currently 9 harmless beetles (`matBeetle`) wandering and fleeing from the tortoise within 1.6 m.

#### Natural History & Behaviors
Beetles are the foundational detritivores of the Hollow:
- `foraging & feeding`: Actively seek out decomposing organic matter: fallen pine needles, leaf piles, and specifically glowing mushroom clusters (`items.type === 'shroom'`). When a beetle reaches a mushroom, it stops for 15–30 seconds, head tucked down, nibbling spores.
- `ball rolling`: Dung and fungal spore ball rolling mechanics:
  - Certain beetles in the birch and fen biomes roll a spherical detritus ball (radius 0.08 m) backwards using their hind legs.
  - If the ball encounters an obstacle or steep slope ($> 15^\circ$), the beetle struggles, slips, and occasionally loses control of the ball, watching it roll down into a hollow before scurrying after it.
- `thanatosis (playing dead)`:
  - If a large entity (tortoise, cat, or human camera) looms suddenly overhead or steps directly over the beetle, it tucks all 6 legs flat against its thorax, drops to the dirt, and ceases all movement for 4–8 seconds.
  - Predators (specifically the cat and heron) lose interest in motionless prey, allowing the beetle to survive.
- `burrowing`:
  - When pursued into a dead end, a beetle can rapidly excavate the soft loam or fen mud, kicking up micro-particle dirt puffs and sinking below the terrain mesh (`m.y -= dt * 0.08`), remaining buried until danger clears.
- `ledge tumbling`: Clumsy biomechanical walkers: when stepping off a stone step or waterway bank, the beetle loses footing, tumbles end-over-end down the incline with physics angular velocity, lands upside-down, waves its legs frantically for 2 seconds, and rocks itself back onto its feet.

---

### 3.6 Pond Skaters (*Gerris lacustris*) — Surface Tension Darts

Currently 26 skaters (`matSkater`, leg span 0.16 m) executing independent shove-and-glide routines across the waterway.

#### Schooling and Collective Dynamics
Real water striders form organized flotillas rather than chaotic random gas molecules:
- **Flotilla Flocking (Boids on Water)**:
  - Skaters cluster into loose schools of 5–10 individuals near calm shallows, the lee of water lily pads, and creek inlets where water current is minimal.
  - Three simple planar steering rules:
    1. *Cohesion*: Gentle glide toward the average position of nearby skaters within 3.0 m.
    2. *Separation*: Sharp shove away if another skater comes within 0.45 m (preventing leg collisions).
    3. *Alignment*: Synchronized orientation during flight bursts.
- **Surface Ripple Perception (Capillary Wave Sensing)**:
  - Skaters are blind to objects above them but extraordinarily sensitive to surface waves.
  - Any disturbance in the water—the tortoise wading into shallows, a falling leaf striking the surface, a heron beak thrust, or raindrops—creates a propagating circular ripple wave.
  - Skaters within 4.0 m of the ripple source detect the wave front, immediately orient $180^\circ$ away, and execute two rapid emergency thrust kicks (`v = 2.4 m/s`), scattering in radiating starburst patterns.
- **Raft Wake Reaction**:
  - As the player rides the giant floating leaf raft across the lake (`P.raft`), the raft pushes a physical displacement wave. Skaters do not phase through the raft; they are swept outward by the bow wave, skimming cleanly along the leaf's perimeter.
- **Raindrops & Surface Rupture**:
  - Light mist (`wet < 0.3`): Skaters become hyperactive, feeding on drowned micro-insects caught in the surface tension.
  - Heavy rain & thunderstorms (`wet > 0.7`): Raindrop impacts smash the delicate water meniscus. Skaters cannot skate on churning water. They sprint frantically toward emergent reeds, bank grasses, and water lily rims, climbing 2 cm up plant stems above the waterline to wait out the deluge.

---

### 3.7 Crows (*Corvus corax*) — The Inquisitive Sentinels

Currently 2 airborne crows patrolling random open cells at 4.8 m altitude, diving to peck the player for 17 damage.

#### Corvids as High-Intelligence Entities
Crows are the most intelligent animals in the forest. Treating them purely as kamikaze dive-bombers wastes their ecological potential:
- **Perching and Aerial Scouting**:
  - Crows spend 60% of their time perched on high lookout posts: dead tree snags, mossy stone monoliths, or the top of the hedge maze crowns (altitude 4.5–6.0 m).
  - While perched, the crow tilts its head in jerky, inquisitive saccades (monocular inspection), preens its wing primaries, and surveys the ground corridors below.
- **Food Caching & Kleptoparasitism**:
  - Crows actively seek unguarded berry bushes (`items.type === 'berry'`).
  - A crow will swoop down from its perch, pluck a berry in its beak, fly to a secluded corner of the maze, cache the berry beneath a patch of dead leaves, and tap a small pebble over it.
  - If the player approaches a crow's secret cache, the crow becomes visibly distressed, circling overhead and cawing loudly (`SFX.caw()`).
- **Cooperative Predator Mobbing**:
  - Crows hate the cat and the heron.
  - When the cat enters `stalk` or `pounce` mode anywhere on the map, a perched crow that spots it will take flight, emitting a harsh, rattling assembly call.
  - The two crows will swoop low in tandem over the cat, snapping their beaks inches above the cat's ears and diving alternately. This harassment distracts the cat, shortening its stalk duration and alerting the player to the predator's presence long before it arrives.
- **Interaction with the Sheltered Tortoise**:
  - If the player pulls into the shell, the crow does not mindlessly fly away after 2.2 seconds.
  - It lands on the ground 1 metre away, cocking its head sideways. It hops closer with distinct avian double-hops, taps the carapace with its beak to test if it is edible, hops onto the top of the shell dome, perches there for a moment looking around, and only flies off when the tortoise begins to emerge.

---

### 3.8 Large Fish (*Silurus lacustris*) — The Deep Water Leviathan

The missing lake dweller (fulfilling the prompt's explicit requirement and completing the waterway ecosystem).

```
         CRUISING (deep lake basin)
                    │
           (ripple detected on surface)
                    ▼
         SURFACING / INVESTIGATING
          │                   │
  (skater / berry)       (leaf raft)
          │                   │
          ▼                   ▼
    SNAP & BREACH       SHADOW ESCORT
```

#### Anatomy and Visual Rig
- Built using Three.js primitive hierarchy: a sleek, hydrodynamic carp/catfish silhouette (`matFish`: deep slate-olive back, iridescent pale yellow belly, shimmering metallic roughness 0.25).
- Segmented spine with 3 articulated joint groups driving an undulating sine-wave swim cycle (`tailYaw = Math.sin(t * 4.2) * 0.35`).
- Translucent pectoral and dorsal fins.

#### Behaviors and Water Mechanics
- **Deep Channel Cruising**:
  - Lives in the deep central basin of the lake (`WAY.r = 12.5m, WAY.depth = 0.50m`).
  - Cruises the lake bed along gentle bezier spline paths at 0.8 m/s, staying near bottom weeds and submerged sunken logs.
- **Surfacing for Food (The Breach)**:
  - The fish watches the underside of the water surface.
  - When a pond skater lingers stationary for $> 3.0$ seconds, or when a ripe berry rolls off a bush into the water, the fish banks upward.
  - It accelerates vertically: a dark, massive silhouette looms beneath the water, followed by a dramatic surface breach—jaws break the surface with a loud watery gulp (`SFX.fishGulp`), sucking the skater or berry under, creating a wide circular wave splash, and flicking its caudal fin before diving back to the abyss.
- **Interactions with the Leaf Raft**:
  - When the tortoise sails across the lake on the leaf raft (`RAFTS[0]`), the fish does not attack the raft (preserving gameplay flow), but acts as an awe-inspiring companion.
  - It glides directly beneath the raft, its elongated silhouette clearly visible through the semi-translucent green leaf deck.
  - If the player drops a collected berry into the water from the raft, the fish surges upward to take the treat, rewarding observational play.
- **Heron vs Fish Conflict**:
  - The Heron's primary aquatic target is the Large Fish.
  - When the fish surfaces in the shallows ($< 0.25\text{ m}$ depth), a perched Heron will launch an ambush dive. If the strike connects, the Heron drags the thrashing fish to the shoreline in a dramatic predator-prey struggle.

---

## 4. The Inter-Mob Interaction Matrix

To make the forest feel truly alive, entities must react systematically to one another. The matrix below defines the complete multi-species behavioral response grid:

| Actor $\downarrow$ / Target $\rightarrow$ | **Thornmaw** | **Heron** | **Cat** | **Wasps** | **Beetles** | **Skaters** | **Crows** | **Large Fish** | **Tortoise (Player)** |
|---|---|---|---|---|---|---|---|---|---|
| **Thornmaw** | Neutral (ignores) | Neutral (too high) | Neutral (avoids roots) | Neutral | **Snaps & swallows**; enters digestion | Neutral (aquatic) | Neutral | Neutral (aquatic) | Strikes walking/sprinting; ignores shell |
| **Heron** | Avoids bramble thickets | Territorial rivalry | Eye-contact standoff; fluffs ruff | Avoids nest areas | Pecks & eats if in shallows | **Spear-fishes** from bank | Chased & mobbed by crows | **Dives & spears** in shallows | Kills if exposed; clatters off shell |
| **Cat** | Avoids reach (sensed) | Stalks if perched low | Territorial posture | **Stung & flees** scratching nose | **Stalks, pounces, bats playfully** | Watches at shoreline; pats at water | Stalks on ground; irritated by aerial mobbing | Watches fins from shore | Stalks, pounces, flips onto back |
| **Wasps** | Neutral | Neutral | **Stings & repels** from nest | Hive unity / swarm | Competes for fallen berries | Neutral (aquatic) | Stings if crow nears nest | Neutral (aquatic) | Stings if near nest; ignores shell |
| **Beetles** | **Avoids vibrations**; preyed upon | Freezes / thanatosis | **Flees / thanatosis**; burrow | Competes for fruit | Social clustering / passing | Neutral (aquatic) | Flees; burrow into mulch | Neutral (aquatic) | Spooked if trodden on; otherwise ignores |
| **Skaters** | Neutral | **Scatters from beak splash** | Scatters from paws at bank | Neutral | Neutral | **Loose schooling / mating darts** | Scatters from swoops | **Preyed upon by breach** | Bow-wave scatter around leaf raft |
| **Crows** | Neutral | **Cooperative aerial mobbing** | **Harasses & dive-bombs** | Robs sweet sap; avoids sting | Drops down to snatch & eat | Pecks if near shoreline | Flocking pair / mutual alarms | Watches breach curiously | Dives for 17 dmg; inquisitive hop if sheltered |
| **Large Fish** | Neutral | **Flees shadow into deep basin** | Splashes water; dives deep | Neutral | Eats if knocked into water | **Surfaces & swallows** | Neutral | Solitary apex aquatic | **Escorts leaf raft**; swallows dropped berries |
| **Tortoise** | Traverses sleeping; shells | Shells against stab; walks | Shells against toss; rocks off | Walks away from leash | Can herd toward thornmaw | Observes from leaf raft | Shells against dive; observes hops | Rides raft over fish; feeds berries |

---

## 5. Ecosystem Dynamics & Internal Biological Clocks

### The Four Homeostatic Drives
Instead of static finite state machines triggered only by player proximity, every active animal simulates four normalized homeostatic drives ($[0.0, 1.0]$):

$$\mathbf{D} = \begin{bmatrix} \text{Hunger} \\ \text{Fatigue} \\ \text{Alertness} \\ \text{Curiosity} \end{bmatrix}$$

```
                ┌──────────────────────────────────────┐
                │        HOMEOSTATIC DRIVES            │
                │ Hunger   Fatigue  Alertness Curiosity│
                └──────────────────┬───────────────────┘
                                   │
                                   ▼
                ┌──────────────────────────────────────┐
                │          UTILITY EVALUATOR           │
                │  Ranks behaviors: Hunt, Rest, Flee,  │
                │        Groom, Forage, Play           │
                └──────────────────┬───────────────────┘
                                   │
                                   ▼
                ┌──────────────────────────────────────┐
                │          BEHAVIOR ARBITER            │
                │      Executes highest-rank goal      │
                └──────────────────────────────────────┘
```

1. **Hunger ($H$):**
   $$\frac{dH}{dt} = +\lambda_{\text{metabolism}}$$
   - Increases steadily over time.
   - When $H > 0.65$, priority shifts from resting or playing to active foraging/hunting.
   - Satisfied when feeding on corresponding food web targets (berries, beetles, fish).
2. **Fatigue ($F$):**
   $$\frac{dF}{dt} = +\lambda_{\text{exertion}} \cdot (\text{speed}) - \lambda_{\text{rest}} \cdot (\text{resting})$$
   - Accumulated through sprinting, pouncing, flying, and swimming.
   - When $F > 0.80$, the mob seeks out a safe sanctuary (perch, dry rock, burrow) to enter a restorative sleep/rest state.
3. **Alertness / Fear ($A$):**
   - Spikes instantaneously upon sudden environmental stimuli: thunderclap, predator screech, sprint footsteps, falling tree branches.
   - Drives flight, freezing (thanatosis), or defensive sheltering. Decays exponentially in quiet environments ($\tau = 4.5\text{ s}$).
4. **Curiosity ($C$):**
   - Unique to intelligent species (Cat, Crow). Rises when novel, non-threatening stimuli are detected in line-of-sight (e.g. the tortoise entering a new clearing, a rolling leaf, a shiny Sunstone). Drives investigative stalking.

### Off-Screen Coarse Simulation (LOD AI)
To eliminate the "frozen in amber" bug without incurring CPU overhead:
- When a mob is outside `activeRange`, it does **not** stop existing.
- Instead of running full 60 FPS physics, raycasts, and mesh updates, the runtime advances its internal state vector $\mathbf{D}$ using a **coarse tick** once every 3.0 seconds ($0.33\text{ Hz}$):
  $$\mathbf{D}_{t+\Delta T} = \mathbf{D}_t + \mathbf{\dot{D}} \cdot \Delta T$$
- When the player eventually walks within `activeRange`, the mob does not wake up at default frame zero. A cat whose fatigue reached threshold 20 seconds ago will be discovered sleeping curled up on a stone; a heron whose hunger peaked will already be standing at the lake bank mid-hunt. The world was alive while the player was away.

---

## 6. Weather & Biome Systematic Coupling

The Hollow's atmospheric engine operates across four primary weather spells:

$$\text{Clear} \; (\text{wet} = 0) \longrightarrow \text{Misting} \; (\text{wet} = 0.3) \longrightarrow \text{Downpour} \; (\text{wet} = 0.75) \longrightarrow \text{Thunderstorm} \; (\text{wet} = 1.0, \text{storm} = \text{true})$$

### The Cross-Species Weather Response

| Weather State | Insects (Wasps, Skaters, Beetles) | Corvids & Herons (Crows, Heron) | Mammals (The Cat) | Flora & Aquatic (Thornmaw, Large Fish) |
|---|---|---|---|---|
| **Clear / Sun** | Full foraging flights; skaters clustered in open lake; beetles ambling | High perching; wide patrol flights; active corvid caching | Sunbathing on dry flat rocks; relaxed territory marking; grooming | Maws active and responsive; fish cruising deep cool channels |
| **Misting / Overcast** (`wet = 0.30`) | Beetles flourish in damp mulch; wasps seek sap; skaters hyperactive | Herons wade into lake shallows; crows forage on ground | High hunting drive; beetles actively stalked in moist grass | Maws primed by moist air; fish surface frequently for drowned bugs |
| **Heavy Rain** (`wet = 0.75`) | Wasps retreat inside nest comb; skaters seek reed shelter; beetles burrow | Flights grounded; crows huddle on sheltered branches; heron perches | Despises wet ground; shakes paws; gallops toward tree hollows | Pitchers flooded; shoots become sluggish; fish active near surface |
| **Thunderstorm** (`wet = 1.0`, `storm = true`) | **100% activity cessation**: wasps sealed in nests; skaters clinging to reeds | **Extreme terror**: crows scatter screeching; herons tuck into deepest brush | **Panic retreat**: sprints at 4.5 m/s to Gloom Grove; zero hunting | **Seismic shock**: maws coil tight sepals; fish dive to deepest silt |

### Biome Ecosystem Affinities
Coupled directly to `BIOMES` (`hollow`, `fen`, `bramble`, `birch`) and `GLOOM`:

```
  ┌─────────────────────────────────────────────────────────────┐
  │                        THE HOLLOW                           │
  │                                                             │
  │     [ BIRCH ]                     [ FEN ]                   │
  │  Wasp nest colonies            Beetle paradise              │
  │  Crow lookout perches          Mud burrowing                │
  │  Cat territory rub-trees       Soft footsteps (damped)      │
  │                                                             │
  │                     [ CENTRAL LAKE ]                        │
  │                  Heron fishing shallows                     │
  │                  Pond skater flotillas                      │
  │                  Large fish deep channel                    │
  │                                                             │
  │     [ BRAMBLE ]               [ GLOOM GROVE ]               │
  │  Thornmaw thickets             Perpetual twilight           │
  │  Dense briar refuges           Cat rain shelter             │
  │  Low visibility                Bioluminescent digestion     │
  │                                No shadow threats            │
  └─────────────────────────────────────────────────────────────┘
```

- **Birch Biome**: High light, tall pale trunks. Home to wasp paper nests suspended from high branches and crow lookout perches. High visibility makes ground movement easily spotted.
- **Fen Biome**: Saturated, muddy terrain with standing pools. The kingdom of beetles and detritivores. Mud damps footstep acoustics, allowing the tortoise to sneak much closer to predators.
- **Bramble Biome**: Dense, thorny corridors with high Thornmaw concentration (`MOB_GROUND.thornmaw.bramble = 3.0`). Provides tight crevices where small beetles can evade cats and crows.
- **Gloom Grove Overlay**: Canopy blocks light, preventing shadow telegraphs (`shadowReadable = false`). Serves as a sanctuary from aerial predators (Heron, Crows) and the primary rain shelter for the Cat, while harbouring dense clusters of bioluminescent Thornmaws on the ground.
- **The Central Lake Basin**: The aquatic hub where Heron, Large Fish, and Pond Skaters interact continuously.

---

## 7. Practical Implementation Architecture

To implement this living ecosystem within `tortoise.html` without degrading performance, the architecture must fit cleanly into the existing engine loop.

```
                             updateMobs(dt)
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
      SPATIAL GRID QUERY                       ENTITY UTILITY TICK
   Flat 2D cell hash grid                    Zero-allocation evaluation
 (replaces O(N²) mob loops)                (reads drives, chooses state)
              │                                         │
              └────────────────────┬────────────────────┘
                                   │
                                   ▼
                         ANIMATION & RIG POSE
                      Direct joint transformation
                        (60 FPS Three.js mesh)
```

### 1. Zero-Allocation Spatial Hash Grid
Currently, checking whether any mob is near another would require nested $O(N^2)$ loops. With 60+ total entities across the board, allocating arrays each frame would trigger frequent Garbage Collection stutter.

Instead, a flat typed spatial hash grid is used:
- The clearing ($92 \times 92\text{ m}$) is divided into a $23 \times 23$ grid of $4.0\text{ m}$ buckets.
- Implemented as three flat `Int16Array` structures:
  ```javascript
  const GRID_SIZE = 23;
  const CELL_SIZE = 4.0;
  const gridHead = new Int16Array(GRID_SIZE * GRID_SIZE).fill(-1);
  const gridNext = new Int16Array(MAX_MOBS).fill(-1);
  ```
- Rebuilt in $< 0.15\text{ ms}$ at the start of `updateMobs(dt)`.
- Querying all neighbors within radius $R$ of an entity requires checking only $3 \times 3$ adjacent grid buckets, reading indices directly into a preallocated scratch array `_nearMobIndices`. Zero heap allocations per frame.

### 2. Preallocated Entity Memory Layout
Each mob's data block (`m.data`) avoids dynamically created sub-objects. Drives and scratch variables are flat numeric properties:

```javascript
// Preallocated inside spawnMob(name, x, z)
m.data.hunger = 0.2;
m.data.fatigue = 0.0;
m.data.alertness = 0.0;
m.data.curiosity = 0.5;
m.data.targetMob = null;    // pointer to another mob instance
m.data.targetDist = 999.0;
m.data.coarseTimer = Math.random() * 3.0;
```

### 3. Utility AI Evaluation Function
Instead of brittle, nested `if-else` trees, each mob executes a lightweight Utility Evaluator every $0.25\text{ s}$ (staggered across frames using `(m.id + frameCount) % 15 === 0`):

$$\text{Score}(\text{Action}) = W_{\text{action}} \cdot \prod_{i} \text{UtilityCurve}_i(\text{Input}_i)$$

For example, for the Cat deciding between `StalkBeetle`, `Groom`, and `Sunbathe`:
- `Score(StalkBeetle) = W_hunt * Curve(Hunger) * (NearestBeetleDist < 6.0 ? 1.0 : 0.0) * (WEATHER.wet < 0.3 ? 1.0 : 0.0)`
- `Score(Sunbathe) = W_rest * Curve(Fatigue) * (InSunlight ? 1.0 : 0.0) * (WEATHER.wet == 0 ? 1.0 : 0.0)`
- `Score(ShelterRain) = W_fear * (WEATHER.wet > 0.6 ? 2.5 : 0.0)`

The highest scoring action wins and sets `m.state`. The tick loop merely animates towards the active state's goal.

### 4. Integration with the Set-Piece Arbiter (`STAGE`)
The existing set-piece arbiter (`STAGE`, lines 5356–5378) serializes the Heron, Cat, and falling glass so they never overlap on the player.

Under the living ecosystem model, `STAGE` is preserved:
- When the Cat or Heron wins the `STAGE` token to perform a set-piece against the player, it seamlessly transitions from its autonomous routine (e.g. cat prowling or heron perched) into its dramatic player-focused choreography.
- Furthermore, when a set piece begins, nearby smaller mobs react organically: a Heron diving towards the clearing causes nearby beetles to instantly drop into thanatosis and pond skaters to scatter. The set piece becomes an environmental crescendo rather than an isolated script.

---

## 8. Empirical Verification & In-Game Testability

In accordance with the project principle *"The game is the gate. A change that only compiles is not done. You have to test them in game."*:

### Verification Protocol for Future Implementation
1. **Automated Headless CDP Suite**:
   - Run via headless Chrome with Chrome DevTools Protocol (CDP) through `test_harness.py`.
   - Automated tests will verify:
     - **Spatial Hash Integrity**: Ensure 100% of mob positions correctly map into grid buckets without leaks or array overruns.
     - **Zero Allocation in Loop**: Measure JavaScript heap delta across a 1,000-frame automated play session (`performance.memory.usedJSHeapSize`). Heap delta must remain flat, proving zero GC churn.
     - **Inter-Mob Event Counters**: Automated verification that over a 5-minute simulated run, counts of inter-mob events are non-zero:
       - `events.thornmaw_ate_beetle >= 1`
       - `events.cat_stalked_beetle >= 2`
       - `events.crow_mobbed_predator >= 1`
       - `events.fish_surfaced_skater >= 2`
       - `events.wasps_grounded_in_storm == true`
2. **Health Check Regression Guard**:
   - The full baseline health check suite (`test_game_health.py`) must pass cleanly with zero errors:
     - Player forward walk distance $> 0.5\text{ m}$.
     - 4 item pickups (2 berries, 2 shrooms) collected cleanly.
     - Shell hide (`hideAmt > 0.5`) and emerge (`hideAmt < 0.05`).
     - Leaf raft boarding on waterway.
     - Sunstone collection, gate opening, and win transition.
     - Clean game reset via `KeyR`.

---

## 9. Summary: The Hollow as an Unbroken World

By giving each mob an autonomous life, physiological drives, and cross-species interactions, the Hollow transforms from a maze with mechanical hazards into a breathing European forest understory.

When the tortoise pushes through a briar hedge into a birch clearing, it does not simply trigger another hazard countdown. It stumbles upon a world in progress: two crows screeching from a high snag as a cat stalks a beetle through damp moss; pond skaters dancing across lake ripples while a great pike cruises the deep water below; and a Thornmaw sleeping off its feast in the warm afternoon light. The tortoise is no longer the sole center of the universe—it is a small, hard-shelled creature navigating an ancient, living world.
