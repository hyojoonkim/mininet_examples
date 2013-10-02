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


class EventTopo(Topo):
  "20 switch and 1 host topology with varying delays"
  def __init__(self, N, **opts):
    # Initialize topology and default options
    Topo.__init__(self, **opts)

    # Create switches and hosts
    hosts = [ self.addHost( 'h%s' % h )
              for h in irange( 1, N ) ]
    switches = [ self.addSwitch( 's%s' % s )
              for s in irange( 1, N ) ]
  
    # Wire up switches
    last = None                
    for switch in switches:
      if last:
        self.addLink( last, switch )
      last = switch
  
    # Wire up hosts
    for host, switch in zip( hosts, switches ):
      self.addLink( host, switch )

topos = { 'mytopo': ( lambda: EventTopo(5) ) }

def startpings( host, targetip, timeout, wait_time):
  "Tell host to repeatedly ping targets"

  # Simple ping loop
  cmd = ( 'while true; do '
          ' echo -n %s "->" %s ' % (host.IP(), targetip.IP()) + 
          ' `ping %s -i %s -w %s -W 0.9 >> ./output/%s_%s`;' % (targetip.IP(), str(wait_time), str(timeout), host.IP(),targetip.IP()) + 
          ' break;'
          'done &' )

#  cmd = (' echo har > hla%s' %(targetip.IP()) + ' &') 

  print ( '*** Host %s (%s) will be pinging ips: %s' %
          ( host.name, host.IP(), targetip.IP() ) )

  host.cmd( cmd )


def RTTTest(n, timeout, wait_time):
    
  print "a. Firing up Mininet"
  net = Mininet(topo=EventTopo(n), controller=lambda name: RemoteController( 'c0', '127.0.0.1' ), host=CPULimitedHost, link=TCLink)                                  
  net.start() 

  h1 = net.get('h1')
  time.sleep(5)

  # Start pings
  print "b. Starting Test"
  hosts = net.hosts

  for h1 in hosts:
    for h2 in hosts:
      if h1!=h2:
        startpings(h1,h2, timeout, wait_time)
   
  # Wait
  time.sleep(timeout)

  # Stop pings
  for host in hosts:
    host.cmd( 'kill %while' )

  print "c. Stopping Mininet"
  net.stop()

def main():
  desc = ( 'Generate Mininet Testbed' )
  usage = ( '%prog [options]\n'
            '(type %prog -h for details)' )
  op = OptionParser( description=desc, usage=usage )

  ### Options
  op.add_option( '--rate', '-r', action="store", \
                 dest="rate", help = "Set rate. <n>S for (n/second), <n>M for (n/minute). Don't include the brackets when specifying n" )

  op.add_option( '--switchNum', '-s', action="store", \
                 dest="switchnum", help = "Specify the number of switches for this linear topology." )

  op.add_option( '--time', '-t', action="store", \
                 dest="timeout", help = "Specify the timeout in seconds." )


  wait_time = 0.0
  options, args = op.parse_args()

  if options.rate is not None:
    if options.rate.endswith('S'):
      num_str = options.rate.rstrip('S')
      wait_time = 1.0/float(num_str)
    elif options.rate.endswith('M'):
      num_str = options.rate.rstrip('M')
      wait_time = 60.0/float(num_str)
    else:
      print 'Wrong rate format. Abort.'
      return
  else:
    print '\nNo rate given. Abort.\n'
    return

  timeout_int = math.ceil(float(options.timeout))
  if options.switchnum is not None and options.timeout is not None and options.rate is not None:
    setLogLevel('info')
    RTTTest(int(options.switchnum), timeout_int, wait_time)

  else:
    print '\nNo switch number given. Abort.\n'

if __name__ == '__main__':
  main()

