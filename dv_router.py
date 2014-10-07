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
                        # self.log("self= %s packet for port= %s" % (self, self.forwarding_table[(self, packet.src)][1]))
                        # self.log("ports= %s" % str(self.ports))
                        # self.log("neighbors= %s" % str(self.neighbors))
                        if self == self.forwarding_table[(self, packet.src)][1]:
                            portB = port #??? what...
                        else:
                            portB = self.ports[self.forwarding_table[(self, packet.src)][1]]
                        if portA < portB:
                            self.ports[packet.src] = port
                            self.forwarding_table[(self, packet.src)] = (self, packet.src)
                            self.log("%s discovers %s" % (self, packet.src))
                            #self.log("%s trace: %s" % (packet.src, src(packet.trace))) ###
                            self.sendUpdate()
                else:
                    self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                    self.log("%s discovers %s" % (self, packet.src))
                    #self.log("%s trace: %s" % (packet.src, str(packet.trace)))
                    self.sendUpdate()
            else: 
                if packet.latency == float("inf"): # if link down
                    self.neighbors = {key:value for key, value in self.neighbors.items() if key != packet.src} # delete neighbor
                    self.ports = {key:value for key, value in self.ports.items() if key != packet.src} # delete port
                    self.log("%s link to %s breaks" % (self, packet.src))
                    #todo = []
                    for a,b in self.forwarding_table.items(): # a[1] == someone who can get you to packet.src
                        if a[0] == self and b[1] == packet.src:
                            #todo.append(a[1]) # the destination i lost a connection to
                            self.forwarding_table[a] = (float("inf"), self)
                            self.log("%s forwarding table now %s" % (self, str(self.forwarding_table)))
                            self.sendUpdate()
                    # for item in todo: # look through all your neighbors ftables to see if they can reach that, they should have their shortest path to that
                    #     self.log("finding better path for %s" % item)
                    #     best = float("inf")
                    #     nToSrc = float("inf")
                    #     fromwho = self
                    #     for i in self.neighbors:
                    #         ftable = i.forwarding_table
                    #         #self.log("ftable %s" % str(ftable))
                    #         for k,v in ftable.items():
                    #             if k[0] == i: # just want to inspect their row of their forwarding table
                    #                 #self.log("k[1]=%s and packet.src=%s" % (k[1], packet.src))
                    #                 # if v[1] == self:
                    #                 #     #~~~~~RECURSION~~~~~~ FUCK THIS
                    #                 #     # look for next best path by inspecting ITS neighbors
                    #                 #     theirneighbors = i.neighbors
                    #                 #     best1 = float("inf")
                    #                 #     nToSrc1 = float("inf")
                    #                 #     fromwho1 = i
                    #                 #     for nbr in theirneighbors:
                    #                 #         if isinstance(nbr, DVRouter):
                    #                 #             neightable = nbr.forwarding_table
                    #                 #             for q,r in neightable.items():
                    #                 #                 if q[0] == nbr:
                    #                 #                     if q[1] == packet.src and r[1] != nbr:
                    #                 #                         nToSrc1 = r[0]
                    #                 #             if nToSrc1 == float("inf"):
                    #                 #                 continue
                    #                 #             elif nToSrc1 + theirneighbors[nbr] < best1:
                    #                 #                 best1 = nToSrc1 + theirneighbors[nbr]
                    #                 #                 fromwho1 = nbr
                    #                 #             elif nToSrc1 + theirneighbors[nbr] == best1:
                    #                 #                 porta = i.ports[nbr]
                    #                 #                 portb = i.ports[fromwho1]
                    #                 #                 if porta < portb:
                    #                 #                     fromwho1 = nbr
                    #                 #     #i.forwarding_table[(i, packet.src)] = (best1, fromwho1)
                    #                 #     #self.log("nbr %s ftable now %s" % (i, str(i.forwarding_table)))
                    #                 #     if best1 != float("inf"):
                    #                 #         self.forwarding_table[(self, packet.src)] = (best1, i)
                    #                 # if k[1] == packet.src and v[1] != self: # if neighbor to neighbor, nToSrc will be 0
                    #                 #     nToSrc = v[0]
                    #                     #self.log("%s has path to %s through %s for %s" % (i, packet.src, v[1], nToSrc))
                    #                     #self.log("nToSrc=%s" % nToSrc)
                    #         # if k[1] == i:
                    #         #     best = self.neighbors[i]
                    #         if nToSrc == float("inf"):
                    #             self.log("inf?")
                    #             continue
                    #         elif nToSrc + self.neighbors[i] < best:
                    #             #self.log("%s to %s originally %s. better is %s through %s" % (self, packet.src, best, nToSrc + self.neighbors[i], i))
                    #             best = nToSrc + self.neighbors[i]
                    #             fromwho = i
                    #         elif nToSrc + self.neighbors[i] == best:
                    #             #self.log("%s to %s same through %s" % (self, packet.src, i))
                    #             portA = self.ports[i]
                    #             portB = self.ports[fromwho]
                    #             if portA < portB:
                    #                 fromwho = i 
                        # self.forwarding_table[(self, packet.src)] = (best, fromwho)
                        # self.log("%s forwarding table now %s" % (self, str(self.forwarding_table)))
                        # self.sendUpdate()
                        # for c,d in self.forwarding_table.items():
                        #     if c[1] == item and c[0] != self:
                        #         self.log("did it get here") # shoud consider equal here
                        #         self.log("%s other values %s for c[1] %s" % (best, str(self.forwarding_table[(self, c[1])][0]), c[1]))
                        #         if best > self.forwarding_table[(self, c[1])][0]:
                        #             self.log("what about here best %s other values %s for c[1] %s" % (best, str(self.forwarding_table[(self, c[1])][0])), c[1])
                        #             best = self.forwarding_table[(self, c[1])][0]
                        #             fromwho = self.forwarding_table[(self, c[1])][1]
                        #         elif best == self.forwarding_table[(self, c[1])][0]:
                        #             if best == float("inf"):
                        #                 continue
                        #             portA = self.ports[fromwho]
                        #             portB = self.ports[self.forwarding_table[(self, c[1])][1]]
                        #             if portA > portB:
                        #                 best = self.forwarding_table[(self, c[1])][0]
                        #                 fromwho = self.forwarding_table[(self, c[1])][1]
                    # self.forwarding_table[(self, packet.src)] = (best, fromwho)
                    # self.log("%s forwarding table now %s" % (self, str(self.forwarding_table)))
                    # self.log("%s link to %s breaks" % (self, packet.src))
                    # self.sendUpdate()
                else: # if link change
                    for x,y in self.forwarding_table.items(): # reroutes things that went through packet.src
                        if y[1] == packet.src:
                            best = packet.latency
                            fromwho = packet.src
                            portA = port
                            for a,b in self.forwarding_table.items():
                                if x[1] == a[1]: # what if b[0] == self.forwarding_table[(self, a[0])][0] ?? no change
                                    if b[0] + self.forwarding_table[(self, a[0])][0] < best: # won't ever be equal to infinity
                                        best = b[0] + self.forwarding_table[(self, a[0])][0]
                                        fromwho = self.forwarding_table[(self, a[0])][1]
                                    if b[0] + self.forwarding_table[(self, a[0])][0] == best: 
                                        portB = self.ports[self.forwarding_table[(self, a[0])][1]]
                                        if portB < portA:
                                            best = b[0] + self.forwarding_table[(self, a[0])][0]
                                            fromwho = self.forwarding_table[(self, a[0])][1]
                    self.forwarding_table[(self, packet.src)] = (best, fromwho)
                    self.log("%s link to %s changed to %s" % (self, packet.src, best))
                    self.sendUpdate()

        # if routingupdate packet...
        #   update forwarding table if necessary
        #   if updated, send updates to neighbors
        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = packet.paths
            changed = False
            for pkt, pt in self.ports.items():
                if pt == port:
                    source = pkt
                    continue
            for dest, dist in routing_table.items():
                self.forwarding_table[(source, dest)] = routing_table[dest]
                total = routing_table[dest] + self.forwarding_table[(self, source)][0]
                if dist == float("inf"):
                    for f,t in self.forwarding_table.items():
                        if f[0] == self and f[1] == dest:
                            if t[0] != float("inf"): # thought the link was up
                                self.forwarding_table[(self, dest)] = (float("inf"), self)
                                change = True
                else:
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
                            portA = port
                            if self.forwarding_table[(self, dest)][0] == float("inf"):
                                self.log("is this infinity %s" % str(self.forwarding_table[(self, dest)][0]))
                            portB = self.ports[self.forwarding_table[(self, dest)][1]]
                            if port < portB:
                                self.forwarding_table[(self, dest)] = (total, source)
                                self.log("3rd change")
                                changed = True

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
            if (self, packet.dst) in self.forwarding_table.keys() and self.forwarding_table[(self, packet.dst)][0] != float("inf"):#where to put 50?
                if packet.dst in self.neighbors:
                    self.log("%s sends data to %s" % (self, self.ports[packet.dst]))
                    self.send(packet, self.ports[packet.dst])
                else:
                    self.log("%s sends data to %s" % (self, self.ports[self.forwarding_table[(self, packet.dst)][1]]))
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
                        # if x[1] in self.history:
                        #     #self.log("in history y[0]= %s and history[x[1]]= %s" % (y[0], self.history[x[1]]))
                        #     if y[0] != self.history[x[1]]:
                        #         self.history[x[1]] = y[0]
                        #         message.add_destination(x[1], y[0])
                        # else:
                        #     #self.log("not in history")
                        #     self.history[x[1]] = y[0]
                        message.add_destination(x[1], y[0])
            if self in message.paths.keys():
                message.paths = {key:value for key, value in message.paths.items() if key != self} # don't want to tell neighbors that your distance to yourself is 0
            if message.paths == {}:
                #self.log("pass by here?")
                return
            message.src = self
            message.dst = neigh
            #self.log("src %s and dst %s" % (message.src, message.dst))
            # self.log("HISTORY TABLE %s" % str(self.history))
            #self.log("FORWARDING TABLE %s" % str(self.forwarding_table))
            self.log("message for %s from %s: %s" % (neigh, self, str(message.paths)))
            self.send(message, self.ports[neigh])


