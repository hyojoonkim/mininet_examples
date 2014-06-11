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


def ping_traffic(hosts, timeout,ping_interval):
    for h1 in hosts:
        for h2 in hosts:
            if h1!=h2:
                h1.cmd('ping','-i', str(ping_interval), '-W', str(timeout), str(h2.IP()), '&')


def tcp_iperf_traffic(hosts):
    # Start iperf daemons in all hosts
    for h1 in hosts:
        h1.cmd('iperf -sD')

    # Start iperf in all hosts to all
    for h1 in hosts:
        for h2 in hosts:
            if h1!=h2:
                h1.cmd('iperf -c', str(h2.IP()), '-t 3600', '&')


def udp_iperf_traffic(hosts):
    # Start iperf daemons in all hosts
    for h1 in hosts:
        h1.cmd('iperf -sD')

    # Start iperf in all hosts to all
    for h1 in hosts:
        for h2 in hosts:
            if h1!=h2:
                h1.cmd('iperf -c', str(h2.IP()), '-t 3600 -u', '&')


def check_connectivity(result):
    for m in result:
        src = m[0] 
        dst = m[1]

        # attempt/success, rtt min/avg/max/mdev %0.3f/%0.3f/%0.3f/%0.3f ms\n
        # ex (1, 1, 3.981, 3.981, 3.981, 0.0)
        measure_tuple = m[2] 
        nattempt = int(measure_tuple[0])
        nsuccess = int(measure_tuple[1])

        # if num. of attempt is not same as num, of success,
        if nattempt != nsuccess:
            return False

    return True


def first_ping(hosts):
    for h1 in hosts:
        if str(h1.IP())=='10.0.0.1' is True:
            h1.cmd('ping -c 1 10.0.0.2')
        else:
            h1.cmd('ping -c 1 10.0.0.1')


def MakeTestBed_and_Test(topo_type, top, middle, bottom, host_fanout, timeout, ping_interval):

    network_stopped = False

    ### Start mininet.
    print "a. Firing up Mininet"
    net = Mininet(topo=EventTopo(topo_type, top, middle, bottom, host_fanout),   \
                  controller=lambda name: RemoteController( 'c0', '127.0.0.1' ), \
                  host=CPULimitedHost, link=TCLink)     
    net.start() 
    time.sleep(1)

    ### Make host notify where it is
    print "b. Send first pings"
    first_ping(net.hosts)

    ### Test connectivity
    print "c. Test connectivity"
    result = net.pingAllFull()
    if check_connectivity(result) is False:
        print '\n####################################\nFailed connectivity test! Abort\n####################################\n'
        stop_mininet(net,c)
        network_stopped = True
  

    ### Start traffic
    print "d. Start background traffic"
    ping_traffic(net.hosts, timeout, ping_interval)
#    tcp_iperf_traffic(net.hosts)
#    udp_iperf_traffic(net.hosts)
 
    time.sleep(5)

    ### Link/switch up and downs start
    print "e. Start killing link/switches"
    c = CLI(net,script='test_cmds')
    #  c = CLI(net)
    #  CLI.do_help(c,'')
 

    ### Test connectivity
    print "f. Test connectivity again"
    result = net.pingAllFull()
    if check_connectivity(result) is False:
        print '\n####################################\nFailed connectivity test! Abort\n####################################\n'
        stop_mininet(net,c)
        network_stopped = True
  

    ### End test. Exit mininet.
    if network_stopped is False:
        print "g. Stopping Mininet"
        stop_mininet(net,c)


def kill_traffic(cli): 
    # Kill ping traffic
    CLI.do_sh(cli,'pkill ping')

    # Kill TCP/UDP (iperf) traffic
    CLI.do_sh(cli, 'kill -9 `pgrep iperf`')
        

def stop_mininet(net,cli):
    kill_traffic(cli)
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
  top = 5
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

