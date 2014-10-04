from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity): # only hosts and dvrouters
    def __init__(self):
        self.neighbors = {} # check through_who when deciding what to routeupdate them, for the extra 10 points, {A:1, B:2}
        self.forwarding_table = {}
        self.ports = {}
        self.history = {}
        pass

    def handle_rx (self, packet, port):
        if isinstance(packet, DiscoveryPacket): # DISCOVERY PACKET
            self.neighbors[packet.src] = packet.latency
            self.forwarding_table[(self, packet.src)] = (packet.latency, self)
            self.sendUpdate()

        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = RoutingUpdate.paths # am i allowed to do this?
            for pkt, pt in self.ports.items():
                if pt == port: # do i need to instantiate source somewhere else? will def be something right?
                    source = pkt # get the source of routing packet to update your forwarding table
            for x in routing_table.keys():
                # update their row of forwarding table
                self.forwarding_table[(source,x)] = routing_table[x]
                # update your row of forwarding table
                if (routing_table[x] + self.neighbors[source]) < self.forwarding_table[self,x][0]:
                    self.forwarding_table[self,x] = (routing_table[x] + self.neighbors[source], source)
            self.sendUpdate()

        else: # DATA PACKET
            if (self, packet.dst) in self.forwarding_table.keys():
                values = self.forwarding_table[(self, packet.dst)]
                if values[1] != self:
                    self.send(packet, self.ports[values[1]])
                else:
                    self.send(packet, self.ports[packet.dst])
            # else: drop the packet! (just don't send)

    def sendUpdate (self):
        for n in self.neighbors.keys():
            message = RoutingUpdate()
            for x,y in self.forwarding_table.items():
                if y[1] == n:
                    message.add_destination(x[1], float("inf"))
                else:
                    message.add_destination(x[1], y[0])
            if n in self.history.keys(): # don't send redundant information
                oldmessage = self.history[n]
                oldrouting_table = oldmessage.paths
                for p,q in oldrouting_table.items():
                    if message.get_distance(p) == q:
                        # delete from message
                        message.paths = {key:value for key, value in paths.items() if key != p}
            self.history[n] = message
            self.send(message, self.ports[n])


