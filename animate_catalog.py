"""
Makes an animation of a given eqcorrscan Party

:author: Toby Messerli
:date: 13/2/2020
"""
from eqcorrscan import Party
import animator
from matplotlib import animation
def animate_catalog(party):
    """
        creates a catalog from the given party and makes a simple animation from it
            :type party: eqcorrscan Party
            :param party: The party containing the events to be animated
            """
    catalog = party.get_catalog()
    my_animator = animator.AnimatedCatalog(catalog)
    my_animation = my_animator.animate(interval=1000, projection="local")
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=45, metadata=dict(artist="Me"), bitrate=1800)

    my_animation.save("party_animation.mp4", writer=writer)
    print("done")


if __name__ == "__main__":
    party = Party().read("party_with_origins.tgz")
    animate_catalog(party)