"""
Shot-First Football - D-Zone 2 Multi-Season StatsBomb xG Calculator

This version can scan multiple StatsBomb competition/season pairs.

Definition:
- Zone 0: semicircle centered on attacking goal-line center,
  radius determined by the penalty arc endpoint.
- Zone 1: semicircle centered on attacking goal-line center,
  radius determined by the front corners of the penalty area.
- Zone 2: semicircle centered on attacking goal-line center,
  radius determined by the attacking-side corner points.
- D-Zone 1: inside Zone 1 AND outside Zone 0.
- D-Zone 2: inside Zone 2 AND outside Zone 1.

Plot colors:
- Goal shots: green
- Non-goal shots: red

Install:
    pip install pandas requests matplotlib

Run:
    python sff_statsbomb_dzone2_multi_season.py
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle


BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
CACHE_DIR = Path("../../../statsbomb_cache")

SB_PITCH_LENGTH = 120
SB_PITCH_WIDTH = 80

GOAL_X = 120
GOAL_Y = 40

PENALTY_SPOT_DISTANCE_X = 11 * (120 / 105)
PENALTY_ARC_RADIUS_X = 9.15 * (120 / 105)
PENALTY_ARC_RADIUS_Y = 9.15 * (80 / 68)

# Add or remove competition/season pairs here.
# Common examples in StatsBomb open data:
# 11 = La Liga
# 90 = 2015/2016
# 42 = FA Women's Super League
# 4 = 2018/2019
#
# IMPORTANT:
# Not every competition_id / season_id pair exists in StatsBomb open data.
# If a pair does not exist, the script will skip it.
COMPETITION_SEASONS: List[Tuple[int, int]] = [
    (11, 90),  # La Liga 2015/2016
    (11, 4),
    (11, 1),
    # (42, 4),  # FA Women's Super League 2018/2019, if available
]

# Use None to take every match from every listed season.
# Use a number like 5 for quick testing.
MAX_MATCHES_PER_SEASON = None


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(exist_ok=True)


def get_json(url: str, cache_path: Path):
    ensure_cache_dir()

    if cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    response = requests.get(url, timeout=30)

    if response.status_code == 404:
        raise FileNotFoundError(f"StatsBomb file not found: {url}")

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
    penalty_spot_x = GOAL_X - PENALTY_SPOT_DISTANCE_X
    penalty_spot_y = GOAL_Y

    angle_deg = 218

    endpoint_x = penalty_spot_x + PENALTY_ARC_RADIUS_X * math.cos(math.radians(angle_deg))
    endpoint_y = penalty_spot_y + PENALTY_ARC_RADIUS_Y * math.sin(math.radians(angle_deg))

    return math.sqrt((endpoint_x - GOAL_X) ** 2 + (endpoint_y - GOAL_Y) ** 2)


def zone1_radius() -> float:
    penalty_area_front_x = 102
    penalty_area_left_y = 18

    return math.sqrt(
        (penalty_area_front_x - GOAL_X) ** 2 +
        (penalty_area_left_y - GOAL_Y) ** 2
    )


def zone2_radius() -> float:
    """
    Zone 2 circle passes through the attacking-side corner points.

    StatsBomb pitch coordinates:
    - attacking goal center: (120, 40)
    - attacking corner points: (120, 0) and (120, 80)

    Distance from (120, 40) to either corner is 40.
    """
    attacking_corner_y = 0
    return math.sqrt((GOAL_X - GOAL_X) ** 2 + (attacking_corner_y - GOAL_Y) ** 2)


def distance_to_goal(x: float, y: float) -> float:
    return math.sqrt((x - GOAL_X) ** 2 + (y - GOAL_Y) ** 2)


def extract_shots_from_events(
    events: List[Dict],
    match_id: int,
    competition_id: int,
    season_id: int,
) -> List[Dict]:
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
            "competition_id": competition_id,
            "season_id": season_id,
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


def collect_shots_for_pair(
    competition_id: int,
    season_id: int,
    max_matches=None
) -> pd.DataFrame:
    try:
        matches = load_matches(competition_id, season_id)
    except FileNotFoundError as e:
        print(f"Skipping competition_id={competition_id}, season_id={season_id}: {e}")
        return pd.DataFrame()

    if max_matches is not None:
        matches = matches[:max_matches]

    all_rows = []

    print(f"\nLoading competition_id={competition_id}, season_id={season_id}")
    print(f"Matches to load: {len(matches)}")

    for i, match in enumerate(matches, start=1):
        match_id = match["match_id"]
        print(f"[{i}/{len(matches)}] Loading match {match_id}...")

        try:
            events = load_events(match_id)
        except FileNotFoundError as e:
            print(f"Skipping match {match_id}: {e}")
            continue

        all_rows.extend(
            extract_shots_from_events(events, match_id, competition_id, season_id)
        )

    return pd.DataFrame(all_rows)


def collect_all_shots() -> pd.DataFrame:
    frames = []

    for competition_id, season_id in COMPETITION_SEASONS:
        df_pair = collect_shots_for_pair(
            competition_id,
            season_id,
            max_matches=MAX_MATCHES_PER_SEASON
        )

        if not df_pair.empty:
            frames.append(df_pair)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)

    df = df.dropna(subset=["x", "y", "xg"])
    df["xg"] = pd.to_numeric(df["xg"], errors="coerce")
    df = df.dropna(subset=["xg"])

    z0 = zone0_radius()
    z1 = zone1_radius()
    z2 = zone2_radius()

    df["distance_to_goal"] = df.apply(lambda row: distance_to_goal(row["x"], row["y"]), axis=1)
    df["is_zone0"] = df["distance_to_goal"] <= z0
    df["is_zone1"] = df["distance_to_goal"] <= z1
    df["is_zone2"] = df["distance_to_goal"] <= z2
    df["is_dzone1"] = df["is_zone1"] & (~df["is_zone0"])
    df["is_dzone2"] = df["is_zone2"] & (~df["is_zone1"])

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


def zone_boundary_points(radius: float):
    theta = [math.pi / 2 - i * math.pi / 300 for i in range(301)]
    xs = [GOAL_X - radius * math.cos(t) for t in theta]
    ys = [GOAL_Y + radius * math.sin(t) for t in theta]
    return xs, ys


def plot_dzone2_shots(df: pd.DataFrame, output_path="sff_dzone2_shots.png"):
    z1 = zone1_radius()
    z2 = zone2_radius()

    fig, ax = plt.subplots(figsize=(12, 8))
    draw_statsbomb_pitch(ax)

    dzone2 = df[df["is_dzone2"]]
    goals = dzone2[dzone2["outcome"] == "Goal"]
    non_goals = dzone2[dzone2["outcome"] != "Goal"]

    ax.scatter(
        non_goals["x"],
        non_goals["y"],
        s=14,
        alpha=0.55,
        c="red",
        label="No Goal"
    )

    ax.scatter(
        goals["x"],
        goals["y"],
        s=34,
        alpha=0.9,
        c="#00ff66",
        edgecolors="white",
        linewidths=0.4,
        label="Goal"
    )

    zone1_xs, zone1_ys = zone_boundary_points(z1)
    zone2_xs, zone2_ys = zone_boundary_points(z2)

    ax.plot(zone1_xs, zone1_ys, color="#00cc55", linewidth=1.8, linestyle="--", label="Zone 1 boundary")
    ax.plot(zone2_xs, zone2_ys, color="#009944", linewidth=2.5, label="Zone 2 boundary")

    ax.text(84, 51, "D-Zone 2", color="#009944", fontsize=16, weight="bold")

    ax.legend(loc="lower left", facecolor="black", edgecolor="white", labelcolor="white")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor())
    print(f"Saved plot: {output_path}")


def summarize_zone(name: str, zone_df: pd.DataFrame) -> None:
    print(f"{name} shots: {len(zone_df)}")

    if len(zone_df) > 0:
        print(f"{name} average xG: {zone_df['xg'].mean():.4f}")
        print(f"{name} median xG: {zone_df['xg'].median():.4f}")
        print(f"{name} total xG: {zone_df['xg'].sum():.4f}")
        print(f"{name} goals: {(zone_df['outcome'] == 'Goal').sum()}")
        print(f"{name} goal rate: {(zone_df['outcome'] == 'Goal').mean():.4f}")


def summarize(df: pd.DataFrame) -> None:
    z0 = zone0_radius()
    z1 = zone1_radius()
    z2 = zone2_radius()

    dzone1 = df[df["is_dzone1"]]
    dzone2 = df[df["is_dzone2"]]
    outside_dzone2 = df[~df["is_dzone2"]]

    print("\n--- Shot-First Football D-Zone 2 Multi-Season Summary ---")
    print(f"Competition/season pairs scanned: {COMPETITION_SEASONS}")
    print(f"Zone 0 radius in StatsBomb coordinates: {z0:.2f}")
    print(f"Zone 1 radius in StatsBomb coordinates: {z1:.2f}")
    print(f"Zone 2 radius in StatsBomb coordinates: {z2:.2f}")
    print(f"Total shots: {len(df)}")

    print()
    summarize_zone("D-Zone 1", dzone1)
    print()
    summarize_zone("D-Zone 2", dzone2)
    print()
    summarize_zone("Outside D-Zone 2", outside_dzone2)

    if len(dzone2) > 0:
        print("\nTop D-Zone 2 shooters by shot count:")
        summary = dzone2.groupby("player").agg(
            shots=("xg", "count"),
            avg_xg=("xg", "mean"),
            total_xg=("xg", "sum"),
            goals=("outcome", lambda s: (s == "Goal").sum())
        ).sort_values("shots", ascending=False).head(20)

        print(summary)

    print("\nShots by competition/season:")
    by_season = (
        df.assign(dzone2_xg=df["xg"].where(df["is_dzone2"]))
        .groupby(["competition_id", "season_id"])
        .agg(
            total_shots=("xg", "count"),
            dzone1_shots=("is_dzone1", "sum"),
            dzone2_shots=("is_dzone2", "sum"),
            avg_xg=("xg", "mean"),
            dzone2_avg_xg=("dzone2_xg", "mean"),
        )
    )
    print(by_season)


def main():
    df = collect_all_shots()

    if df.empty:
        print("No shots found.")
        return

    summarize(df)

    csv_path = "sff_statsbomb_dzone2.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved data: {csv_path}")

    plot_dzone2_shots(df)


if __name__ == "__main__":
    main()
