
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle

# ------------------------------------------------------------
# Vertical football pitch template
# Black background, white pitch lines
# Designed as a base for Shot-First Football visualizations
# ------------------------------------------------------------

PITCH_LENGTH = 105
PITCH_WIDTH = 68

def draw_vertical_pitch(ax):
    ax.set_facecolor("black")

    line_color = "white"
    lw = 2

    # Outer boundary
    ax.add_patch(Rectangle(
        (0, 0),
        PITCH_WIDTH,
        PITCH_LENGTH,
        fill=False,
        edgecolor=line_color,
        linewidth=lw
    ))

    # Halfway line
    ax.plot([0, PITCH_WIDTH], [PITCH_LENGTH / 2, PITCH_LENGTH / 2],
            color=line_color, linewidth=lw)

    # Center circle and spot
    ax.add_patch(Circle(
        (PITCH_WIDTH / 2, PITCH_LENGTH / 2),
        9.15,
        fill=False,
        edgecolor=line_color,
        linewidth=lw
    ))
    ax.add_patch(Circle(
        (PITCH_WIDTH / 2, PITCH_LENGTH / 2),
        0.4,
        color=line_color
    ))

    # Penalty areas
    penalty_width = 40.32
    penalty_depth = 16.5
    penalty_x = (PITCH_WIDTH - penalty_width) / 2

    ax.add_patch(Rectangle(
        (penalty_x, 0),
        penalty_width,
        penalty_depth,
        fill=False,
        edgecolor=line_color,
        linewidth=lw
    ))

    ax.add_patch(Rectangle(
        (penalty_x, PITCH_LENGTH - penalty_depth),
        penalty_width,
        penalty_depth,
        fill=False,
        edgecolor=line_color,
        linewidth=lw
    ))

    # Six-yard boxes
    six_width = 18.32
    six_depth = 5.5
    six_x = (PITCH_WIDTH - six_width) / 2

    ax.add_patch(Rectangle(
        (six_x, 0),
        six_width,
        six_depth,
        fill=False,
        edgecolor=line_color,
        linewidth=lw
    ))

    ax.add_patch(Rectangle(
        (six_x, PITCH_LENGTH - six_depth),
        six_width,
        six_depth,
        fill=False,
        edgecolor=line_color,
        linewidth=lw
    ))

    # Penalty spots
    ax.add_patch(Circle((PITCH_WIDTH / 2, 11), 0.35, color=line_color))
    ax.add_patch(Circle((PITCH_WIDTH / 2, PITCH_LENGTH - 11), 0.35, color=line_color))

    # Penalty arcs
    ax.add_patch(Arc(
        (PITCH_WIDTH / 2, 11),
        18.3,
        18.3,
        angle=0,
        theta1=38,
        theta2=142,
        color=line_color,
        linewidth=lw
    ))

    ax.add_patch(Arc(
        (PITCH_WIDTH / 2, PITCH_LENGTH - 11),
        18.3,
        18.3,
        angle=0,
        theta1=218,
        theta2=322,
        color=line_color,
        linewidth=lw
    ))

    # Goals
    goal_width = 7.32
    goal_depth = 2
    goal_x = (PITCH_WIDTH - goal_width) / 2

    ax.add_patch(Rectangle(
        (goal_x, -goal_depth),
        goal_width,
        goal_depth,
        fill=False,
        edgecolor=line_color,
        linewidth=lw
    ))

    ax.add_patch(Rectangle(
        (goal_x, PITCH_LENGTH),
        goal_width,
        goal_depth,
        fill=False,
        edgecolor=line_color,
        linewidth=lw
    ))

    # Corner arcs
    ax.add_patch(Arc((0, 0), 2, 2, angle=0, theta1=0, theta2=90,
                     color=line_color, linewidth=lw))
    ax.add_patch(Arc((PITCH_WIDTH, 0), 2, 2, angle=0, theta1=90, theta2=180,
                     color=line_color, linewidth=lw))
    ax.add_patch(Arc((0, PITCH_LENGTH), 2, 2, angle=0, theta1=270, theta2=360,
                     color=line_color, linewidth=lw))
    ax.add_patch(Arc((PITCH_WIDTH, PITCH_LENGTH), 2, 2, angle=0, theta1=180, theta2=270,
                     color=line_color, linewidth=lw))

    ax.set_xlim(-4, PITCH_WIDTH + 4)
    ax.set_ylim(-4, PITCH_LENGTH + 4)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    fig, ax = plt.subplots(figsize=(7, 11))
    fig.patch.set_facecolor("black")

    draw_vertical_pitch(ax)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
