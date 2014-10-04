from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity): # only hosts and dvrouters
    def __init__(self):
        self.neighbors = {} # check through_who when deciding what to routeupdate them, for the extra 10 points, {A:1, B:2}
        self.forwarding_table = {} # example forwarding table: {(A,1) : C, (B,2) : D, (dest,cost) : through_who}
        # {((from, dest): (distance, from who))}, example: {(a, b):(2, a)}
        self.history = {} # keep history of what you've sent each of your neighbors (HINT HINT) {neighbor: last sent, neighbor1: last sent}
        self.ports = {} # keep track of which ports link to which neighbors, from discovery packet {neighbor: port#, neighbor1: port1#}
        pass

    def handle_rx (self, packet, port):

        # routing updates could be diff for diff neighbors, store routing updates as {(a, b):(2, a)}

        # DISCOVERY PACKET
        if isinstance(packet, DiscoveryPacket):



            # know where the links/ports are
            # OR know when a link is down
            # OR know when a link cost has changed
            if packet.is_link_up: # no need to differentiate?
                # LINK DOWN
                if packet.latency == float("inf"):
                    # assuming it was already up
                    self.neighbors[packet.src] = packet.latency
                    self.fowarding_table[(packet.dst, packet.latency)] = packet.src
                    # send routing updates to relevant neighbors
                    ##

                # LINK COST CHANGE
                if packet in self.neighbors:
                    self.neighbors[packet.src] = packet.latency
                    self.fowarding_table[(packet.dst, packet.latency)] = packet.src
                    # change forwarding table too
                    # send routing update to RELEVANT neighbors (not through one who told you)

                # LINK UP
                # test
                print 'discovery packet DISCOVERED :D :D'
                self.ports[packet.src] = port # add which neighbors are reachable from which port
                self.neighbors[packet.src] = packet.latency # distance to neighbors
                self.forwarding_table[(self, packet.src)] = (packet.latency, self)
                for x in len(self.neighbors.keys()):
                    message = reRoute(x, packet, forwarding_table, neighbors) # a routingupdate

                # check if path goes through neighbor you're thinking of sending it to
                for x in self.neighbors.keys():
                    message = RoutingUpdate()
                    if x in self.history: # check if you already sent the exact same thing / unnecessary
                        old_message = self.history[x] # or should i put this in the other loop below and remove if i've sent this before? hard to remove from tuple...
                    for y in self.forwarding_table.values() & f in self.forwarding_tables.keys():
                        if x != y:
                            message.add_destination(f[0], f[1])
                    send(message, self.ports[x], False)
                    self.history[x] = message
                

            return

        elif isinstance(packet, RoutingUpdate):
            routing_table = RoutingUpdate.paths # am i allowed to do this?
            for a in routing_table.values() and b in routing_table.keys(): # can i do this?
                if a == 0: # routing update doesn't give you source?
                    source = b
            for x in routing_table.keys():
                forwarding_table[(self, source)] = routing_table[]
            return

        else: # DATA PACKET
            if (self, packet.dst) in forwarding_table.keys():
                values = forwarding_table[(self, packet.dst)]
                if values[1] != self:
                    self.send(packet, ports[values[1]])
                else:
                    self.send(packet, ports[packet.dst])
            # else: drop the packet! (just don't send)



    # ROUTING UPDATE PACKET -- sending update to all your neighbors, not a path at all
    # routing update comes in...
    # update forwarding table
#      if isinstance(packet, RoutingUpdate):
    # my_paths = packet.str_routing_table
    # # can it send an update to me about it's changed length from me?
    # # mydtoyou ...
    # distance_to_dvrouter = packet.get_distance(self) # has to exist right?
    # # if MYDTOYOU + YOURDTOSOMETHING < MYDTOSOMETHING, change my routing table
    # for x in packet.all_dests():
    #   if x in self.routing_table:
#                  # already have data in routing table...
#                  if distance_to_dvrouter + my_paths[x] < self.routing_table[x]:
#                      # change routing table
#                      self.routing_table[x] = my_paths[x]
    #   # something doesn't exist in my routing table...
    #   else: 
    #       self.routing_table[x] = my_paths[x]
    #   # what happens if the new routing table has a link disappear?
#          return
            
#      # DATA PACKET
#      # find out where packet wants to go
#      # check forwarding table for shortest path
#      if isinstance(packet, Ping):
    # # do i need to know the source of this packet?
    # dest = packet.dst 
    # print 'i got a data packet!!! :D'
    # # 1) check if there's direct path
    # # 2) use routing table to route packet
    # # start with closest neighbor
    # for x in xrange(len(self.routing_table)):
    #   # need to set things in the routing table before trying to test this.... dumbass
    #   if (x[0] == self) & (x[1] == dest):
    #       print 'sent it to mah neighbor ^___^V'
    #       send(packet, port) # does it matter what port you send packets out of? do i need to input a third parameter or will it be automatic?
                
#          return

# drop data packet if you don't have a route for it


        #raise NotImplementedError