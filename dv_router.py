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
                        self.log("discovery packet")
                        self.sendUpdate()
                        self.ports[packet.src] = port
                    if packet.latency == self.forwarding_table[(self, packet.src)][0]:
                        portA = port
                        self.log("self= %s packet for port= %s" % (self, self.forwarding_table[(self, packet.src)][1]))
                        self.log("ports= %s" % str(self.ports))
                        self.log("neighbors= %s" % str(self.neighbors))
                        if self == self.forwarding_table[(self, packet.src)][1]:
                            portB = port #??? what...
                        else:
                            portB = self.ports[self.forwarding_table[(self, packet.src)][1]]
                        if portA < portB:
                            self.ports[packet.src] = port
                            self.forwarding_table[(self, packet.src)] = (self, packet.src)
                            self.log("discovery packet")
                            self.sendUpdate()
                else:
                    self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                    self.log("discovery packet")
                    self.sendUpdate()
            else: # link change or link down
                if packet.latency == float("inf"): # if link down
                    self.neighbors = {key:value for key, value in self.neighbors.items() if key != packet.src} # delete neighbor
                    self.ports = {key:value for key, value in self.ports.items() if key != packet.src} # delete port
                # reroute ftable, for both inf and link change
                total = packet.latency
                from0 = self
                for x,y in self.forwarding_table.items():
                    if x[1] == packet.src and x[0] != self: # cycle through column
                        col = y[0]
                        from0 = y[1]
                        #extra = self.neighbors[from] # is this the shortest way?????????
                        extra = self.forwarding_table[self, from0][0]
                        if col + extra < total:
                            total = col + extra # new distance to dst, could still be infinity
                self.forwarding_table[(self, packet.src)] = (total, from0)
                self.log("discovery packet")
                self.sendUpdate()

        # if routingupdate packet...
        #   update forwarding table if necessary
        #   if updated, send updates to neighbors
        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = packet.paths
            for pkt, pt in self.ports.items():
                if pt == port:
                    source = pkt
                    continue
            for dest in routing_table.keys():
                # if dest is a neighbor, continue
                # neighbors = []
                # for m,n in self.forwarding_table.items():
                #     if m[0] == self:
                #         if n[1] == self: # neighbor
                #             neighbors.append(m[1])
                # if dest in neighbors:
                #     self.log(" %s has these neighbors: %s" % (self, neighbors))
                #     self.log("yes no maybe so")
                #     continue
                self.forwarding_table[(source, dest)] = routing_table[dest]
                total = routing_table[dest] + self.forwarding_table[(self, source)][0]
                if self == dest:
                    #self.log("why.... when does this ever happen")
                    continue
                if (self, dest) not in self.forwarding_table:
                    # self.log("is this why")
                    self.forwarding_table[(self, dest)] = (total, source)
                    # self.log(" self, dest %s total %s source %s " % (str(self.forwarding_table[(self, dest)]), total, source))
                    #self.log("fsdlmskl %s" % str(self.forwarding_table[(self, dest)]))
                else: # need to have lowest hop recorded / neighbors -- lowest though?
                    #self.log("how about this")
                    # self.log(" how are they diff %s %s" % (str(self.forwarding_table[(self, dest)][0]), total))
                    if self.forwarding_table[(self, dest)][0] == total:
                        # self.log("second")
                        #self.log("equality")
                        if self.forwarding_table[(self, dest)][1] in self.ports.keys():
                            # self.log("thirdddd")
                            portA = self.ports[self.forwarding_table[(self, dest)][1]]
                            portB = port
                            for x,y in self.ports.items():
                                if y == portA:
                                    srcA = x
                                if y == portB:
                                    srcB = x
                            if portB < portA:  #??
                                src = srcB
                            else:
                                src = srcA
                            #self.log("src %s" % src)
                            self.forwarding_table[(self, dest)] = (total, src)
                    elif self.forwarding_table[(self, dest)][0] < total:
                        # self.log("first")
                        self.forwarding_table[(self, dest)] = (total, source)
            self.log("routing update packet")
            self.sendUpdate()

        # if data packet...
        #   look for path to destination
        #   if there's a path, send it, or drop if not
        else: # DATA PACKET
            self.log("data packet")
            self.log("packet.dest %s" % packet.dst)
            self.log("available paths %s" % str(self.forwarding_table))
            if (self, packet.dst) in self.forwarding_table.keys() and self.forwarding_table[(self, packet.dst)][0] != float("inf"):#where to put 50?
                if packet.dst in self.neighbors:
                    self.send(packet, self.ports[packet.dst])
                else:
                    self.send(packet, self.ports[self.forwarding_table[(self, packet.dst)][1]])

    # sending updates to neighbors...
    #   send if 1) path is not going through it 2) last sent message was not the same
    def sendUpdate (self):
        for neigh, dist in self.neighbors.items():
            message = RoutingUpdate()

            for x,y in self.forwarding_table.items():
                if x[0] == self: # only sending my row to neighbors
                    if neigh == y[1]: # number 1
                        
                        continue # do i have to do poison reverse here?
                    else:
                        if x[1] in self.history:
                            self.log("in history")
                            if y[0] != self.history[x[1]]:
                                self.history[x[1]] = y[0]
                                message.add_destination(x[1], y[0])
                        else:
                            self.log("not in history")
                            self.history[x[1]] = y[0]
                            message.add_destination(x[1], y[0])
            if message.paths == {}:
                self.log("pass by here?")
                return
            message.src = self
            message.dst = neigh
            #self.log("src %s and dst %s" % (message.src, message.dst))
            #self.log("HISTORY TABLE %s" % str(self.history))
            self.log("FORWARDING TABLE for %s" % str(self.forwarding_table))
            self.log("message for %s from %s: %s" % (neigh, self, str(message.paths)))
            self.send(message, self.ports[neigh])


