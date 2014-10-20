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

        :return: default_gateway
        """


        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue

                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

    def __get_upstream_stats__(self):
        """
        Get upstream statistics (Upstream Power)

        :return: upstream_power_levels
        """

        url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusUpstreamCfgCgi")
        parse = BeautifulSoup(url.read())

        power_label = parse.find(text="Power Level (dBmV)")
        power_table = power_label.parent.parent
        power = power_table.findAll('td')
        power_levels = [power[1].text, power[2].text, power[3].text, power[4].text]

        return power_levels

    def __get_downstream_stats__(self):
        """
        Get downstream statistics (Downstream Power)

        :return: downstream_power_levels
        """

        url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusDownstreamCfgCgi")
        parse = BeautifulSoup(url.read())

        power_label = parse.find(text="Power Level (dBmV)")
        power_table = power_label.parent.parent
        power = power_table.findAll('td')
        power_levels = [power[1].text, power[2].text, power[3].text, power[4].text, power[5].text, power[6].text, power[7].text, power[8].text]

        return power_levels

    def __get_snr__(self):
        """
        Get modem SNR

        :return: SNR_levels
        """

        url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusDownstreamCfgCgi")
        parse = BeautifulSoup(url.read())

        snr_label = parse.find(text="RxMER (dB)")
        snr_table = snr_label.parent.parent
        snr = snr_table.findAll('td')
        snr_levels = [snr[1].text, snr[2].text, snr[3].text, snr[4].text, snr[5].text, snr[6].text, snr[7].text, snr[8].text]

        return snr_levels


if __name__ == '__main__':

    # Need to finish this

    SuperHub = SuperHub()

    print SuperHub.__get_upstream_stats__()
    print SuperHub.__get_downstream_stats__()
    print SuperHub.__get_snr__()




