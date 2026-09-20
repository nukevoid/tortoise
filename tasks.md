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
- [ ] Fix Heron - after shadow now just screen about gameover: add Heron head and neck with animation 
- [ ] Add cat, hides in bushes. It no hostile, but can play with you and tos you, then disapeear
- [ ] Add mechani then you can be fliped (you see then shell otside), and you have to swing by left\right keys to stay normal. Can can flip you during tha play
- [ ] Level has to be saved. Generate level offline
- [ ] investiagate level disign aproaches and generators, implement and test
- [ ] Add different bioms, use them in level generation
- [ ] Add landscape 
- [ ] Add weather
- [ ] Balanse gameplay 
- [ ] Change had indication: heath - hearts, stamina - leafs. Change all code than use it