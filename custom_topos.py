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

    s1 = self.addSwitch( 's1' )
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


##### Topologies #####
topos = { 'fattree_2_3_1': ( lambda: Fattree_general(2,3,1) ),          \
          'clique_4sw' : ( lambda: Clique_4sw() ),           \
          'clique_3sw' : ( lambda: Clique_3sw() ),           \
          'server_lb' : ( lambda: Server_LB() ),             \
          'fattree_1_2_2' : ( lambda: Fattree_general(1,2,2) ),             \
          'fattree_2_5_1' : ( lambda: Fattree_general(2,5,1) ) }
