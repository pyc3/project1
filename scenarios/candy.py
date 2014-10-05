import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo

def create (switch_type = Hub, host_type = BasicHost):
    """
    Creates a topology with loops that looks like:
    h1a    s4--s5    h2a
       \  /      \  /
        s1        s2
       /  \      /  \ 
    h1b    --s3--    h2b
    """

    switch_type.create('s1')
    switch_type.create('s2')
    switch_type.create('s3')
    switch_type.create('s4')

    # host_type.create('h1a')
    # host_type.create('h1b')
    # host_type.create('h2a')
    # host_type.create('h2b')

    topo.link(s1, s2)
    topo.link(s2, s3)
