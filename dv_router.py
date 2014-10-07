
from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        self.forwarding_table = {}
        self.ports = {}
        self.history = {}
        self.neighbors = {}
        pass

    def handle_rx (self, packet, port):
        # if discovery packet...
        #    record neighbors
        #    record best path to neighbor
        #    send updates to neighbors
        if isinstance(packet, DiscoveryPacket): # DISCOVERY PACKET
            if packet.is_link_up:
                self.neighbors[packet.src] = packet.latency # neighbor distance
                self.ports[packet.src] = port
                if (self, packet.src) in self.forwarding_table.keys(): # there's a path to that new neighbor already
                    if packet.latency < self.forwarding_table[(self, packet.src)][0]:
                        self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                        self.log("%s discovers %s" % (self, packet.src))
                        #self.log("%s trace: %s" % (packet.src, src(packet.trace)))
                        self.sendUpdate()
                        self.ports[packet.src] = port
                    elif packet.latency == self.forwarding_table[(self, packet.src)][0]:
                        portA = port
                        if self == self.forwarding_table[(self, packet.src)][1]:
                            portB = port #??? what...
                        else:
                            portB = self.ports[self.forwarding_table[(self, packet.src)][1]]
                        if portA < portB:
                            self.ports[packet.src] = port
                            self.forwarding_table[(self, packet.src)] = (self, packet.src)
                            self.log("%s discovers %s" % (self, packet.src))
                            self.sendUpdate()
                else:
                    self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                    self.log("%s discovers %s" % (self, packet.src))
                    #self.log("%s trace: %s" % (packet.src, str(packet.trace)))
                    self.sendUpdate()
            else: 
                for key in self.neighbors.keys():
                    self.forwarding_table[self, packet.dst] = (float("inf"), self)
                    self.neighbors[key] = float("inf")
                    if self.neighbors[key] < float("inf"):
                        print("LINK BREAKS; LINK BREAKS!!")
                self.ports = {key:value for key, value in self.ports.items() if key != packet.src}
                self.neighbors = {key:value for key, value in self. neighbors.items() if key != packet.src}
                self.sendUpdate() 


        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = packet.paths
            link_down = False
            changed = False
            source = packet.src
            for pkt, pt in self.ports.items():
                if pt == port:
                    source = pkt
                    continue
            for dest, dist in routing_table.items():
                self.forwarding_table[(source, dest)] = routing_table[dest]
                total = routing_table[dest] + self.forwarding_table[(self, source)][0]
                if self == dest:
                    if dist < self.forwarding_table[(self, source)][0]:
                        # self.log("dist %s self-source %s" % (dest, ))
                        self.forwarding_table[(self, source)] = (dist, self)
                        self.log("1st change")
                        changed = True
                    if dist > self.forwarding_table[(self, source)]:
                        self.log("does this ever happen and why")
                if (self, dest) not in self.forwarding_table:
                    self.forwarding_table[(self, dest)] = (total, source)
                    self.log("2nd change")
                    changed = True
                else:
                    if self.forwarding_table[(self, dest)][0] == total:
                        portB = port
                        portA = port
                        if self.ports.has_key(self.forwarding_table.has_key((self, dest))):
                            portA = port
                            portB = self.ports[self.forwarding_table[(self, dest)][1]]
                        if port < portB:
                            self.forwarding_table[(self, dest)] = (total, source)
                            self.log("3rd change")
                            changed = True
                            del self.ports[portB]

                    elif self.forwarding_table[(self, dest)][0] > total:
                        self.forwarding_table[(self, dest)] = (total, source)
                        self.log("4th change")
                        changed = True
            if changed:
                self.forwarding_table[(self, self)] = (0, self)
                self.log("%s updates %s with %s" % (source, self, str(routing_table)))
                self.log("%s forwarding_table now is %s" % (self, str(self.forwarding_table)))
                self.sendUpdate()

        # if data packet...
        #   look for path to destination
        #   if there's a path, send it, or drop if not
        else: # DATA PACKET
            self.log("%s trace: %s" % (packet.src, str(packet.trace)))
            self.log("packet.dest %s" % packet.dst)
            self.log("available paths %s" % str(self.forwarding_table))
            if packet.dst == self:
                return
            if (self, packet.dst) in self.forwarding_table.keys():
                if packet.dst in self.neighbors:
                    self.log("%s sends data to %s" % (self, self.ports[packet.dst]))
                    self.send(packet, self.ports[packet.dst])
                else:
                    if self.ports.has_key(self.forwarding_table[(self, packet.dst)][1]):
                        print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
                        self.send(packet, self.ports[self.forwarding_table[(self, packet.dst)][1]])
                    else:
                        self.send(packet, port, flood=True)

    # sending updates to neighbors...
    #   send if 1) path is not going through it 2) last sent message was not the same
    def sendUpdate (self):
        for neigh, dist in self.neighbors.items():
            message = RoutingUpdate()
            for x,y in self.forwarding_table.items():
                if x[0] == self: # only sending my row to neighbors
                    if neigh == y[1]: # number 1
                        continue # do i have to do poison reverse here?
                    elif dist != float("inf"):
                        message.add_destination(x[1], y[0])
                        new_dest = y[0]
            if self in message.paths.keys():
                message.paths = {key:value for key, value in message.paths.items() if key != self} # don't want to tell neighbors that your distance to yourself is 0
            if message.paths == {}:
                return
            message.src = self
            message.dst = neigh
            if dist != float("inf"):
                self.send(message, self.ports[neigh])
            else:
                print("SSSSSSSSSSSSSSSSSSSSSSSSSSS")
                for node in self.neighbors.keys():
                    self.send(message, node, flood=True)
