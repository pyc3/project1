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
        pass

    def handle_rx (self, packet, port):
        if isinstance(packet, DiscoveryPacket): # DISCOVERY PACKET
            if packet.is_link_up:
                best = packet.latency
                from_who = self
                for x,y in self.forwarding_table.items():
                    if x[1] == packet.src and x[0] != self:
                        if best > y:
                            best = y
                            from_who = x[0]
                self.forwarding_table[(self, packet.src)] = (best, from_who)
                self.ports[packet.src] = port
            else:
                if self.forwarding_table[(self, packet.src)][0] > packet.latency:
                    self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                else:
                    best = packet.latency
                    from_who = self
                    for x,y in self.forwarding_table.items():
                        if x[1] == packet.src and x[0] != self:
                            if best > y:
                                #self.log("waahh2")
                                best = y
                                from_who = x[0]
                    if best == float("inf"):
                        self.ports = {key:value for key, value in self.ports.items() if value != port}
                    self.forwarding_table[(self, packet.src)] = (best, from_who)
            self.log("discovery packet")
            self.sendUpdate()

        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = packet.paths
            for pkt, pt in self.ports.items():
                if pt == port:
                    source = pkt
                    continue
            for dest in routing_table.keys():
                # if dest is a neighbor, continue
                neighbors = []
                for m,n in self.forwarding_table.items():
                    if m[0] == self:
                        if n[1] == self: # neighbor
                            neighbors.append(m[1])
                if dest in neighbors:
                    self.log(" %s has these neighbors: %s" % (self, neighbors))
                    self.log("yes no maybe so")
                    continue
                self.forwarding_table[(source, dest)] = routing_table[dest]
                total = routing_table[dest] + self.forwarding_table[(self, source)][0]
                if (self, dest) not in self.forwarding_table:
                    self.log("is this why")
                    self.forwarding_table[(self, dest)] = (total, source)
                    self.log(" self, dest %s total %s source %s " % (str(self.forwarding_table[(self, dest)]), total, source))
                    #self.log("fsdlmskl %s" % str(self.forwarding_table[(self, dest)]))
                else: # need to have lowest hop recorded / neighbors -- lowest though?
                    #self.log("how about this")
                    self.log(" how are they diff %s %s" % (str(self.forwarding_table[(self, dest)][0]), total))
                    if self.forwarding_table[(self, dest)][0] == total:
                        self.log("second")
                        #self.log("equality")
                        if self.forwarding_table[(self, dest)][1] in self.ports.keys():
                            self.log("thirdddd")
                            portA = self.ports[self.forwarding_table[(self, dest)][1]]
                            portB = port
                            for x,y in self.ports.items():
                                if y == portA:
                                    srcA = x
                                if y == portB:
                                    srcB = x
                            if portB < portA:
                                src = srcB
                            else:
                                src = srcA
                            #self.log("src %s" % src)
                            self.forwarding_table[(self, dest)] = (total, src)
                    elif self.forwarding_table[(self, dest)][0] < total:
                        self.log("first")
                        self.forwarding_table[(self, dest)] = (total, source)
            self.log("routing update packet")
            self.sendUpdate()

        else: # DATA PACKET
            # self.log("packet latency: %s" % self.forwarding_table[(self, packet.dst)][0])
            self.log("packet dest %s" % packet.dst)
            self.log("available paths %s" % str(self.forwarding_table))
            if (self, packet.dst) in self.forwarding_table.keys():
                if self.forwarding_table[(self, packet.dst)][0] > 50:
                    self.forwarding_table[(self, packet.dst)] = (float("inf"), self.forwarding_table[(self, packet.dst)][1]) #
                    for y in self.ports.values():
                        if y == packet.dst:
                            self.ports = {key:value for key, value in self.ports.items() if key != packet.dst}
                    return
            if self.forwarding_table[(self, packet.dst)][1] == self:
                self.log("data packet")
                self.send(packet, self.ports[self.forwarding_table[(self, packet.dst)][1]])
            else: 
                out = self.forwarding_table[(self, packet.dst)][1]
                self.log("data packet")
                self.send(packet, self.ports[out])

    def sendUpdate (self):
        for a,b in self.ports.items():
            nbr = a
            message = RoutingUpdate()

            for x,y in self.forwarding_table.items():
                #self.log("x= %s y= %s" % (x,y))
                if x[0] == self:
                    if x[1] == nbr:
                        #self.log("doesn't this stop it")
                        continue
                    if y[1] == nbr: # this is false (nbr=dv2, basichost1): (2, y[1]=dv2)
                        #self.log("for %s y[1]= %s x[0]= %s" % (nbr, y[1], self))
                        if self.history != {}:
                            if x[1] in self.history:
                                if self.history[x[1]] == float("inf"):
                                    continue
                        message.add_destination(x[1], float("inf")) # poison reverse
                        self.history[x[1]] = float("inf")
                    else:
                        if self.history != {}:
                            if x[1] in self.history:
                                if self.history[x[1]] == y[0]:
                                    #self.log("shoud continue?")
                                    continue
                        message.add_destination(x[1], y[0])
                        self.history[x[1]] = y[0]
            if message.paths == {}:
                return
            message.src = self
            message.dst = nbr 
            #self.log("src %s and dst %s" % (message.src, message.dst))
            #self.log("HISTORY TABLE %s" % str(self.history))
            self.log("FORWARDING TABLE for %s: %s" % (nbr, str(self.forwarding_table)))
            self.log("message for %s from %s: %s" % (nbr, self, str(message.paths)))
            self.send(message, b)


