#######################################################
# $ sudo python topo.py -r 1S -s 20 -t 60
#######################################################



from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController   
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
import time
import math
from optparse import OptionParser

from lib.custom_topos import Alfares_FatTree

class EventTopo(Topo):
  def __init__(self, kval, **opts):
    # Initialize topology and default options
    Topo.__init__(self, **opts)


    self.fattree_topo(top, middle, bottom, host_fanout)


  def linear_topo(self,num_hosts):
    # Create switches and hosts
    hosts = [ self.addHost( 'h%s' % h )
              for h in irange( 1, num_hosts ) ]
    switches = [ self.addSwitch( 's%s' % s )
              for s in irange( 1, num_hosts ) ]
  
    # Wire up switches
    last = None                
    for switch in switches:
      if last:
        self.addLink( last, switch )
      last = switch
  
    # Wire up hosts
    for host, switch in zip( hosts, switches ):
      self.addLink( host, switch )


  def fattree_topo(self,top, middle, bottom, hostfanout):
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
#        if (h + idx*hostfanout+1)%2 != 0:
#          self.addLink( host_machines[h + idx*hostfanout], b )
#        else:
#          self.addLink( host_machines[h + idx*hostfanout], b, delay='100ms')



def startpings( host, targetip, timeout, ping_interval):

# ' `ping %s -i %s -w %s -W 0.9 >> ./output/%s_%s`;' % (targetip.IP(), str(ping_interval), str(timeout), host.IP(),targetip.IP()) + 


  # Simple ping loop
  cmd = ( 'while true; do '
          ' echo -n %s "->" %s ' % (host.IP(), targetip.IP()) + 
          ' `ping %s -i %s -w %s >> ./output/%s_%s`;' % (targetip.IP(), str(ping_interval), str(timeout), host.IP(),targetip.IP()) + 
          ' break;'
          'done &' )

  print ( '*** Host %s (%s) will be pinging IP: %s' %
          ( host.name, host.IP(), targetip.IP() ) )

  host.cmd( cmd )



def MakeTestBed_and_Test(kval, timeout, ping_interval):
  print "a. Firing up Mininet"
  net = Mininet(topo=Alfares_FatTree(kval), controller=lambda name: RemoteController( 'c0', '127.0.0.1' ), host=CPULimitedHost, link=TCLink)                                  
  net.start() 

  time.sleep(5)
  hosts = net.hosts

  # One ping from each host. Make the controller ready.
  for h1 in hosts:
    for h2 in hosts:
      if h1!=h2:
        h1.cmdPrint('ping', '-c3', str(h2.IP()))
#       pinghost = [h1,h2]
#       ping(pinghost)


  # Start pings
#  print "b. Starting continuous allpair ping"
#  for h1 in hosts:
#    for h2 in hosts:
#      if h1!=h2:
#        startpings(h1,h2, timeout, ping_interval)
#   
  # Wait
  time.sleep(timeout)

#  # Stop pings
#  print "c. Stopping pings"
#  for host in hosts:
#    host.cmd( 'kill %while' )
#
  # Stop mininit
  print "d. Stopping Mininet"
  net.stop()


def main():
  desc = ( 'Generate Mininet Testbed' )
  usage = ( '%prog [options]\n'
            '(type %prog -h for details)' )
  op = OptionParser( description=desc, usage=usage )

  ### Options
  op.add_option( '--rate', '-r', action="store", \
                 dest="rate", help = "Set rate. <n>S for (n/second), <n>M for (n/minute). Don't include the brackets when specifying n" )

  op.add_option( '--time', '-t', action="store", \
                 dest="timeout", help = "Specify the timeout in seconds." )
 
  op.add_option( '--kvalue', '-k', action="store", \
                 dest="kvalue", help = "K value for the folded clos topology." )


  ping_interval = 0.0
  options, args = op.parse_args()

  if options.rate is not None:
    if options.rate.endswith('S'):
      num_str = options.rate.rstrip('S')
      ping_interval = 1.0/float(num_str)
    elif options.rate.endswith('M'):
      num_str = options.rate.rstrip('M')
      ping_interval = 60.0/float(num_str)
    else:
      print 'Wrong rate format. Abort.'
      return
  else:
    print '\nNo rate given. Abort.\n'
    return

  # Set parameters      
  timeout_int = math.ceil(float(options.timeout))
  

  # Start
  if options.timeout is not None and options.rate is not None:
    setLogLevel('info')
    MakeTestBed_and_Test(int(options.kvalue), timeout_int, ping_interval)

  else:
    print '\nNo switch number given. Abort.\n'



if __name__ == '__main__':
  main()

