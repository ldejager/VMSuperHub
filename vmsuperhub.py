#!/usr/bin/python2.6
#
# Virgin Media SuperHub Statistics Gathering Tool
#

import datetime
import time
import struct
import urllib2
import socket
from bs4 import BeautifulSoup


class SuperHub(object):
    """
    Virgin Media SuperHub Statistics Class
    """

    def __init__(self):
        """
        Initializing
        """

    def __get_gateway__(self):
        """
        Get default gateway by reading /proc/net/route
        """

        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue

                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    def __get_upstream_stats__(self):
        """
        Get upstream statistics
        """

        upstream_url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusUpstreamCfgCgi")
        upstream_parse = BeautifulSoup(upstream_url.read())

        upstream_power_label = upstream_parse.find(text="Power Level (dBmV)")
        upstream_power_table = upstream_power_label.parent.parent
        upstream_power = upstream_power_table.findAll('td')
        upstream_power_levels = [upstream_power[1].text, upstream_power[2].text, upstream_power[3].text, upstream_power[4].text]

        return upstream_power_levels


if __name__ == '__main__':

    # Need to finish this

    SuperHub = SuperHub()

    print SuperHub.__get_upstream_stats__()
    print SuperHub.__get_gateway__()




