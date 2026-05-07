
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle
import numpy as np

PITCH_LENGTH = 105
PITCH_WIDTH = 68

def draw_vertical_pitch(ax):
    ax.set_facecolor("black")
    line_color = "white"
    lw = 2

    ax.add_patch(Rectangle((0, 0), PITCH_WIDTH, PITCH_LENGTH, fill=False, edgecolor=line_color, linewidth=lw))
    ax.plot([0, PITCH_WIDTH], [PITCH_LENGTH / 2, PITCH_LENGTH / 2], color=line_color, linewidth=lw)

    ax.add_patch(Circle((PITCH_WIDTH / 2, PITCH_LENGTH / 2), 9.15, fill=False, edgecolor=line_color, linewidth=lw))
    ax.add_patch(Circle((PITCH_WIDTH / 2, PITCH_LENGTH / 2), 0.4, color=line_color))

    penalty_width = 40.32
    penalty_depth = 16.5
    penalty_x = (PITCH_WIDTH - penalty_width) / 2

    ax.add_patch(Rectangle((penalty_x, 0), penalty_width, penalty_depth, fill=False, edgecolor=line_color, linewidth=lw))
    ax.add_patch(Rectangle((penalty_x, PITCH_LENGTH - penalty_depth), penalty_width, penalty_depth, fill=False, edgecolor=line_color, linewidth=lw))

    six_width = 18.32
    six_depth = 5.5
    six_x = (PITCH_WIDTH - six_width) / 2

    ax.add_patch(Rectangle((six_x, 0), six_width, six_depth, fill=False, edgecolor=line_color, linewidth=lw))
    ax.add_patch(Rectangle((six_x, PITCH_LENGTH - six_depth), six_width, six_depth, fill=False, edgecolor=line_color, linewidth=lw))

    bottom_penalty_spot = (PITCH_WIDTH / 2, 11)
    top_penalty_spot = (PITCH_WIDTH / 2, PITCH_LENGTH - 11)

    ax.add_patch(Circle(bottom_penalty_spot, 0.35, color=line_color))
    ax.add_patch(Circle(top_penalty_spot, 0.35, color=line_color))

    ax.add_patch(Arc(bottom_penalty_spot, 18.3, 18.3, angle=0, theta1=38, theta2=142, color=line_color, linewidth=lw))
    ax.add_patch(Arc(top_penalty_spot, 18.3, 18.3, angle=0, theta1=218, theta2=322, color=line_color, linewidth=lw))

    goal_width = 7.32
    goal_depth = 2
    goal_x = (PITCH_WIDTH - goal_width) / 2

    ax.add_patch(Rectangle((goal_x, -goal_depth), goal_width, goal_depth, fill=False, edgecolor=line_color, linewidth=lw))
    ax.add_patch(Rectangle((goal_x, PITCH_LENGTH), goal_width, goal_depth, fill=False, edgecolor=line_color, linewidth=lw))

    return bottom_penalty_spot, top_penalty_spot


def draw_zone(ax, penalty_spot, is_top=True):
    green = "#00ff66"
    origin_x = PITCH_WIDTH / 2

    if is_top:
        origin_y = PITCH_LENGTH
        angle = 218
        theta = np.linspace(np.pi, 2*np.pi, 500)
    else:
        origin_y = 0
        angle = 38
        theta = np.linspace(0, np.pi, 500)

    penalty_arc_radius = 9.15
    px, py = penalty_spot

    endpoint_x = px + penalty_arc_radius * np.cos(np.deg2rad(angle))
    endpoint_y = py + penalty_arc_radius * np.sin(np.deg2rad(angle))

    zone_radius = np.sqrt((endpoint_x - origin_x)**2 + (endpoint_y - origin_y)**2)

    x = origin_x + zone_radius * np.cos(theta)
    y = origin_y + zone_radius * np.sin(theta)

    ax.plot(x, y, color=green, linewidth=2.5)
    ax.add_patch(Circle((origin_x, origin_y), 0.45, color=green))

    ax.text(px + 2.2, py, "Zone 0", color=green, fontsize=14, fontweight="bold", va="center")


def main():
    fig, ax = plt.subplots(figsize=(7, 11))
    fig.patch.set_facecolor("black")

    bottom_spot, top_spot = draw_vertical_pitch(ax)

    draw_zone(ax, bottom_spot, is_top=False)

    ax.set_xlim(-4, PITCH_WIDTH + 4)
    ax.set_ylim(-4, PITCH_LENGTH + 4)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
