#!/usr/bin/python

"""Mininet Network for CST311 Programming Assignment 4"""
__author__ = "Divine Web Design"
__credits__ = [
    "Mike Divine",
    "Russell Frost",
    "Kenneth Ao",
    "Ben Shafer"
]

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
import mininet.term
from subprocess import call

def my_network():

    net = Mininet(  topo=None,
                    build=False,
                    ipBase='10.0.0.0/24')

    info('*** Adding controller\n' )
    c0 = net.addController( name='c0',
                            controller=Controller,
                            protocol='tcp',
                            port=6633)

    info('*** Add switches\n')
    #instantiate switches s1 and s2 ahead of legacy router
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)

    # Instantiate 3 routers
    r5 = net.addHost('r5', cls=Node, ip='10.0.2.1/24') # router connected to "East Coast Network"
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    r4 = net.addHost('r4', cls=Node, ip='192.168.1.1/30') # router connecting the other 2 routers
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    r3 = net.addHost('r3', cls=Node, ip='10.0.1.1/24') # router connected to "West Coast Network"
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Instantiate hosts and set default route to the IP of their default gateway router
    info('*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.2/24', defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.1.3/24', defaultRoute='via 10.0.1.1')
    h3 = net.addHost('h3', cls=Host, ip='10.0.2.2/24', defaultRoute='via 10.0.2.1')
    h4 = net.addHost('h4', cls=Host, ip='10.0.2.3/24', defaultRoute='via 10.0.2.1')

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(s2, r5)
    net.addLink(s1, r3)
    # Assign IP addresses to the interfaces of the interconnected routers.
    net.addLink(r3, r4, intfName1='r3-eth1', params1={'ip': '192.168.1.2/30'}, intfName2='r4-eth0', params2={'ip': '192.168.1.1/30'}) 
    net.addLink(r4, r5, intfName1='r4-eth1', params1={'ip': '192.168.2.1/30'}, intfName2='r5-eth1', params2={'ip': '192.168.2.2/30'})

    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    info('*** Post configure switches and hosts\n')
    # Create routes for each router to forward traffic to the appropriate link.
    r3.cmd('ip route add 10.0.2.0/24 via 192.168.1.1 dev r3-eth1')
    r3.cmd('ip route add 192.168.2.0/30 via 192.168.1.1 dev r3-eth1')
    r4.cmd('ip route add 10.0.1.0/24 via 192.168.1.2 dev r4-eth0')
    r4.cmd('ip route add 10.0.2.0/24 via 192.168.2.2 dev r4-eth1')
    r5.cmd('ip route add 10.0.1.0/24 via 192.168.2.1 dev r5-eth1')
    r5.cmd('ip route add 192.168.1.0/30 via 192.168.2.1 dev r5-eth1')
    
    # Start the Web server,chat server, and chat clients in xterm windows.
    mininet.term.makeTerm(h4, title='h4', term='xterm', cmd="bash -c 'python3 ./CST311/chat_server.py;'")
    mininet.term.makeTerm(h2, title='h2', term='xterm', cmd="bash -c 'python3 ./CST311/simple_tls_server.py;'")
    mininet.term.makeTerm(h1, title='h1', term='xterm', cmd="bash -c 'python3 ./CST311/chat_client.py;'")
    mininet.term.makeTerm(h3, title='h3', term='xterm', cmd="bash -c 'python3 ./CST311/chat_client.py;'")

    CLI(net)
    net.stop()
    mininet.term.cleanUpScreens()

if __name__ == '__main__':
    setLogLevel( 'info' )
    my_network()