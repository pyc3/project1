from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity): # only hosts and dvrouters
    def __init__(self):
        self.neighbors = {}
        self.forwarding_table = {}
        self.ports = {}
        self.history = {}
        pass

    def handle_rx (self, packet, port):
        if isinstance(packet, DiscoveryPacket): # DISCOVERY PACKET
            self.neighbors[packet.src] = packet.latency
            self.forwarding_table[(self, packet.src)] = (packet.latency, self)
            self.ports[packet.src] = port
            self.log("send before discovery packet")
            self.sendUpdate() # dont send updates when link just came up

        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = packet.paths
            for pkt, pt in self.ports.items():
                if pt == port: # do i need to instantiate source outside just in case?
                    source = pkt # get the source of routing packet to update your forwarding table
                    continue
            for x in routing_table.keys():
                # update their row of forwarding table
                self.forwarding_table[(source,x)] = routing_table[x]
                # update your row of forwarding table
                if x == self:
                    return # don't have to do anything because discovery packet will do it???
                if (((self,x) not in self.forwarding_table) or ((routing_table[x] + self.neighbors[source]) < self.forwarding_table[self,x][0])):
                    self.forwarding_table[self,x] = (routing_table[x] + self.neighbors[source], source)
                    changed = True
                if (self,x) in self.forwarding_table:
                    if ((routing_table[x] + self.neighbors[source]) > self.forwarding_table[self,x][0]):
                        changed = False # I'M NOT GIVING A BETTER PATH FOR MY NEIGHBORSSSSS THIS IS A PROBLEM
                    if ((routing_table[x] + self.neighbors[source]) == self.forwarding_table[self,x][0]):
                        # pick port # that is lower
                        port1 = self.ports[source]
                        if (self == self.forwarding_table[self,x][1]):
                            port2 = self.ports[x]
                        else:
                            port2 = self.ports[self.forwarding_table[self,x][1]]
                        if port1 < port2:
                            self.forwarding_table[self,x] = (routing_table[x] + self.neighbors[source], source)
                            # changed = True
            self.log("send before update packet")
            if changed:
                self.sendUpdate()
            

        else: # DATA PACKET
            if (self, packet.dst) in self.forwarding_table.keys():
                if self.forwarding_table[(self, packet.dst)][1] > 50:
                    #withdraw route
                    self.log("you've reached 50")
                    self.forwarding_table[(self, packet.dst)][1] = float("inf")
                    return #?
                if self.forwarding_table[(self, packet.dst)][1] != self:
                    self.send(packet, self.ports[self.forwarding_table[(self, packet.dst)][1]])
                else:
                    if packet.dst in self.neighbors:
                        self.send(packet, self.ports[packet.dst])
                    else:
                        out = self.forwarding_table[self, packet.dst][1]
                        self.log("send before data packet")
                        self.send(packet, self.ports[out])


    def sendUpdate (self):
        for n in self.neighbors.keys():
            message = RoutingUpdate()
            if self.neighbors[n] == float("inf"):
                continue
            for x,y in self.forwarding_table.items():
                #self.log("y[1] = %s" % y[1])
                if x[0] == self:
                    # don't tell neighbor about its distance to you
                    # if y[1] == self:
                    #     continue
                    if x[1] == n:
                        #self.log("appropriate? %s %s %s" % (x[1], n, self))
                        continue
                    if y[1] == n: # dont tell neighbor about path through neighbor, set to infinity
                        #self.log("did it get here")
                        message.add_destination(x[1], float("inf")) 
                    else:
                        message.add_destination(x[1], y[0])
            if n in self.history.keys(): # don't send redundant information
                oldmessage = self.history[n]
                oldrouting_table = oldmessage.paths
                for p in oldrouting_table.keys():
                    if message.get_distance(p) == oldrouting_table[p]:
                        message.paths = {key:value for key, value in message.paths.items() if key != p}
            #self.log("message is %s" % str(message.paths))
            if message.paths == {}:
                #self.log("why don't you call come")
                return
            l = False
            for o in message.paths.values():
                if o != float("inf"):
                    l = True
                    break
            if l:
                message.src = self
                message.dst = n #necessary?
                self.history[n] = message
                self.log("message for %s from %s" % (n, self))
                self.log("table: %s " % str(message.paths))
                self.send(message, self.ports[n])


