#!/usr/bin/python2.6
#
# Virgin Media SuperHub signal and power levels monitoring tool
# This tools collects data and sends it to a carbon host for storage
#
# Leon de Jager <ldejager@coretanium.net>
#
# TODO: Cleanup code
# TODO: Implement error handling around socket connects
# TODO: Failback data storage to CSV for manual processing if required
# TODO: Daemonise script
# TODO: Implement performance counters

import time
import struct
import urllib2
import socket
from bs4 import BeautifulSoup


class SuperHub(object):
    """
    Virgin Media SuperHub Statistics Class
    """

    CARBON_SERVER = '0.0.0.0'
    CARBON_PORT = 2003
    INTERVAL = 60

    def __init__(self):
        """
        Initializing
        """

    def __get_gateway__(self):
        """
        Get default gateway by reading /proc/net/route
        If running windows, replace with something that is appropriate for that environment.
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
        """

        try:
            url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusUpstreamCfgCgi", timeout=10)
            parse = BeautifulSoup(url.read())

            power_label = parse.find(text="Power Level (dBmV)")
            power_table = power_label.parent.parent
            power = power_table.findAll('td')
            power_levels = [power[1].text, power[2].text, power[3].text, power[4].text]

            power_data = []

            ts = int(time.time())

            for (i, value) in enumerate(power_levels, start=1):
                power_format = "virgin.modem.stats.us{0}_power {1} {2}".format(i, value, ts)
                power_data.append(power_format)

            return power_data

        except urllib2.URLError, e:

            print "There was an error: %r" % e


    def __get_downstream_stats__(self):
        """
        Get downstream statistics (Downstream Power)
        """

        url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusDownstreamCfgCgi")
        parse = BeautifulSoup(url.read())

        power_label = parse.find(text="Power Level (dBmV)")
        power_table = power_label.parent.parent
        power = power_table.findAll('td')
        power_levels = [power[1].text, power[2].text, power[3].text, power[4].text, power[5].text, power[6].text, power[7].text, power[8].text]

        power_data = []

        ts = int(time.time())

        for (i, value) in enumerate(power_levels, start=1):
            power_format = "virgin.modem.stats.ds{0}_power {1} {2}".format(i, value, ts)
            power_data.append(power_format)

        return power_data

    def __get_snr__(self):
        """
        Get modem SNR
        """

        url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusDownstreamCfgCgi")
        parse = BeautifulSoup(url.read())

        snr_label = parse.find(text="RxMER (dB)")
        snr_table = snr_label.parent.parent
        snr = snr_table.findAll('td')
        snr_levels = [snr[1].text, snr[2].text, snr[3].text, snr[4].text, snr[5].text, snr[6].text, snr[7].text, snr[8].text]

        snr_data = []

        ts = int(time.time())

        for (i, value) in enumerate(snr_levels, start=1):
            snr_format = "virgin.modem.stats.ds{0}_rx {1} {2}".format(i, value, ts)
            snr_data.append(snr_format)

        return snr_data


    def __carbon_send__(self, data_stream):
        """
        Send data to Carbon
        """

        print 'sending data to carbon:\n%s' % data_stream
        sock = socket.socket()
        sock.connect((SuperHub.CARBON_SERVER, SuperHub.CARBON_PORT))
        sock.sendall(data_stream)
        sock.close()


if __name__ == '__main__':

    SuperHub = SuperHub()

    while True:
        data = SuperHub.__get_upstream_stats__() + SuperHub.__get_downstream_stats__() + SuperHub.__get_snr__()
        data_stream = '\n'.join(data) + '\n'
        SuperHub.__carbon_send__(data_stream)
        time.sleep(SuperHub.INTERVAL)
