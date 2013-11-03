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
  def __init__(self, topo_type, top, middle=None, bottom=None, host_fanout=None, **opts):
    # Initialize topology and default options
    Topo.__init__(self, **opts)

    if topo_type == 'linear':
      self.linear_topo(top)

    elif topo_type == 'fattree':
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
  "Tell host to repeatedly ping targets"

  # Simple ping loop
  cmd = ( 'while true; do '
          ' echo -n %s "->" %s ' % (host.IP(), targetip.IP()) + 
          ' `ping %s -i %s -w %s -W 0.9 >> ./output/%s_%s`;' % (targetip.IP(), str(ping_interval), str(timeout), host.IP(),targetip.IP()) + 
          ' break;'
          'done &' )

#  cmd = (' echo har > hla%s' %(targetip.IP()) + ' &') 

  print ( '*** Host %s (%s) will be pinging ips: %s' %
          ( host.name, host.IP(), targetip.IP() ) )

  host.cmd( cmd )


def switch_stat_printout(s1):

  # switch stat print loop
#  cmd = ( "while true; do "
#          " date >> ./output/switchstats" 
#          " echo ======== >> ./output/switchstats" 
#          " ovs-dpctl show | grep -E -i -w 'system|flows|lookups' >> ./output/switchstats"
#          " sleep 1"
#          " break;"
#          'done &' )
#
  cmd = ("while true; do " + 
         " sleep 1;" + 
         " echo ======== >> ./output/ssss ;" + 
         "done &")

  print 'check 1.5'
  s1.cmd( cmd )



def MakeTestBed_and_Test(topo_type, top, middle, bottom, host_fanout, timeout, ping_interval):
  print "a. Firing up Mininet"
  net = Mininet(topo=EventTopo(topo_type, top, middle, bottom, host_fanout), controller=lambda name: RemoteController( 'c0', '127.0.0.1' ), host=CPULimitedHost, link=TCLink)                                  
  net.start() 

  h1 = net.get('h1')
  time.sleep(5)

  # Start pings
#  print "b. Starting allpair ping"
  hosts = net.hosts
#
#  for h1 in hosts:
#    for h2 in hosts:
#      if h1!=h2:
#        startpings(h1,h2, timeout, ping_interval)
   
  # Switch instructions (print flow table)
  switches = net.switches
  if len(switches) > 0:
    print 'check 1'
    switch_stat_printout(switches[0])
    print 'check 2'
#    switches[0].cmd("date >> ./output/stats")
#    switches[0].cmd("echo '==========' >> ./output/stats")
#    switches[0].cmd("ovs-dpctl show | grep -E -i -w 'system|flows|lookups' >> ./output/stats")
  else:
    print 'No switches returned'

  # Wait
  time.sleep(timeout)

#  # Stop pings
  for host in hosts:
    host.cmd( 'kill %while' )

  for s in switches:
    s.cmd( 'kill %while' )

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

  op.add_option( '--time', '-t', action="store", \
                 dest="timeout", help = "Specify the timeout in seconds." )
 
  op.add_option( '--type', '-y', action="store", \
                 dest="topo_type", help = "Specify type of the topology (linear, fattree)" )


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
  top = 1
  middle = 2
  bottom = 3
  host_fanout = 2

  # Start
  if options.timeout is not None and options.rate is not None:
    setLogLevel('info')
    MakeTestBed_and_Test(options.topo_type,
                         top,
                         middle,
                         bottom, 
                         host_fanout,
                         timeout_int, ping_interval)
  else:
    print '\nNo switch number given. Abort.\n'



if __name__ == '__main__':
  main()

