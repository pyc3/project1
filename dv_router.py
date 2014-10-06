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
                if (self, packet.src) in self.forwarding_table.keys(): # there's a path to that new neighbor already
                    if packet.latency < self.forwarding_table[(self, packet.src)][0]:
                        self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                        self.log("discovery packet")
                        self.sendUpdate()
                        self.ports[packet.src] = port
                    if packet.latency == self.forwarding_table[(self, packet.src)][0]:
                        portA = port
                        portB = self.ports[self.forwarding_table[(self, packet.src)][1]]
                        if portA < portB:
                            self.ports[packet.src] = port
                            self.forwarding_table[(self, packet.src)] = (self, packet.src)
                            self.log("discovery packet")
                            self.sendUpdate()
                else:
                    self.forwarding_table[(self, packet.src)] = (packet.latency, self)
            else: # link change or link down
                if packet.latency == float("inf"): # if link down
                    self.neighbors = {key:value for key, value in self.neighbors.items() if key != packet.src} # delete neighbor
                    self.ports = {key:value for key, value in self.ports.items() if key != packet.src} # delete port
                # reroute ftable, for both inf and link change
                total = packet.latency
                from = self
                for x,y in self.forwarding_table.items():
                    if x[1] == packet.src and x[0] != self: # cycle through column
                        col = y[0]
                        from = y[1]
                        #extra = self.neighbors[from] # is this the shortest way?????????
                        extra = self.forwarding_table[self, from][0]
                        if col + extra < total:
                            total = col + extra # new distance to dst, could still be infinity
                self.forwarding_table[(self, packet.src)] = (total, from)
                self.log("discovery packet")
                self.sendUpdate()

        # if routingupdate packet...
        #   update forwarding table if necessary
        #   if updated, send updates to neighbors
        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            routing_table = packet.paths # the update message from neighbor
            for pkt, pt in self.ports.items():
                if pt == port:
                    source = pkt
                    continue
            for dest in routing_table.keys(): # for each update message. self = B, dest = e, dist = 1
                # if my cost to packet.src + dist < my forwarding table cost
                if (self, dest) in self.forwarding_table.keys():
                    if self.forwarding_table[(self, packet.src)][0] + routing_table[dest] < self.forwarding_table[(self, dest)][0]:
                        self.forwarding_table[(self, dest)] = self.forwarding_table[(self, packet.src)][0] + routing_table[dest]
                    if self.forwarding_table[(self, packet.src)][0] + routing_table[dest] == self.forwarding_table[(self, dest)][0]:
                        portA = port
                        portB = self.ports[self.forwarding_table[(self, dest)][1]]
                        if portA < portB:
                            self.forwarding_table[(self, dest)] = self.forwarding_table[(self, packet.src)][0] + routing_table[dest]
                            self.log("routing update packet")
                            self.sendUpdate()
                else:
                    self.forwarding_table[(self, dest)] = self.forwarding_table[(self, packet.src)][0] + routing_table[dest]
                    self.log("routing update packet")
                    self.sendUpdate()


        # if data packet...
        #   look for path to destination
        #   if there's a path, send it, or drop if not
        else: # DATA PACKET
            if (self, packet.dst) in self.forwarding_table.keys() and self.forwarding_table[(self, packet.dst)][0] != float("inf"):#where to put 50?
                if packet.dst in neighbors:
                    self.send(packet, self.ports[packet.dst])
                else:
                    self.send(packet, self.ports[self.forwarding_table[(self, packet.dst)][1]])

    # sending updates to neighbors...
    #   send if 1) path is not going through it 2) last sent message was not the same
    def sendUpdate (self):
        for neigh, dist in neighbors:
            message = RoutingUpdate()

            for x,y in self.forwarding_table.items():
                for x[0] == self: # only sending my row to neighbors
                    if neigh == y[1]: # number 1
                        
                        continue # do i have to do poison reverse here?
                    else:
                        if x[1] in self.history:
                            if y[1] != self.history[x[1]]:
                                self.history[n] = self.forwarding_table[(self, n)]
                                message.add_destination(n, self.forwarding_table[(self, n)][0])
                        else:
                            self.history[n] = self.forwarding_table[(self, n)]
                            message.add_destination(n, self.forwarding_table[(self, n)][0])
            if message.paths == {}:
                return
            message.src = self
            message.dst = neigh
            #self.log("src %s and dst %s" % (message.src, message.dst))
            #self.log("HISTORY TABLE %s" % str(self.history))
            self.log("FORWARDING TABLE for %s: %s" % (nbr, str(self.forwarding_table)))
            self.log("message for %s from %s: %s" % (nbr, self, str(message.paths)))
            self.send(message, self.ports[neigh])


