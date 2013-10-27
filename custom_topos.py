################################################################################
# Mininet Custom Topologies                                                    #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
################################################################################

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController   
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
import math


#######################################################
# $ sudo mn --controller=remote,ip=127.0.0.1 --custom ./custom_topos.py 
#           --topo fattree_three --arp --mac --link=tc
#######################################################


class Clique_3sw( Topo ):
  def __init__(self):
    # Initialize topology
    Topo.__init__( self )

    # Add hosts and switches
    h1 = self.addHost( 'h1' )
    h2 = self.addHost( 'h2' )
    h3 = self.addHost( 'h3' )

    s1 = self.addSwitch( 's1' )
    s2 = self.addSwitch( 's2' )
    s3 = self.addSwitch( 's3' )

    # Add links
    self.addLink( h1, s1 )
    self.addLink( h2, s2 )
    self.addLink( h3, s3 )

    for i in range(3):
      for j in range(2):
        if (i+1)<(j+2):
          if i==1 and j==3:
            self.addLink ( 's%s'%(i+1), 's%s'%(j+2), delay='100ms')
          self.addLink ( 's%s'%(i+1), 's%s'%(j+2))


class Clique_4sw( Topo ):
  def __init__(self):
    # Initialize topology
    Topo.__init__( self )

    # Add hosts and switches
    h1 = self.addHost( 'h1' )
    h2 = self.addHost( 'h2' )
    h3 = self.addHost( 'h3' )
    h4 = self.addHost( 'h4' )

    s1 = self.addSwitch( 's1' )
    s2 = self.addSwitch( 's2' )
    s3 = self.addSwitch( 's3' )
    s4 = self.addSwitch( 's4' )

    # Add links
    self.addLink( h1, s1 )
    self.addLink( h2, s2 )
    self.addLink( h3, s3 )
    self.addLink( h4, s4 )

    for i in range(4):
      for j in range(3):
        if (i+1)<(j+2):
          self.addLink ( 's%s'%(i+1), 's%s'%(j+2))

class Server_LB( Topo ):
  def __init__(self):
    # Initialize topology
    Topo.__init__( self )

    # Add hosts and switches
    h1 = self.addHost( 'h1' )
    h2 = self.addHost( 'h2' )
    h3 = self.addHost( 'h3' )
    h4 = self.addHost( 'h4' )

    s1 = self.addSwitch( 's1',dpid='0000000000001111' )
    s2 = self.addSwitch( 's2' )
    s3 = self.addSwitch( 's3' )

    # Add links
    self.addLink( h1, s1 )
    self.addLink( h2, s2 )
    self.addLink( h3, s2, delay='100ms')
    self.addLink( h4, s3 )
    
    self.addLink( s1, s2 )
    self.addLink( s2, s3)

class Fattree_general( Topo ):
  def __init__(self, top, bottom, hostfanout):
    Topo.__init__(self)

    top_switches = []  
    bottom_switches = []  
    host_machines = []

    # Create top switches
    for s in range(top):
      top_switches.append(self.addSwitch( 's%s'%(s+1) ))

    # Create bottom switches and hosts
    for s in range(bottom):
      bottom_switches.append(self.addSwitch( 's%s'%(s+1+top) ))

      # Host creation
      for h in range(hostfanout):
        host_machines.append(self.addHost( 'h%s'%(h+1+s*hostfanout) ))

    # Wiring of top and bottom, bottom and hosts
    for idx,b in enumerate(bottom_switches):
      for t in top_switches:
        self.addLink ( b, t )

      # Wiring hosts and bottom switches
      for h in range(hostfanout):
        if (h + idx*hostfanout+1)%2 != 0:
          self.addLink( host_machines[h + idx*hostfanout], b )
        else:
          self.addLink( host_machines[h + idx*hostfanout], b, delay='100ms')

class Fattree_threelevel( Topo ):          
  def __init__(self, top, middle, bottom, hostfanout):
    Topo.__init__(self)

    top_switches = []  
    middle_switches = []  
    bottom_switches = []  
    host_machines = []

    # Create top switches
    for s in range(top):
      top_switches.append(self.addSwitch( 's%s'%(s+1) ))

    # Create middle switches and hosts
    for s in range(middle):
      middle_switches.append(self.addSwitch( 's%s'%(s+1+top) ))

    # Create bottom switches and hosts
    for s in range(bottom):
      bottom_switches.append(self.addSwitch( 's%s'%(s+1+top+middle) ))

      # Host creation
      for h in range(hostfanout):
        host_machines.append(self.addHost( 'h%s'%(h+1+s*hostfanout) ))

    # Wiring of top and middle
    for idx,m in enumerate(middle_switches):
      for t in top_switches:
        self.addLink ( m, t )

    # Wiring of middle and bottom, bottom and hosts
    for idx,b in enumerate(bottom_switches):
      for t in middle_switches:
        self.addLink ( b, t )

      # Wiring hosts and bottom switches
      for h in range(hostfanout):
        self.addLink( host_machines[h + idx*hostfanout], b )



class Alfares_FatTree( Topo ):
  def __init__(self, k):
    Topo.__init__(self)

    core_switches = []  
    aggr_switches = []  
    edge_switches = []  
    host_machines = []

    # Create core switches
    for s in range(k):
      core_switches.append(self.addSwitch( 's%s'%(s+1) ))

    number_of_aggr_switches = int(math.pow(k,2)/2)
    number_of_edge_switches = number_of_aggr_switches
    # Create aggregation switches
    for s in range(number_of_aggr_switches):
      aggr_switches.append(self.addSwitch( 's%s'%(s+k+1) ))

    # Create edge switches and hosts
    for s in range(number_of_edge_switches):
      edge_switches.append(self.addSwitch( 's%s'%(s+number_of_aggr_switches+k+1) ))

      # Host creation
      for h in range(k/2):
        host_machines.append(self.addHost( 'h%s'%(h+1+s*(k/2)) ))

    # Wiring of core and aggregation
    for idx1,core in enumerate(core_switches):
      for idx2,aggr in enumerate(aggr_switches):
        if idx2%k == idx1/2:
          self.addLink( aggr, core )

    # Wiring of aggregation and edge
    for aggr in aggr_switches:
      for edge in edge_switches:
        self.addLink ( edge, aggr )

    # Wiring hosts and edge switches
    for idx,edge in enumerate(edge_switches):
      for h in range(k/2):
        self.addLink( host_machines[h + idx*(k/2)], edge )

##### Topologies #####
topos = { 'fattree_2_3_1': ( lambda: Fattree_general(2,3,1) ),          \
#          'fattree_three' : ( lambda: Fattree_threelevel(1,5,72,24) ),           \
          'fattree_three' : ( lambda: Fattree_threelevel(1,2,3,2) ),           \
          'm_fattree' : ( lambda: Alfares_FatTree(4) ),           \
          'clique_4sw' : ( lambda: Clique_4sw() ),           \
          'clique_3sw' : ( lambda: Clique_3sw() ),           \
          'server_lb' : ( lambda: Server_LB() ),             \
          'fattree_1_2_2' : ( lambda: Fattree_general(1,2,2) ),             \
          'fattree_2_5_1' : ( lambda: Fattree_general(2,5,1) ) }
