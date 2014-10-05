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
                self.forwarding_table[(source, dest)] = routing_table[dest]
                if (self, dest) not in self.forwarding_table:
                    self.forwarding_table[(self, dest)] = (routing_table[dest] + self.forwarding_table[(self, source)][0], source)
                else:
                    if self.forwarding_table[(self, dest)] < (routing_table[dest] + self.forwarding_table[(self, source)][0]):
                        self.forwarding_table[(self, dest)] = (routing_table[dest] + self.forwarding_table[(self, source)][0])
                    if self.forwarding_table[(self, dest)] == (routing_table[dest] + self.forwarding_table[(self, source)][0]):
                        portA = ports[self.forwarding_table[(self, dest)][1]]
                        portB = ports[port]
                        if portA > port:
                            self.forwarding_table[(self, dest)] = (routing_table[dest] + self.forwarding_table[(self, source)][0], self.forwarding_table[(self, source)][1])
            self.log("routing update packet")
            self.sendUpdate()

        else: # DATA PACKET
            if (self, packet.dst) in self.forwarding_table.keys():
                if self.forwarding_table[(self, packet.dst)][0] > 50:
                    self.forwarding_table[(self, packet.dst)][0] = float("inf")
                    return
            if self.forwarding_table[(self, packet.dst)][1] == self:
                self.log("data packet")
                self.send(packet, self.ports[self.forwarding_table[(self, packet.dst)][1]])
            else: 
                out = self.forwarding[(self, packet.dst)][1]
                self.log("data packet")
                self.send(packet, self.ports[out])

    def sendUpdate (self):
        for a,b in self.ports.items():
            nbr = a
            message = RoutingUpdate()

            for x,y in self.forwarding_table.items():

                if x[0] == self:
                    if x[1] == nbr:
                        continue
                    if y[1] == nbr:
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
                                    continue
                        message.add_destination(x[1], y[0])
                        self.history[x[1]] = y[0]
            if message.paths == {}:
                return
            message.src = self
            message.dst = nbr 
            self.log("HISTORY TABLE %s" % str(self.history))
            self.log("FORWARDING TABLE %s" % str(self.forwarding_table))
            self.log("message for %s from %s: %s" % (nbr, self, str(message.paths)))
            self.send(message, b)


