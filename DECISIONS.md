# Architectural Decisions

This file documents key technical decisions and explanations made throughout the project.

---

## What is a Kalman Filter?
*Author: David Gleason*

A Kalman filter is a  mathematical algorithm that estimates the position and velocity of a moving object when direct measurements are noisy or incomplete. It works in two steps: first it predicts where the object will be next based on its current state and a motion model, then it corrects that prediction when a new measurement arrives by blending the prediction and the measurement according to how much it trusts each one. The more uncertain the prediction, the more weight it gives the new measurement, and vice versa. In the context of vehicle tracking, the Kalman filter allows DeepSORT to maintain a smooth estimated trajectory for each vehicle even when the detector misses it for a few frames keeping the same vehicle ID alive rather than losing track and starting over.
---

## Git Workflow — How We Collaborate Without Conflicts
*Author: David Gleason*

Each teammate works on their own branch and merges into `main` via Pull Requests.

**Branches:**
- `main` — stable, always runnable
- `david/tracking` — David's branch (DeepSORT, OpenCV overlay, pipeline)
- `dylan/ml` — Dylan's branch (frame extraction, labeling exports, training notebooks)
- `nick/systems` — Nick's branch (SRT parser, speed estimator, zone logic)

---

### At the Start of Every Work Session

```bash
git checkout <your-branch>       # e.g. git checkout david/tracking
git fetch origin
git merge origin/main            # pull in any changes teammates merged since last time
```

If there are conflicts, resolve them before doing any new work.

---

### While You're Working

Commit often with clear messages:
```bash
git add <specific files>
git commit -m "short description of what you did"
```

Never use `git add .` blindly — check what you're staging first with `git status`.

---

### When You're Ready to Share Your Work

```bash
git fetch origin
git merge origin/main            # sync with main one more time
# resolve any conflicts
git push origin <your-branch>
```

Then open a Pull Request on GitHub from your branch into `main`. Tag a teammate to review — a quick sanity check, not a deep review.

---

### What a Pull Request Looks Like on GitHub

1. Push your branch:
   ```bash
   git push origin david/tracking
   ```

2. Go to the repo on GitHub — you'll see a yellow banner:
   > "david/tracking had recent pushes — **Compare & pull request**"
   
   Click it.

3. You'll see a form:
   - **Title** — short description of what you did (e.g. "Add DeepSORT tracker class")
   - **Base:** `main` ← **Compare:** `david/tracking` (this should already be set)
   - Scroll down to see a diff of every file you changed

4. Click **"Create pull request"**

5. Tag a teammate — top right, click **Reviewers**, add Nick or Dylan

6. They open the PR, glance at the diff, click **"Merge pull request"** → **"Confirm merge"**

7. Done — your changes are now in `main`. Everyone pulls next session and gets them.

> **Rule:** If GitHub won't let you merge because of conflicts, go back to your branch, run `git merge origin/main`, fix the conflicts locally, push again — the PR updates automatically.

---

### Conflict-Prone Files — Handle With Care

| File | Who owns it | Rule |
|---|---|---|
| `requirements.txt` | Everyone | Merge manually, keep all packages |
| `src/pipeline.py` | David + Nick | Coordinate before both editing |
| `DECISIONS.md` | Everyone | Edit different sections, no overlap |

---

## Running the Pipeline
*Author: David Gleason*

### Step 1 — Define Zone Logic (run once per video)

```bash
cd src
python zone_picker.py "path\to\video.MP4"
```

Controls:
- **Left-click** — add a point to the zone polygon
- **Enter** — finish the current zone
- **N** — discard current points, start a new zone
- **Right-click** — undo last point
- **S** — save zones to file
- **Q** — quit

To save zones under a specific name (recommended per video):
```bash
python zone_picker.py "path\to\video.MP4" 30 "zones_session1.json"
```

---

### Step 2 — Run the Full Pipeline

```bash
cd src
python pipeline.py "path\to\video.MP4" "path\to\video.SRT"
```

With a custom zones file or model:
```bash
python pipeline.py "path\to\video.MP4" "path\to\video.SRT" --zones "zones_session1.json" --model "../models/best_visdrone.pt"
```

Outputs:
- Annotated video → `outputs/annotated_video/pipeline_output.mp4`
- Speed + zone CSV → `outputs/csv_logs/speed_log.csv`

Overlay colors:
- **Green** box — vehicle outside all zones
- **Red** box — vehicle inside a zone


