
"""
Shot-First Football - StatsBomb Zone 0 xG Calculator

This script downloads StatsBomb Open Data from GitHub, extracts shots,
filters shots inside your Zone 0 definition, and calculates average xG.

Coordinate note:
StatsBomb uses a 120 x 80 pitch.
- Attacking goal center is treated as (120, 40)
- Zone 0 is defined as the semi-circular region centered on the goal-line center
- The radius is calculated from the endpoint of the penalty arc, mirroring the
  visual method used in the Shot-First Football pitch diagrams.

"""

import json
import math
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle


BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

# Recommended starting point:
# 11 = La Liga
# 90 = 2015/2016
DEFAULT_COMPETITION_ID = 11
DEFAULT_SEASON_ID = 90

CACHE_DIR = Path("../../../statsbomb_cache")

SB_PITCH_LENGTH = 120
SB_PITCH_WIDTH = 80

GOAL_X = 120
GOAL_Y = 40

# StatsBomb-scaled geometry
PENALTY_SPOT_DISTANCE_X = 11 * (120 / 105)
PENALTY_ARC_RADIUS_X = 9.15 * (120 / 105)
PENALTY_ARC_RADIUS_Y = 9.15 * (80 / 68)


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(exist_ok=True)


def get_json(url: str, cache_path: Path):
    ensure_cache_dir()

    if cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    return data


def load_matches(competition_id: int, season_id: int) -> List[Dict]:
    url = f"{BASE_URL}/matches/{competition_id}/{season_id}.json"
    cache_path = CACHE_DIR / f"matches_{competition_id}_{season_id}.json"
    return get_json(url, cache_path)


def load_events(match_id: int) -> List[Dict]:
    url = f"{BASE_URL}/events/{match_id}.json"
    cache_path = CACHE_DIR / f"events_{match_id}.json"
    return get_json(url, cache_path)


def zone0_radius() -> float:
    """
    Radius from attacking goal-line center to one endpoint of the penalty arc.
    """
    penalty_spot_x = GOAL_X - PENALTY_SPOT_DISTANCE_X
    penalty_spot_y = GOAL_Y

    # Endpoint angle chosen to mirror the pitch diagram construction.
    angle_deg = 218

    endpoint_x = penalty_spot_x + PENALTY_ARC_RADIUS_X * math.cos(math.radians(angle_deg))
    endpoint_y = penalty_spot_y + PENALTY_ARC_RADIUS_Y * math.sin(math.radians(angle_deg))

    return math.sqrt((endpoint_x - GOAL_X) ** 2 + (endpoint_y - GOAL_Y) ** 2)


def is_zone0(x: float, y: float, radius: float) -> bool:
    distance = math.sqrt((x - GOAL_X) ** 2 + (y - GOAL_Y) ** 2)
    return distance <= radius


def extract_shots_from_events(events: List[Dict], match_id: int) -> List[Dict]:
    rows = []

    for event in events:
        if event.get("type", {}).get("name") != "Shot":
            continue

        location = event.get("location")
        shot = event.get("shot", {})

        if not location or len(location) < 2:
            continue

        x, y = location[0], location[1]

        rows.append({
            "match_id": match_id,
            "team": event.get("team", {}).get("name"),
            "player": event.get("player", {}).get("name"),
            "minute": event.get("minute"),
            "x": x,
            "y": y,
            "xg": shot.get("statsbomb_xg"),
            "outcome": shot.get("outcome", {}).get("name"),
            "body_part": shot.get("body_part", {}).get("name"),
            "technique": shot.get("technique", {}).get("name"),
            "play_pattern": event.get("play_pattern", {}).get("name"),
        })

    return rows


def collect_shots(competition_id: int, season_id: int, max_matches=None) -> pd.DataFrame:
    matches = load_matches(competition_id, season_id)

    if max_matches is not None:
        matches = matches[:max_matches]

    all_rows = []

    for i, match in enumerate(matches, start=1):
        match_id = match["match_id"]
        print(f"[{i}/{len(matches)}] Loading match {match_id}...")

        events = load_events(match_id)
        all_rows.extend(extract_shots_from_events(events, match_id))

    df = pd.DataFrame(all_rows)

    if df.empty:
        return df

    df = df.dropna(subset=["x", "y", "xg"])
    df["xg"] = pd.to_numeric(df["xg"], errors="coerce")
    df = df.dropna(subset=["xg"])

    radius = zone0_radius()
    df["distance_to_goal"] = ((df["x"] - GOAL_X) ** 2 + (df["y"] - GOAL_Y) ** 2) ** 0.5
    df["is_zone0"] = df.apply(lambda row: is_zone0(row["x"], row["y"], radius), axis=1)

    return df


def draw_statsbomb_pitch(ax):
    ax.set_facecolor("black")
    fig = ax.figure
    fig.patch.set_facecolor("black")

    line_color = "white"
    lw = 1.6

    ax.add_patch(Rectangle((0, 0), SB_PITCH_LENGTH, SB_PITCH_WIDTH,
                           fill=False, edgecolor=line_color, linewidth=lw))

    ax.plot([60, 60], [0, 80], color=line_color, linewidth=lw)

    ax.add_patch(Rectangle((102, 18), 18, 44, fill=False, edgecolor=line_color, linewidth=lw))
    ax.add_patch(Rectangle((0, 18), 18, 44, fill=False, edgecolor=line_color, linewidth=lw))

    ax.add_patch(Rectangle((114, 30), 6, 20, fill=False, edgecolor=line_color, linewidth=lw))
    ax.add_patch(Rectangle((0, 30), 6, 20, fill=False, edgecolor=line_color, linewidth=lw))

    ax.add_patch(Circle((60, 40), 10, fill=False, edgecolor=line_color, linewidth=lw))

    ax.add_patch(Circle((108, 40), 0.45, color=line_color))
    ax.add_patch(Circle((12, 40), 0.45, color=line_color))

    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)
    ax.set_aspect("equal")
    ax.axis("off")


def plot_zone0_shots(df: pd.DataFrame, output_path="sff_zone0_shots.png"):
    radius = zone0_radius()

    fig, ax = plt.subplots(figsize=(12, 8))
    draw_statsbomb_pitch(ax)

    non_zone = df[~df["is_zone0"]]
    zone = df[df["is_zone0"]]

    ax.scatter(non_zone["x"], non_zone["y"], s=12, alpha=0.25, label="Other shots")
    ax.scatter(zone["x"], zone["y"], s=28, alpha=0.85, label="Zone 0 shots")

    theta = [math.pi / 2 - i * math.pi / 300 for i in range(301)]
    xs = [GOAL_X - radius * math.cos(t) for t in theta]
    ys = [GOAL_Y + radius * math.sin(t) for t in theta]
    ax.plot(xs, ys, linewidth=2.5, label="Zone 0 boundary")

    ax.text(104, 43, "Zone 0", fontsize=16, weight="bold")

    ax.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor())
    print(f"Saved plot: {output_path}")


def summarize(df: pd.DataFrame) -> None:
    radius = zone0_radius()
    zone0 = df[df["is_zone0"]]
    outside = df[~df["is_zone0"]]

    print("\n--- Shot-First Football Zone 0 Summary ---")
    print(f"Zone 0 radius in StatsBomb coordinates: {radius:.2f}")
    print(f"Total shots: {len(df)}")
    print(f"Zone 0 shots: {len(zone0)}")
    print(f"Outside Zone 0 shots: {len(outside)}")

    if len(zone0) > 0:
        print(f"Zone 0 average xG: {zone0['xg'].mean():.4f}")
        print(f"Zone 0 median xG: {zone0['xg'].median():.4f}")
        print(f"Zone 0 goal rate: {(zone0['outcome'] == 'Goal').mean():.4f}")

    if len(outside) > 0:
        print(f"Outside Zone 0 average xG: {outside['xg'].mean():.4f}")
        print(f"Outside Zone 0 median xG: {outside['xg'].median():.4f}")
        print(f"Outside Zone 0 goal rate: {(outside['outcome'] == 'Goal').mean():.4f}")

    if len(zone0) > 0:
        print("\nTop Zone 0 shooters by shot count:")
        summary = zone0.groupby("player").agg(
            shots=("xg", "count"),
            avg_xg=("xg", "mean"),
            goals=("outcome", lambda s: (s == "Goal").sum())
        ).sort_values("shots", ascending=False).head(15)

        print(summary)


def main():
    competition_id = DEFAULT_COMPETITION_ID
    season_id = DEFAULT_SEASON_ID

    # For testing, set max_matches = 3.
    # For full season, set max_matches = None.
    max_matches = None

    df = collect_shots(competition_id, season_id, max_matches=max_matches)

    if df.empty:
        print("No shots found.")
        return

    summarize(df)

    csv_path = "sff_statsbomb_shots_with_zone0.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved data: {csv_path}")

    plot_zone0_shots(df)


if __name__ == "__main__":
    main()
