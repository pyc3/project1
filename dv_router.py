from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity): # only hosts and dvrouters
    def __init__(self):
        self.neighbors = {} # check through_who when deciding what to routeupdate them, for the extra 10 points, {A:1, B:2}
        self.forwarding_table = {} # example forwarding table: {(A,1) : C, (B,2) : D, (dest,cost) : through_who}
        # {((from, dest): (distance, from who))}, example: {(a, b):(2, a)}
        self.history = {} # keep history of what you've sent each of your neighbors (HINT HINT) {neighbor: last sent, neighbor1: last sent}
        self.ports = {} # keep track of which ports link to which neighbors, from discovery packet {neighbor: port#, neighbor1: port1#}
        pass

    def handle_rx (self, packet, port):

        # routing updates could be diff for diff neighbors, store routing updates as {(a, b):(2, a)}

        # DISCOVERY PACKET
        if isinstance(packet, DiscoveryPacket):



            # know where the links/ports are
            # OR know when a link is down
            # OR know when a link cost has changed
            if packet.is_link_up: # no need to differentiate?
                # LINK DOWN
                if packet.latency == float("inf"):
                    # assuming it was already up
                    self.neighbors[packet.src] = packet.latency
                    self.fowarding_table[(packet.dst, packet.latency)] = packet.src
                    # send routing updates to relevant neighbors
                    ##

                # LINK COST CHANGE
                if packet in self.neighbors:
                    self.neighbors[packet.src] = packet.latency
                    self.fowarding_table[(packet.dst, packet.latency)] = packet.src
                    # change forwarding table too
                    # send routing update to RELEVANT neighbors (not through one who told you)

                # LINK UP
                # test
                print 'discovery packet DISCOVERED :D :D'
                self.ports[packet.src] = port # add which neighbors are reachable from which port
                self.neighbors[packet.src] = packet.latency # distance to neighbors
                self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                for x in len(self.neighbors.keys()):
                    message = reRoute(x, packet, forwarding_table, neighbors) # a routingupdate

                # check if path goes through neighbor you're thinking of sending it to
                for x in self.neighbors.keys():
                    message = RoutingUpdate()
                    if x in self.history: # check if you already sent the exact same thing / unnecessary
                        old_message = self.history[x] # or should i put this in the other loop below and remove if i've sent this before? hard to remove from tuple...
                    for y in self.forwarding_table.values() & f in self.forwarding_tables.keys():
                        if x != y:
                            message.add_destination(f[0], f[1])
                    send(message, self.ports[x], False)
                    self.history[x] = message
                

            return

        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = RoutingUpdate.paths # am i allowed to do this?
            for pkt, pt in ports.items():
                if pt == port: # do i need to instantiate source somewhere else? will def be something right?
                    source = pkt # get the source of routing packet to update your forwarding table
            for x in routing_table.keys():
                # update their row of forwarding table
                forwarding_table[(source,x)] = routing_table[x]
                # update your row of forwarding table
                if (routing_table[x] + neighbors[source]) < forwarding_table[self,x][0]:
                    forwarding_table[self,x] = (routing_table[x] + neighbors[source], source)
            self.sendUpdate()

        else: # DATA PACKET
            if (self, packet.dst) in forwarding_table.keys():
                values = forwarding_table[(self, packet.dst)]
                if values[1] != self:
                    self.send(packet, ports[values[1]])
                else:
                    self.send(packet, ports[packet.dst])
            # else: drop the packet! (just don't send)

    def sendUpdate(self):
        forwarding_table = self.forwarding_table
        neighbors = self.neighbors
        for n in neighbors.keys():
            message = RoutingUpdate()
            for x,y in forwarding_table.items():
                if y[1] == n:
                    message.add_destination(x[1], float("inf"))
                else:
                    message.add_destination(x[1], y[0])
            self.send(message, self.ports[n])