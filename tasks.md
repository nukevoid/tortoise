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
- [ ] Make bushed more realistic 
- [ ] Do color corection to more calm and realistic
- [ ] Add nice sunlight and gust on air
