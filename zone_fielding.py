
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ------------------------------------------------------------
# Shot-First Football - Polar threat visualization
# ------------------------------------------------------------
# Goal center is treated as the origin (0, 0).
# x-axis: distance away from the goal, into the pitch
# y-axis: lateral deviation from the central lane
#
# The animation shows:
# 1) Circular distance rings centered on the goal
# 2) A moving point that samples different shooting positions
# 3) Effective distance / threat score that penalizes wide angles
#
# Run:
#   python shot_first_polar_animation.py
#
# Optional:
#   To save as GIF/MP4, uncomment the save() line near the bottom.
# ------------------------------------------------------------


# ---------- PARAMETERS ----------
PITCH_LENGTH = 52.5   # half-pitch depth shown from goal line to midfield-ish
PITCH_WIDTH = 34.0    # half-width from center to touchline
RINGS = [8, 16, 22, 30, 40]
ANGLE_WEIGHT = 0.55   # how much lateral angle is penalized
FPS = 40
INTERVAL_MS = 40


def effective_distance(x: float, y: float, angle_weight: float = ANGLE_WEIGHT) -> float:
    """
    Angle-adjusted effective distance.

    x: forward distance from goal center
    y: lateral offset from central lane

    Idea:
    - Raw radial distance alone is not enough
    - Wide shots should be treated as less dangerous than central shots
    - This formula approximates that by adding an angle penalty through y

    You can tune this later.
    """
    return np.sqrt(x**2 + (1 + angle_weight) * y**2)


def threat_score(x: float, y: float) -> float:
    """
    A simple normalized threat score in [0, 1] based on effective distance.
    """
    d_eff = effective_distance(x, y)
    score = np.exp(-d_eff / 15.0)
    return float(np.clip(score, 0.0, 1.0))


def threat_category(score: float) -> str:
    """
    Categorize the shot by threat.
    """
    if score >= 0.62:
        return "A - Elite Threat"
    if score >= 0.42:
        return "B - High Threat"
    if score >= 0.27:
        return "C - Moderate Threat"
    if score >= 0.16:
        return "D - Speculative"
    return "E - Low Value"


def draw_pitch(ax):
    """
    Draw a simplified half-pitch with the goal at x=0, y=0.
    """
    # Outer boundary
    ax.plot([0, PITCH_LENGTH], [-PITCH_WIDTH, -PITCH_WIDTH], lw=2)
    ax.plot([0, PITCH_LENGTH], [PITCH_WIDTH, PITCH_WIDTH], lw=2)
    ax.plot([PITCH_LENGTH, PITCH_LENGTH], [-PITCH_WIDTH, PITCH_WIDTH], lw=2)
    ax.plot([0, 0], [-3.66, 3.66], lw=5)  # goal mouth

    # Penalty box
    ax.plot([0, 16.5], [-20.16, -20.16], lw=1.5)
    ax.plot([0, 16.5], [20.16, 20.16], lw=1.5)
    ax.plot([16.5, 16.5], [-20.16, 20.16], lw=1.5)

    # Six-yard box
    ax.plot([0, 5.5], [-9.16, -9.16], lw=1.5)
    ax.plot([0, 5.5], [9.16, 9.16], lw=1.5)
    ax.plot([5.5, 5.5], [-9.16, 9.16], lw=1.5)

    # Penalty spot
    ax.scatter([11], [0], s=25, zorder=3)

    # Central lane
    ax.axhline(0, linestyle="--", linewidth=1)

    # Circular distance rings
    theta = np.linspace(-np.pi/2, np.pi/2, 500)
    for r in RINGS:
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        mask = (x >= 0) & (x <= PITCH_LENGTH) & (y >= -PITCH_WIDTH) & (y <= PITCH_WIDTH)
        ax.plot(x[mask], y[mask], linestyle=":", linewidth=1.2)
        if r <= PITCH_LENGTH:
            ax.text(r, PITCH_WIDTH - 1.5, f"r={r}m", ha="center", va="top", fontsize=9)

    ax.set_xlim(-1, PITCH_LENGTH + 1)
    ax.set_ylim(-PITCH_WIDTH - 1, PITCH_WIDTH + 1)
    ax.set_aspect("equal")
    ax.set_xlabel("Distance from goal center (m)")
    ax.set_ylabel("Lateral offset from central lane (m)")
    ax.set_title("Shot-First Football: Polar Zone / Effective Threat Visualization")


def make_trajectory(num_frames: int):
    """
    Build a smooth trajectory that compares central and wide shots
    at different distances.
    """
    t = np.linspace(0, 1, num_frames)

    # Distance oscillates between ~10m and ~32m
    x = 21 + 11 * np.sin(2 * np.pi * t)

    # Lateral movement oscillates between central and wide
    y = 18 * np.sin(4 * np.pi * t + np.pi / 5)

    return x, y


def main():
    fig, ax = plt.subplots(figsize=(11, 7))
    draw_pitch(ax)

    point, = ax.plot([], [], marker="o", markersize=10, linestyle="")
    line_to_goal, = ax.plot([], [], linewidth=1.5)

    radial_text = ax.text(0.02, 0.97, "", transform=ax.transAxes, va="top", fontsize=11)
    angle_text = ax.text(0.02, 0.90, "", transform=ax.transAxes, va="top", fontsize=11)
    eff_text = ax.text(0.02, 0.83, "", transform=ax.transAxes, va="top", fontsize=11)
    score_text = ax.text(0.02, 0.76, "", transform=ax.transAxes, va="top", fontsize=11)
    category_text = ax.text(0.02, 0.69, "", transform=ax.transAxes, va="top", fontsize=12, fontweight="bold")

    explanation = ax.text(
        0.60, 0.97,
        "Idea:\n"
        "- Circular rings = raw distance\n"
        "- Wide angles get penalized\n"
        "- Central long shots can match\n"
        "  nearer wide shots in category",
        transform=ax.transAxes,
        va="top",
        fontsize=10,
        bbox=dict(boxstyle="round", alpha=0.15)
    )

    num_frames = 300
    xs, ys = make_trajectory(num_frames)

    def init():
        point.set_data([], [])
        line_to_goal.set_data([], [])
        radial_text.set_text("")
        angle_text.set_text("")
        eff_text.set_text("")
        score_text.set_text("")
        category_text.set_text("")
        return point, line_to_goal, radial_text, angle_text, eff_text, score_text, category_text, explanation

    def update(frame):
        x = float(xs[frame])
        y = float(ys[frame])

        d_raw = np.sqrt(x**2 + y**2)
        angle_deg = np.degrees(np.arctan2(abs(y), x))
        d_eff = effective_distance(x, y)
        score = threat_score(x, y)
        category = threat_category(score)

        point.set_data([x], [y])
        line_to_goal.set_data([0, x], [0, y])

        radial_text.set_text(f"Raw radial distance: {d_raw:.2f} m")
        angle_text.set_text(f"Shot angle from central lane: {angle_deg:.2f}°")
        eff_text.set_text(f"Effective distance: {d_eff:.2f} m")
        score_text.set_text(f"Threat score: {score:.3f}")
        category_text.set_text(f"Category: {category}")

        return point, line_to_goal, radial_text, angle_text, eff_text, score_text, category_text, explanation

    anim = FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=num_frames,
        interval=INTERVAL_MS,
        blit=True,
        repeat=True,
    )

    # To save:
    # anim.save("shot_first_polar_animation.gif", writer="pillow", fps=FPS)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
