from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink
import subprocess
import sys
import time
import os
import base64


class LinuxRouter( Node ):
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )

        self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.cmd( 'sysctl net.ipv4.conf.all.proxy_arp=1' )


    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        self.cmd( 'sysctl net.ipv4.conf.all.proxy_arp=0' )
        super( LinuxRouter, self ).terminate()


def runNetwork():
    """
        author: Brian Lebiednik
    """
    net = Mininet(topo=None)
    core = 4

    info('*** Adding Core routers ***\n')
    info('----------------------\n')
    corerouters = {}
    for x in range(0, core):
        corerouters[x] = net.addHost('cr'+str(x), cls=LinuxRouter, ip='10.0.1'+str(x)+'.1/24')
        #using 10.0.3X.0/24 for the default IP
    info('*** Adding aggregate router                       ***\n')
    aggrouters = {}
    for x in range(0,(core * 2)):
        aggrouters[x] = net.addHost('ar'+str(x), cls=LinuxRouter, ip='10.0.2'+str(x)+'.1/24')
        #using 10.0.2X.0/24 for the default IP
    info('*** Adding edge routers                          ***\n' )
    edgerouters = {}
    for x in range(0, (core *2)):
        edgerouters[x] = net.addHost('er'+str(x), cls=LinuxRouter, ip='10.0.3'+str(x)+'.1/24')
        #using 10.0.3X.0/24 for the default IP
    info('***  Adding hosts                                 ***\n')
    hosts = {}
    for x in range (0, (core*8)):
        hosts[x] = net.addHost('h'+str(x))

    info('*** Adding links to construct topology ***\n')
    info('------------------------------------------\n')
    info('*********************************************************\n')
    info('*     cr0          cr1          cr2          cr3        *\n')
    info('*                                                       *\n')
    info('*  ar0    ar1    ar2    ar3    ar4    ar5    ar6    ar7 *\n')
    info('*                                                       *\n')
    info('*  er0    er1    er2    er3    er4    er5    er6    er7 *\n')
    info('*                                                       *\n')
    info('*********************************************************\n')

    info('*** Adding links to core routers                      ***\n')
    for x in range(0,core*2, 2):
        net.addLink(corerouters[0], aggrouters[x],params1={'ip': '10.{}.2.2/24'.format(x)}, params2={'ip': '10.{}.2.3/24'.format(x)})
        net.addLink(corerouters[1], aggrouters[x],params1={'ip': '10.{}.3.2/24'.format(x)}, params2={'ip': '10.{}.3.3/24'.format(x)})
        #using 10.X.3.0/24 for the default IP
    for x in range(1, core*2, 2):
        net.addLink(corerouters[2], aggrouters[x], params1={'ip': '10.{}.4.2/24'.format(x)}, params2={'ip': '10.{}.4.3/24'.format(x)})
        net.addLink(corerouters[3], aggrouters[x], params1={'ip': '10.{}.5.2/24'.format(x)}, params2={'ip': '10.{}.5.3/24'.format(x)})
    info('*** Adding links to aggregate routers                 ***\n')
    for x in range(0, (core*2), 2):
        net.addLink(aggrouters[x], edgerouters[x], params1={'ip': '10.{}.6.2/24'.format(x)}, params2={'ip': '10.{}.6.3/24'.format(x)})
        net.addLink(aggrouters[x], edgerouters[x+1], params1={'ip': '10.{}.7.2/24'.format(x)}, params2={'ip': '10.{}.7.3/24'.format(x)})

    for x in range(1, (core*2), 2):
        net.addLink(aggrouters[x], edgerouters[x], params1={'ip': '10.{}.8.2/24'.format(x)}, params2={'ip': '10.{}.8.3/24'.format(x)})
        net.addLink(aggrouters[x], edgerouters[x-1], params1={'ip': '10.{}.9.2/24'.format(x)}, params2={'ip': '10.{}.9.3/24'.format(x)})
        #aggrouter[x]

    info('*** Adding links to host                              ***\n')
    k = 0
    for x in range(0, (core*2)):
        for j in range(0, core):
            i = (x*core)+j
            net.addLink(edgerouters[x], hosts[i], params1={'ip': '10.{}.101.2/24'.format(k)}, params2={'ip': '10.{}.101.3/24'.format(k)})
            k = k +1


    net.build()
    for x in range(0, (core*2), 2):
        aggrouters[x].cmd('ip route add default via 10.{}.2.2'.format(x))
        aggrouters[x+1].cmd('ip route add default via 10.{}.4.2'.format(x))
    for x in range(0, (core*2), 2):
        edgerouters[x].cmd('ip route add default via 10.{}.6.2'.format(x))
        edgerouters[x+1].cmd('ip route add default via 10.{}.7.2'.format(x))

    for x in range(0, 8):
        corerouters[0].cmd('ip route add 10.{}.101.0/24 via 10.0.2.3'.format(x))
        corerouters[1].cmd('ip route add 10.{}.101.0/24 via 10.0.3.3'.format(x))
        corerouters[2].cmd('ip route add 10.{}.101.0/24 via 10.1.4.3'.format(x))
        corerouters[3].cmd('ip route add 10.{}.101.0/24 via 10.1.5.3'.format(x))

    for x in range(8, 16):
        corerouters[0].cmd('ip route add 10.{}.101.0/24 via 10.2.2.3'.format(x))
        corerouters[1].cmd('ip route add 10.{}.101.0/24 via 10.2.3.3'.format(x))
        corerouters[2].cmd('ip route add 10.{}.101.0/24 via 10.3.4.3'.format(x))
        corerouters[3].cmd('ip route add 10.{}.101.0/24 via 10.3.5.3'.format(x))

    for x in range(16, 24):
        corerouters[0].cmd('ip route add 10.{}.101.0/24 via 10.4.2.3'.format(x))
        corerouters[1].cmd('ip route add 10.{}.101.0/24 via 10.4.3.3'.format(x))
        corerouters[2].cmd('ip route add 10.{}.101.0/24 via 10.5.4.3'.format(x))
        corerouters[3].cmd('ip route add 10.{}.101.0/24 via 10.5.5.3'.format(x))

    for x in range(24, 32):
        corerouters[0].cmd('ip route add 10.{}.101.0/24 via 10.6.2.3'.format(x))
        corerouters[1].cmd('ip route add 10.{}.101.0/24 via 10.6.3.3'.format(x))
        corerouters[2].cmd('ip route add 10.{}.101.0/24 via 10.7.4.3'.format(x))
        corerouters[3].cmd('ip route add 10.{}.101.0/24 via 10.7.5.3'.format(x))

    corerouters[0].cmd('ip route add 10.0.6.0/24 via 10.0.2.3')
    corerouters[0].cmd('ip route add 10.0.7.0/24 via 10.0.2.3')
    corerouters[0].cmd('ip route add 10.1.8.0/24 via 10.0.2.3')
    corerouters[0].cmd('ip route add 10.1.9.0/24 via 10.0.2.3')
    corerouters[0].cmd('ip route add 10.2.6.0/24 via 10.2.2.3')
    corerouters[0].cmd('ip route add 10.2.7.0/24 via 10.2.2.3')
    corerouters[0].cmd('ip route add 10.3.8.0/24 via 10.2.2.3')
    corerouters[0].cmd('ip route add 10.3.9.0/24 via 10.2.2.3')
    corerouters[0].cmd('ip route add 10.4.6.0/24 via 10.4.2.3')
    corerouters[0].cmd('ip route add 10.4.7.0/24 via 10.4.2.3')
    corerouters[0].cmd('ip route add 10.5.8.0/24 via 10.4.2.3')
    corerouters[0].cmd('ip route add 10.5.9.0/24 via 10.4.2.3')
    corerouters[0].cmd('ip route add 10.6.6.0/24 via 10.6.2.3')
    corerouters[0].cmd('ip route add 10.6.7.0/24 via 10.6.2.3')
    corerouters[0].cmd('ip route add 10.7.8.0/24 via 10.6.2.3')
    corerouters[0].cmd('ip route add 10.7.9.0/24 via 10.6.2.3')



    corerouters[1].cmd('ip route add 10.0.6.0/24 via 10.0.3.3')
    corerouters[1].cmd('ip route add 10.0.7.0/24 via 10.0.3.3')
    corerouters[1].cmd('ip route add 10.1.8.0/24 via 10.0.3.3')
    corerouters[1].cmd('ip route add 10.1.9.0/24 via 10.0.3.3')

    corerouters[1].cmd('ip route add 10.2.6.0/24 via 10.2.3.3')
    corerouters[1].cmd('ip route add 10.2.7.0/24 via 10.2.3.3')
    corerouters[1].cmd('ip route add 10.3.8.0/24 via 10.2.3.3')
    corerouters[1].cmd('ip route add 10.3.9.0/24 via 10.2.3.3')

    corerouters[1].cmd('ip route add 10.4.6.0/24 via 10.4.3.3')
    corerouters[1].cmd('ip route add 10.4.7.0/24 via 10.4.3.3')
    corerouters[1].cmd('ip route add 10.5.8.0/24 via 10.4.3.3')
    corerouters[1].cmd('ip route add 10.5.9.0/24 via 10.4.3.3')

    corerouters[1].cmd('ip route add 10.6.6.0/24 via 10.6.3.3')
    corerouters[1].cmd('ip route add 10.6.7.0/24 via 10.6.3.3')
    corerouters[1].cmd('ip route add 10.7.8.0/24 via 10.6.3.3')
    corerouters[1].cmd('ip route add 10.7.9.0/24 via 10.6.3.3')

    corerouters[2].cmd('ip route add 10.0.6.0/24 via 10.1.4.3')
    corerouters[2].cmd('ip route add 10.0.7.0/24 via 10.1.4.3')
    corerouters[2].cmd('ip route add 10.1.8.0/24 via 10.1.4.3')
    corerouters[2].cmd('ip route add 10.1.9.0/24 via 10.1.4.3')

    corerouters[2].cmd('ip route add 10.2.6.0/24 via 10.3.4.3')
    corerouters[2].cmd('ip route add 10.2.7.0/24 via 10.3.4.3')
    corerouters[2].cmd('ip route add 10.3.8.0/24 via 10.3.4.3')
    corerouters[2].cmd('ip route add 10.3.9.0/24 via 10.3.4.3')

    corerouters[2].cmd('ip route add 10.4.6.0/24 via 10.5.4.3')
    corerouters[2].cmd('ip route add 10.4.7.0/24 via 10.5.4.3')
    corerouters[2].cmd('ip route add 10.5.8.0/24 via 10.5.4.3')
    corerouters[2].cmd('ip route add 10.5.9.0/24 via 10.5.4.3')

    corerouters[2].cmd('ip route add 10.6.6.0/24 via 10.7.4.3')
    corerouters[2].cmd('ip route add 10.6.7.0/24 via 10.7.4.3')
    corerouters[2].cmd('ip route add 10.7.8.0/24 via 10.7.4.3')
    corerouters[2].cmd('ip route add 10.7.9.0/24 via 10.7.4.3')

    corerouters[3].cmd('ip route add 10.0.6.0/24 via 10.1.5.3')
    corerouters[3].cmd('ip route add 10.0.7.0/24 via 10.1.5.3')
    corerouters[3].cmd('ip route add 10.1.8.0/24 via 10.1.5.3')
    corerouters[3].cmd('ip route add 10.1.9.0/24 via 10.1.5.3')

    corerouters[3].cmd('ip route add 10.2.6.0/24 via 10.3.5.3')
    corerouters[3].cmd('ip route add 10.2.7.0/24 via 10.3.5.3')
    corerouters[3].cmd('ip route add 10.3.8.0/24 via 10.3.5.3')
    corerouters[3].cmd('ip route add 10.3.9.0/24 via 10.3.5.3')

    corerouters[3].cmd('ip route add 10.4.6.0/24 via 10.5.5.3')
    corerouters[3].cmd('ip route add 10.4.7.0/24 via 10.5.5.3')
    corerouters[3].cmd('ip route add 10.5.8.0/24 via 10.5.5.3')
    corerouters[3].cmd('ip route add 10.5.9.0/24 via 10.5.5.3')

    corerouters[3].cmd('ip route add 10.6.6.0/24 via 10.7.5.3')
    corerouters[3].cmd('ip route add 10.6.7.0/24 via 10.7.5.3')
    corerouters[3].cmd('ip route add 10.7.8.0/24 via 10.7.5.3')
    corerouters[3].cmd('ip route add 10.7.9.0/24 via 10.7.5.3')

    #net.pingAll()

    CLI(net)
    net.stop()
    subprocess.call(['mn', '-c'])


if __name__ == '__main__':
    setLogLevel('info')
    runNetwork()
