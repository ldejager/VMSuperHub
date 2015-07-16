#!/usr/bin/env python
#
# Virgin Media SuperHub signal and power levels monitoring tool
# This tools collects data and sends it to a carbon host for storage
#
# Leon de Jager <ldejager@coretanium.net>

import time
import struct
import urllib2
import socket
import csv
import os
from bs4 import BeautifulSoup


class SuperHub(object):
    """
    Virgin Media SuperHub Statistics Class
    """

    CARBON_SERVER = '0.0.0.0'
    CARBON_PORT = 2003
    INTERVAL = 60
    CARBON_PATH = 'virgin.modem.stats'
    CSV_FILE = os.path.dirname(os.path.abspath(__file__)) + '/vmstats.csv'
    OUTPUT = '3'
    CONNECT_TIMEOUT = '10'
    DEFAULT_MODEM_IP = '192.168.100.1'

    def __init__(self):
        """
        Initializing
        """

        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/var/run/vmsuperhub.pid'
        self.pidfile_timeout = 5
        self.time = time.time()

    def __get_gateway__(self):
        """
        Get gateway IP (modem/router) to grab stats.

        In router mode read /proc/net/route, in modem mode use DEFAULT_MODEM_IP config value.
        """

        try:
            urllib2.urlopen("http://" + self.DEFAULT_MODEM_IP + "/RouterStatus.html", timeout=1)
            return self.DEFAULT_MODEM_IP
        except urllib2.URLError:
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
            url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusUpstreamCfgCgi",
                                  timeout=self.CONNECT_TIMEOUT)
            parse = BeautifulSoup(url.read())

            power_label = parse.find(text="Power Level (dBmV)")
            power_table = power_label.parent.parent
            power = power_table.findAll('td')
            power_levels = [power[1].text, power[2].text, power[3].text, power[4].text]

            for idx, level in enumerate(power_levels):
                if 'N/A' in level:
                    level = '%.2f' % float(0.00)
                    power_levels[idx] = level
                else:
                    power_levels[idx] = level

            power_data = []

            ts = int(time.time())

            for (i, value) in enumerate(power_levels, start=1):
                power_format = SuperHub.CARBON_PATH + ".us{0}_power {1} {2}".format(i, value, ts)
                power_data.append(power_format)

            return power_data

        except urllib2.URLError, e:

            print "There was an error: %r" % e

    def __get_downstream_stats__(self):
        """
        Get downstream statistics (Downstream Power)
        """

        try:
            url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusDownstreamCfgCgi",
                                  timeout=self.CONNECT_TIMEOUT)
            parse = BeautifulSoup(url.read())

            power_label = parse.find(text="Power Level (dBmV)")
            power_table = power_label.parent.parent
            power = power_table.findAll('td')
            power_levels = [power[1].text, power[2].text, power[3].text, power[4].text, power[5].text, power[6].text,
                            power[7].text, power[8].text]

            for idx, level in enumerate(power_levels):
                if 'N/A' in level:
                    level = '%.2f' % float(0.00)
                    power_levels[idx] = level
                else:
                    power_levels[idx] = level

            power_data = []

            ts = int(time.time())

            for (i, value) in enumerate(power_levels, start=1):
                power_format = SuperHub.CARBON_PATH + ".ds{0}_power {1} {2}".format(i, value, ts)
                power_data.append(power_format)

            return power_data

        except urllib2.URLError, e:

            print "There was an error: %r" % e

    def __get_snr__(self):
        """
        Get modem SNR
        """

        try:
            url = urllib2.urlopen("http://" + self.__get_gateway__() + "/cgi-bin/VmRouterStatusDownstreamCfgCgi",
                                  timeout=self.CONNECT_TIMEOUT)
            parse = BeautifulSoup(url.read())

            snr_label = parse.find(text="RxMER (dB)")
            snr_table = snr_label.parent.parent
            snr = snr_table.findAll('td')
            snr_levels = [snr[1].text, snr[2].text, snr[3].text, snr[4].text, snr[5].text, snr[6].text, snr[7].text,
                          snr[8].text]

            for idx, level in enumerate(snr_levels):
                if 'N/A' in level:
                    level = '%.2f' % float(0.00)
                    snr_levels[idx] = level
                else:
                    snr_levels[idx] = level

            snr_data = []

            ts = int(time.time())

            for (i, value) in enumerate(snr_levels, start=1):
                snr_format = SuperHub.CARBON_PATH + ".ds{0}_rx {1} {2}".format(i, value, ts)
                snr_data.append(snr_format)

            return snr_data

        except urllib2.URLError, e:

            print "There was an error: %r" % e

    @staticmethod
    def __carbon_send__(data_stream):
        """
        Send data to Carbon
        """

        try:
            sock = socket.socket()
            sock.connect((SuperHub.CARBON_SERVER, SuperHub.CARBON_PORT))
            sock.sendall(data_stream)
            sock.close()

        except socket.error, e:

            print "There was an error: %r" % e

    @staticmethod
    def __write_csv__(data_stream):
        """
        Write CSV file as fallback method for manual processing if required
        """

        with open(SuperHub.CSV_FILE, 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([data_stream])

    def run(self):
        """
        Main processing daemon
        """

        while True:
            print "---\n%s" % SuperHub.time
            print "Collecting data..."
            t0 = time.time()
            data = SuperHub.__get_upstream_stats__() + SuperHub.__get_downstream_stats__() + SuperHub.__get_snr__()
            data_stream = '\n'.join(data) + '\n'
            if SuperHub.OUTPUT == '3':
                SuperHub.__carbon_send__(data_stream)
                print "Sending data to CARBON..."
                SuperHub.__write_csv__(data_stream)
                print "Writing data to CSV..."
            elif SuperHub.OUTPUT == '2':
                SuperHub.__carbon_send__(data_stream)
                print "Sending data to CARBON..."
            elif SuperHub.OUTPUT == '1':
                SuperHub.__write_csv__(data_stream)
                print "Writing data to CSV..."
            t1 = time.time()
            time_taken = t1-t0
            time_sleep = SuperHub.INTERVAL - time_taken
            print "Data collection took %s" % time_taken
            print "Sleeping for %s...\n---\n\n" % time_sleep
            time.sleep(SuperHub.INTERVAL - time_taken)


if __name__ == '__main__':

    SuperHub = SuperHub()

    SuperHub.run()
