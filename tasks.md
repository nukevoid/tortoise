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
- [X] remove timer for the shell
- [X] do step sound faster and lighter
- [X] fix anemy plant mode  - it don't hase stem from root to flower
- [X] don't make that diagonal free cells not connected (visualy I can see next diagonal cell, but can't go to it now)
- [X] more lighter and faster steps, it is tortoise, not Cow
- [X] add reflection to water (cubemap like minimum)
- [X] add button to switch view from first to third person
- [X] ground under water has to look wet - darker with weetness
- [X] bug: in left top sector related to lake lake water is higher than banks and terain
- [X] sound of wind has to depend on wind power. And make wins lighter by defaul, and stronger time to time
- [X] bug: some ponds looks like without water, maybe camera beneth the water plane 
- [X] fix camera in 3rd mode ( has to look from the top bottom to forward), investigate how cameras in 3d view works
- [X] remove strafes, assign to A and D YAW rotation
- [X] fix legs and head animation and model of tortoise (looks bed in 3rd view mode)
- [X] bug - on lake's leaf  player movement has jitter 
- [X] do more time of calm wind 
- [X] add rain drops on water when it rains
- [ ] in V mode when hides in SHell: additional shel apiars around the body - fix it
- [ ] in V mode uppar part of the legs visible thought shell
- [ ] in swing flipped animation rotation has to be oposite to movement
- [ ] add smooth water - bank intersection
- [ ] add small rocks and debris that shows only in small range 
- [ ] sunbeam visibility has to depend on weather 
- [ ] on leaf change sound from steps to water splahes
- [ ] when pick mashrom - game freeze for 1-2 second
