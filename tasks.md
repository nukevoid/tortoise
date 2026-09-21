# Tasks

## How a task here is done

One at a time, in order. Re-read this file after each one -- it changes while work
is in progress. Finish a task, prove it on the board, commit it, then start the
next; nothing is left half-done across a commit.

One commit per task, Conventional Commits, subject <= 72 chars. Say in the message
what was verified and how, and say plainly what was not. Never push, branch or
restructure without being asked.


## How it is checked

The game is the gate. A change that only compiles is not done. You have to test them in game

**Before committing** -- remove every temporary test hook and re-flash without it;
put back any device setting the test changed; do not commit build artifacts
or anyone else's uncommitted work.
mark done tasks like - [X] 
 - git commit explicit paths, never -a. 
 - Health-check between iterations. 

## Tasks

-
- [X] rain sound
- [X] stamina has to have histeresis. Now it shakes at the end 
- [X] do level desing around POI and coridors between them 
- [X] Bushes are agly, and I almost don't see busshed with branches witch is perfect. This one witch block woles- has stretched tectures and super lowpoly. Fix
- [X] water has to block ablility to hide in shelter
- [X] do body of tortoise smaller
- [X] fix rolling animation - it has to roll like wheel from side to side
- [X] assigne some enemies to some bioiemes. Heron can't be in foggy biom becouse we don't se shadow
- [X] Add sound of steps, for water and ground different
- [X] Make texture on sphere bushes more detailed
- [X] Move enemy Plant with spikes to dark fogy biom and increase quantity 
- [X] Add lake with ability wo sweem on big leaf. Lets cenral lake connects 4 sides of our map
- [X] change sky color slowwly when it rains
- [X] Do research for performance optimisation
- [X] implement performance optimisation 
- [X] fix lake - now it is super deeep tranche without water, not big shalow lake 
- [X] fix leaf - now I can speen on it under the ground
- [X] fix spherical bushes material - it is to reglective (has to be more difuse)
- [X] use wind power for amplitude of animation of grass, reas, leaft, rain etc. Change wind power with weather
- [X] fix: cat can drown in lake. Just don't 
- [X] lake - separate biom with own flora and fauna
- [X] lake has to be in center of map. Dont extend it to borders. Separate each part of map using regular wals and connect them at center at lake
- [X] sky can't be blue at the top what it's heavyrain
- [X] fix masshroms heads - thay inverted
- [ ] remove timer for the shell
- [ ] do step sound faster and lighter
- [ ] fix anemy plant mode  - it don't hase stem from root to flower
- [ ] don't make that diagonal free cells not connected (visualy I can see next diagonal cell, but can't go to it now)