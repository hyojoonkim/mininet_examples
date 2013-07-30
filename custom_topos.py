################################################################################
# Mininet Custom Topologies                                                    #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
################################################################################

from mininet.topo import Topo

class FatTree_basic( Topo ):
  def __init__(self):
    # Initialize topology
    Topo.__init__( self )

    # TODO


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

class FatTree_5sw( Topo ):
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
    s4 = self.addSwitch( 's4' )
    s5 = self.addSwitch( 's5' )

    # Add links
    self.addLink( h1, s1 )
    self.addLink( h2, s2 )
    self.addLink( h3, s3 )

    self.addLink( s4, s1 )
    self.addLink( s4, s2 )
    self.addLink( s4, s3 )

    self.addLink( s5, s1 )
    self.addLink( s5, s2 )
    self.addLink( s5, s3 )

topos = { 'fattree_5sw': ( lambda: FatTree_5sw() ), 'fattree_basic': ( lambda: FatTree_basic() ), 'clique_4sw' : ( lambda: Clique_4sw() )}
