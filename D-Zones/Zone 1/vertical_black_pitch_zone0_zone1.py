
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle
import numpy as np

PITCH_LENGTH = 105
PITCH_WIDTH = 68

LINE_COLOR = "white"
ZONE0_COLOR = "#00ff66"
ZONE1_COLOR = "#00cc55"


def draw_vertical_pitch(ax):
    ax.set_facecolor("black")
    lw = 2

    ax.add_patch(Rectangle((0, 0), PITCH_WIDTH, PITCH_LENGTH,
                           fill=False, edgecolor=LINE_COLOR, linewidth=lw))

    ax.plot([0, PITCH_WIDTH], [PITCH_LENGTH / 2, PITCH_LENGTH / 2],
            color=LINE_COLOR, linewidth=lw)

    ax.add_patch(Circle((PITCH_WIDTH / 2, PITCH_LENGTH / 2), 9.15,
                        fill=False, edgecolor=LINE_COLOR, linewidth=lw))
    ax.add_patch(Circle((PITCH_WIDTH / 2, PITCH_LENGTH / 2), 0.4, color=LINE_COLOR))

    penalty_width = 40.32
    penalty_depth = 16.5
    penalty_x = (PITCH_WIDTH - penalty_width) / 2

    ax.add_patch(Rectangle((penalty_x, 0), penalty_width, penalty_depth,
                           fill=False, edgecolor=LINE_COLOR, linewidth=lw))
    ax.add_patch(Rectangle((penalty_x, PITCH_LENGTH - penalty_depth), penalty_width, penalty_depth,
                           fill=False, edgecolor=LINE_COLOR, linewidth=lw))

    six_width = 18.32
    six_depth = 5.5
    six_x = (PITCH_WIDTH - six_width) / 2

    ax.add_patch(Rectangle((six_x, 0), six_width, six_depth,
                           fill=False, edgecolor=LINE_COLOR, linewidth=lw))
    ax.add_patch(Rectangle((six_x, PITCH_LENGTH - six_depth), six_width, six_depth,
                           fill=False, edgecolor=LINE_COLOR, linewidth=lw))

    bottom_penalty_spot = (PITCH_WIDTH / 2, 11)
    top_penalty_spot = (PITCH_WIDTH / 2, PITCH_LENGTH - 11)

    ax.add_patch(Circle(bottom_penalty_spot, 0.35, color=LINE_COLOR))
    ax.add_patch(Circle(top_penalty_spot, 0.35, color=LINE_COLOR))

    ax.add_patch(Arc(bottom_penalty_spot, 18.3, 18.3, angle=0,
                     theta1=38, theta2=142, color=LINE_COLOR, linewidth=lw))
    ax.add_patch(Arc(top_penalty_spot, 18.3, 18.3, angle=0,
                     theta1=218, theta2=322, color=LINE_COLOR, linewidth=lw))

    goal_width = 7.32
    goal_depth = 2
    goal_x = (PITCH_WIDTH - goal_width) / 2

    ax.add_patch(Rectangle((goal_x, -goal_depth), goal_width, goal_depth,
                           fill=False, edgecolor=LINE_COLOR, linewidth=lw))
    ax.add_patch(Rectangle((goal_x, PITCH_LENGTH), goal_width, goal_depth,
                           fill=False, edgecolor=LINE_COLOR, linewidth=lw))

    return {
        "bottom_penalty_spot": bottom_penalty_spot,
        "top_penalty_spot": top_penalty_spot,
        "penalty_x": penalty_x,
        "penalty_width": penalty_width,
        "penalty_depth": penalty_depth,
    }


def draw_zone0(ax, penalty_spot, is_top=True):
    """
    Zone 0 stays in its original position.
    """
    origin_x = PITCH_WIDTH / 2

    if is_top:
        origin_y = PITCH_LENGTH
        endpoint_angle_deg = 218
        theta = np.linspace(np.pi, 2 * np.pi, 500)
    else:
        origin_y = 0
        endpoint_angle_deg = 38
        theta = np.linspace(0, np.pi, 500)

    px, py = penalty_spot
    penalty_arc_radius = 9.15

    endpoint_x = px + penalty_arc_radius * np.cos(np.deg2rad(endpoint_angle_deg))
    endpoint_y = py + penalty_arc_radius * np.sin(np.deg2rad(endpoint_angle_deg))

    zone_radius = np.sqrt((endpoint_x - origin_x) ** 2 + (endpoint_y - origin_y) ** 2)

    x = origin_x + zone_radius * np.cos(theta)
    y = origin_y + zone_radius * np.sin(theta)

    ax.plot(x, y, color=ZONE0_COLOR, linewidth=2.5)
    ax.text(px + 2.2, py, "Zone 0", color=ZONE0_COLOR,
            fontsize=13, fontweight="bold", va="center", ha="left")


def draw_zone1(ax, penalty_x, penalty_width, penalty_depth, is_top=True):
    """
    Zone 1 label moved in front of the penalty area.
    """
    origin_x = PITCH_WIDTH / 2

    if is_top:
        origin_y = PITCH_LENGTH
        corner_y = PITCH_LENGTH - penalty_depth
        theta = np.linspace(np.pi, 2 * np.pi, 500)
        label_x = origin_x + 6
        label_y = PITCH_LENGTH - penalty_depth - 4.5
    else:
        origin_y = 0
        corner_y = penalty_depth
        theta = np.linspace(0, np.pi, 500)
        label_x = origin_x + 6
        label_y = penalty_depth + 4.5

    left_corner = (penalty_x, corner_y)

    zone_radius = np.sqrt((left_corner[0] - origin_x) ** 2 + (left_corner[1] - origin_y) ** 2)

    x = origin_x + zone_radius * np.cos(theta)
    y = origin_y + zone_radius * np.sin(theta)

    ax.plot(x, y, color=ZONE1_COLOR, linewidth=2.5)
    ax.text(label_x, label_y, "Zone 1", color=ZONE1_COLOR,
            fontsize=13, fontweight="bold", va="center", ha="left")


def main():
    fig, ax = plt.subplots(figsize=(7, 11))
    fig.patch.set_facecolor("black")

    info = draw_vertical_pitch(ax)

    draw_zone0(ax, info["top_penalty_spot"], is_top=True)
    draw_zone1(ax, info["penalty_x"], info["penalty_width"], info["penalty_depth"], is_top=True)

    draw_zone0(ax, info["bottom_penalty_spot"], is_top=False)
    draw_zone1(ax, info["penalty_x"], info["penalty_width"], info["penalty_depth"], is_top=False)

    ax.set_xlim(-4, PITCH_WIDTH + 4)
    ax.set_ylim(-4, PITCH_LENGTH + 4)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
