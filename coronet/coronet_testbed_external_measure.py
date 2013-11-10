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
import sys
from optparse import OptionParser
from lib.custom_topos import Alfares_FatTree


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



def MakeTestBed_and_Test(kval, timeout, ping_interval, controller_ip):
  print "a. Firing up Mininet"
  net = Mininet(topo=Alfares_FatTree(kval), controller=lambda name: RemoteController( 'c0', controller_ip ), host=CPULimitedHost, link=TCLink)
  net.start() 

  time.sleep(5)
  hosts = net.hosts

  # One ping from each host. Make the controller ready.
  print "b. Get all the paths ready"
  for h1 in hosts:
    for h2 in hosts:
      if h1!=h2:
        h1.cmdPrint('ping', '-c3', str(h2.IP()))


  # Start continuous ping
  print "c. Starting continuous allpair ping"
  for h1 in hosts:
    for h2 in hosts:
      if h1!=h2:
        h1.cmdPrint('ping', str(h2.IP()), '&')
#        startpings(h1,h2, timeout, ping_interval)
   
  # Wait
  time.sleep(timeout)

  # Stop pings
  print "d. Stopping pings"
  for host in hosts:
    host.cmd( 'pkill ping' )

  # Stop mininit
  print "e. Stopping Mininet"
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

  op.add_option( '--controller', '-c', action="store", \
                 dest="controller", help = "Controller IP address (with numbers!)" )


  ping_interval = 0.0
  options, args = op.parse_args()

  args = sys.argv[1:]
  if len(args) != 8:
    print '\nWrong number of arguments given: %s. Abort\n' %(str(len(args)))
    op.print_help()
    sys.exit(1)

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
  controller_ip = options.controller
  
  # Start
  if options.timeout is not None and options.rate is not None:
    setLogLevel('info')
    MakeTestBed_and_Test(int(options.kvalue), timeout_int, ping_interval, controller_ip)

  else:
    print '\nNo switch number given. Abort.\n'



if __name__ == '__main__':
  main()

