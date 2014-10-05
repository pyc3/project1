from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity): # only hosts and dvrouters
    def __init__(self):
        #self.neighbors = {}
        self.forwarding_table = {}
        self.ports = {}
        self.history = {}
        pass

    def handle_rx (self, packet, port):
        if isinstance(packet, DiscoveryPacket): # DISCOVERY PACKET
            # use is_link_up!!!!!!! @_@)R@#$@#$
            # link up
            # add neighbor, add forwarding table entry, add port
            # send update
            if packet.is_link_up: # link up
                #self.neighbors[packet.src] = packet.latency
                best = packet.latency
                from_who = self #
                for x,y in self.forwarding_table.items():
                    if x[1] == packet.src and x[0] != self:
                        #self.log("why")
                        if best > y:
                            #self.log("wahhhh")
                            best = y
                            from_who = x[0]#
                self.forwarding_table[(self, packet.src)] = (best, from_who)
                #self.log("from whooo %s" % from_who)
                #self.log("forwardingggg %s" % str(self.forwarding_table))
                #self.forwarding_table[(self, packet.src)] = (packet.latency, self) # not necessarily!
                self.ports[packet.src] = port
            else: # link down OR link cost change
                #self.neighbors[packet.src] = packet.latency
                # link cost change is good
                if self.forwarding_table[(self, packet.src)][0] > packet.latency:
                    self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                else: # link cost change is bad/ link goes down (infinity)
                    best = packet.latency
                    from_who = self
                    for x,y in self.forwarding_table.items():
                        if x[1] == packet.src and x[0] != self:
                            if best > y:
                                #self.log("waahh2")
                                best = y
                                from_who = x[0]
                    if best == float("inf"):
                        #self.log("float infininityytytiyi")
                        self.ports = {key:value for key, value in self.ports.items() if value != port}
                        #self.log("%s" % str(self.ports))
                    #self.log("%s %s" % (best, from_who))
                    self.forwarding_table[(self, packet.src)] = (best, from_who)
            self.log("discovery packet")
            self.sendUpdate()

        elif isinstance(packet, RoutingUpdate): # ROUTING UPDATE PACKET
            # update their row of forwarding table
            routing_table = packet.paths
            for pkt, pt in self.ports.items():
                if pt == port:
                    source = pkt
                    continue
            for dest in routing_table.keys():
                self.forwarding_table[(source, dest)] = routing_table[dest]
                # update my row of forwarding table
                if (self, dest) not in self.forwarding_table: # if not in forwarding table
                    # best = (routing_table[dest] + self.forwarding_table[(self, source)][0], self.forwarding_table[(self, source)][1])
                    # from_who = 
                    # for x,y in self.forwarding_table.items():
                    #     if x[1] == packet.src and x[0] != self:
                    #         if best > y[0]:
                    #             best = y[0]
                    #             from_who = y[1]
                    # self.forwarding_table[(self, packet.src)] = (best, from_who)
                    # is there another path?
                    # if latency is infinity, do i want to add?
                    #self.log("before routing: %s" % str(self.forwarding_table))
                    # if dest == source:
                    #     self.log("IS THIS IT GODDAMNIT")
                        #self.forwarding_table[(self, dest)] = (routing_table[dest])
                    self.forwarding_table[(self, dest)] = (routing_table[dest] + self.forwarding_table[(self, source)][0], source)
                    #self.log("AFTER routing: %s" % str(self.forwarding_table))
                else: # if it's in the forwarding table
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
                    self.forwarding_table[(self, packet.dst)][0] = float("inf") # drop link
                    return
            if self.forwarding_table[(self, packet.dst)][1] == self: # send to direct neighbor
                self.log("data packet")
                self.send(packet, self.ports[self.forwarding_table[(self, packet.dst)][1]])
            else: 
                out = self.forwarding[(self, packet.dst)][1]
                self.log("data packet")
                self.send(packet, self.ports[out])

            # if there's a path to dst, take it -- look in forwarding table, not neighbors
            # if not, drop
            # to send, beware of ports. if direct neighbor, ports[neighbor]. if indirect route, ports[neighbor to indirect]

    # send specialized routingupdate() to each neighbor
    # don't send neighbor a path through neighbor
    # don't send redundant information
    # don't send direct neighbor your distance to it
    def sendUpdate (self):
        for a,b in self.ports.items(): #neighbors
        #for n in self.forwarding_table.keys(): # cycle through all my neighbors
            nbr = a
            message = RoutingUpdate()
            # if self.forwarding_table[(self, nbr)] == float("inf"): # link went down/unreachable neighbor
            #     continue
            # else:

            for x,y in self.forwarding_table.items():

                if x[0] == self: #only send your row
                    #self.log("forwarding table %s" % str(self.forwarding_table))
                    #self.log("from who??? %s" % y[1])
                    if x[1] == nbr: # req3
                        continue
                    if y[1] == nbr: # req1
                        #self.log("isnt it supposed to come here")
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
            #self.log("beforeee: %s" % str(message.paths))
            # req2 - history can't just be last routingupdate()
            # has to be another forwarding table ><
            # if self.history != {}: # not empty history
            #     for p,q in self.history.items():
            #         # self.log("myhistory= %s" % str(self.history))
            #         # self.log("myftable= %s" % str(self.forwarding_table))
            #         # self.log("p %s" % str(p))
            #         #self.log("message get %s" % message.get_distance(p[1]))


            #         if p[1] in message.paths.keys():
            #             if p == self:
            #                 if message.get_distance(p[1]) == q[0]:
            #                     message.paths = {key:value for key, value in message.paths.items() if key != p}
            #             else:
            #                 if message.get_distance(p[1]) == q:
            #                     message.paths = {key:value for key, value in message.paths.items() if key != p}
            #self.log("afterrr: %s" % str(message.paths))    

            # if nbr in self.history.keys():
            #     oldrouting_table = self.history[nbr].paths
            #     for p in oldrouting_table.keys():
            #         if message.get_distance(p) == oldrouting_table[p]:
            #             message.paths = {key:value for key, value in message.paths.items() if key != p}
            if message.paths == {}:
                #self.log("???")
                return
            # l = False
            # for o in message.paths.values():
            #     if o != float("inf"):
            #         l = True
            #         break
            # if l:
            message.src = self
            message.dst = nbr #necessary?
            #self.history = {}
            # self.log("message paths %s" % message.paths)
            # for dest, dist in message.paths:
            #     self.history[dest] = dist
            self.log("HISTORY TABLE %s" % str(self.history))
            self.log("FORWARDING TABLE %s" % str(self.forwarding_table))
            self.log("message for %s from %s" % (nbr, self))
            self.log("table: %s " % str(message.paths))
            self.send(message, b)


