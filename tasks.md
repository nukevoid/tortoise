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

- [X] Make obstacles (bushes, trees) smooth with many polygons
- [X] Fix problem when player can move formad becose upper body is toching something, but direct view is cler
- [X] Bushes and trees still polygonal, fix them
- [X] Fix "in the shell" view
- [X] Fix terrain texture resolution 
- [X] Add water, creeks, pudles, lake
- [X] make falling leaf animation realistinc (rotation, dwings etc) 
- [X] Crteate optimisation plan
- [X] Do optimisation
- [X] Make bushed more realistic 
- [X] Do color corection to more calm and realistic
- [X] Add nice sunlight and gust on air
- [X] Dafault speed has to be slower
- [X] Rework bushes (main obstacles), make 3 different wariants, use some new tecnhnics to generate them to be more realistic
- [X] Add adrchitecture to add mobs wtich can interact with player
- [X] First mob: hostile plant with 3 thorny shoots. Its bit you in some range with some delays, but you can hide in shell. Visualy has to have animations in sync with bites
- [X] Heron - Can eats you from above. Firstly you see only shadown of Heron, then you have 2-3 sec to hide in shell. Then you see Heand with long head of Heron, triying to eat you. IF you no in shell - you loose 
- [X] hostile plant - add longer delays between bites
- [X] Falling glass cup: like heron - shadow, then cup falling cirectly on you. You can move 5 sec untill in breakes, couse you are under the cup
- [X] in some glasses with spider  inside, and you have to hide or they weel bite you
- [X] improve spider model
- [X] Fix Heron - after shadow now just screen about gameover: add Heron head and neck with animation 
- [X] Add cat, hides in bushes. It no hostile, but can play with you and tos you, then disapeear
- [X] Add mechani then you can be fliped (you see then shell otside), and you have to swing by left\right keys to stay normal. Can can flip you during tha play
- [X] Level has to be saved. Generate level offline
- [X] investiagate level disign aproaches and generators, implement and test
- [X] Add different bioms, use them in level generation
- [X] Add landscape 
- [X] make minimap map aliitle larger
- [X] fix direction of marker on mini map
- [X] Add weather
- [X] fliped mechanic to hard at the end. Start is easy but final flip is always missing
- [X] Balanse gameplay 
- [X] Change had indication: heath - hearts, stamina - leafs. Change all code than use it
- [X] Add more mobs variation 
- [X] Do mobs that in same time wont be Heron and Glass, or other 
- [X] increase quality of water, place more water regions
- [X] In many places wisualy looks like we can go but we cant, and in map we see obstackle 
- [X] do research how to play mobs and realm and other items usig Game Designt technicas and keep player attention + give plaer emotional swing
- [X] implement results of Game Desing research
- [X] In some places water edge is under the ground
- [X] In fliped state mouse rotate the shell but don't have to
- [X] return bushes before fixing the "In many places wisualy looks like we can go but we cant, and in map we see obstackle " . Now thay look boring green solid wall. Just put in wholes some new type of semi filled bushes
- [X] Add timeout how long we can be in shell with indicator and restore time
- [X] cat\ Heron just came one by one, no time to  flip over. And this is first encounter. Introduse enemies slowly, one by one with increasing of dificulty
- [X] Fix Heron model 
- [X] do flip swing offline simulation and improve algorithm so user can easely find rhythm and ryhtm has to be same
- [X] improve swing animation - now it rotates at the center of mass but has to roll on the ground
- [X] slow down tortoise
- [X] in fog ski is just blue
- [X] change wind with weather and wind sound
- [X] rain sound
- [X] stamina has to have histeresis. Now it shakes at the end 
- [X] do level desing around POI and coridors between them 
- [X] Bushes are agly, and I almost don't see busshed with branches witch is perfect. This one witch block woles- has stretched tectures and super lowpoly. Fix
- [X] water has to block ablility to hide in shelter
- [X] do body of tortoise smaller
- [X] fix rolling animation - it has to roll like wheel from side to side
- [X] assigne some enemies to some bioiemes. Heron can't be in foggy biom becouse we don't se shadow
- [ ] Add sound of steps, for water and ground different
