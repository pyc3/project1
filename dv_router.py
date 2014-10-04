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
            self.ports[packet.src] = port
            self.sendUpdate()

        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = packet.paths # am i allowed to do this?
            for pkt, pt in self.ports.items():
                if pt == port: # do i need to instantiate source somewhere else? will def be something right?
                    source = pkt # get the source of routing packet to update your forwarding table
                    continue
            self.log("source %s" % source)
            for x in routing_table.keys():
                self.log("self: %s" % self)
                self.log("key: %s" % x)
                self.log("neighbors: %s" % str(self.neighbors))
                self.log("forwarding table: %s" % str(self.forwarding_table))
                self.log("routing table %s" % str(routing_table))
                # update their row of forwarding table
                self.forwarding_table[(source,x)] = routing_table[x]
                # update your row of forwarding table
                # maybe i didn't have anything in that slot before
                if x == self:
                    return # don't have to do anything because discovery packet will do it???
                #self.log("routing_table[x]= %s neighbors[source]= %s forwarding_Table[self,x][0]=%s" % (routing_table[x], self.neighbors[source], self.forwarding_table[self,x][0]))
                if (((self,x) not in self.forwarding_table) or ((routing_table[x] + self.neighbors[source]) < self.forwarding_table[self,x][0])):
                    self.log("goes in here")
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
            # create tuple just for my row in the forwarding table
            # myRow = {}
            # for x,y in self.forwarding_table.items():
            #     if x[0] == self:
            #         myRow[x[1]] = y[0]
            for x,y in self.forwarding_table.items():
                if x[0] == self:
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
                        message.paths = {key:value for key, value in message.paths.items() if key != p}
            message.src = self
            message.dst = n #necessary?
            self.history[n] = message
            self.send(message, self.ports[n])


