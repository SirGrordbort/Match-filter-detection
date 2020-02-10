
from eqcorrscan import Party
import animator
from matplotlib import animation
def animate_catalog(party):
    catalog = party.get_catalog()
    my_animator = animator.AnimatedCatalog(catalog)
    my_animation = my_animator.animate(interval=100000, projection="local")
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=45, metadata=dict(artist="Me"), bitrate=1800)

    my_animation.save("Test_animation.mp4", writer=writer)
    print("done")


if __name__ == "__main__":
    party = Party().read("party_with_origins.tgz")
    animate_catalog(party)