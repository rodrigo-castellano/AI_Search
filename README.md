# Adversarial Search — the KTH Fishing Derby

Minimax with alpha–beta pruning, iterative deepening and move ordering, playing
a two-player fishing game under a hard 60 ms move deadline.

Assignment 1 of **DD2380 Artificial Intelligence**, KTH, autumn 2021.

📄 [Assignment brief](docs/Assignment_Search_HT2021_P1%20(1).pdf) ·
[lecture on search](docs/AI%20-%20search.pdf) ·
[lecture on adversarial search](docs/AI%20-%20Adversarial%20Search%20(1).pdf)

## The game

Two boats on opposite sides of a wrapping sea, each lowering a hook to catch
fish. Fish carry different scores, some negative. Both players move
simultaneously and the board wraps horizontally, so the distance between a hook
and a fish has to be measured the short way round.

The score is the difference between the two players' catches — a zero-sum game,
which is what makes minimax the right tool.

## What is implemented

All of it in [`player.py`](player.py); the rest is the course's game engine.

**Iterative deepening** ([`search_best_next_move`](player.py)) searches to depth
1, 3, 5, … 19, keeping the best move found so far and stopping the moment the
elapsed time passes 55 ms. The deadline is 60 ms, so this leaves a margin for
the move to be sent. A partial search that returns in time beats a perfect one
that gets disqualified.

**Alpha–beta pruning** ([`alphabeta_iter`](player.py)) with the time check
repeated at every node, so a search already over budget unwinds immediately
rather than finishing the subtree.

**Move ordering** via `best_positions_dict`, which remembers the best move found
for each state key at the previous depth and tries it first. Alpha–beta prunes
far more when the best move is examined first, so this is what makes the deeper
iterations affordable.

**The heuristic** ([`heuristic`](player.py)) is the interesting part:

$$h = (\text{my score} - \text{their score}) + 0.01 \sum_{f} \frac{\text{value}(f)}{\text{distance}(f) + 0.01}$$

The first term is the actual objective. The second is a tie-breaker: with the
score level, prefer positions close to valuable fish. Distance is computed
across the horizontal wrap, taking the minimum of the direct and both wrapped
paths.

There is one deliberate trap in it. If the hook has already caught a fish but a
noticeably better one (worth more than 5 extra) sits within 3 squares, the
position scores −100000. Holding a cheap fish blocks the hook from taking the
expensive one, so the search is pushed hard away from that state.

## Running

```bash
pip install -r requirements.txt      # requirements_win.txt on Windows
python main.py                        # or: python main.py -p settings.yml
```

`settings.yml` sets the fish layout and the opponent. `opponent.py` is the
course-supplied adversary, shipped obfuscated — `pytransform/` is its runtime
and is needed to run against it.

`requirements.txt` pins `numpy==1.22` and `PyYAML==5.4` rather than the versions
the course shipped, which had published CVEs.
