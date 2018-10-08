import socket
import struct
import binascii
import time
import json
import urllib2
import smtplib
import requests

# Dash button MAC addresses
macs = {
        '44650dd2dad1' : 'dash_simple',
        '50f5dafd7441' : 'dash_cascade'
}

# Trigger a IFTTT URL. Body includes JSON with timestamp values.

rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

def difm(type, channel, device):
    r = requests.post("http://127.0.0.1:5000/process", data={"t":type, "channel":channel, "device":device})
    print r.status_code, r.reason


if __name__ == "__main__":
    while True:
        packet = rawSocket.recvfrom(2048)
        ethernet_header = packet[0][0:14]
        ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)

        ethertype = ethernet_detailed[2]
        if ethertype != '\x08\x06':
            continue

        arp_header = packet[0][14:42]
        arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)
        source_mac = binascii.hexlify(arp_detailed[5])
        source_ip = socket.inet_ntoa(arp_detailed[6])
        dest_ip = socket.inet_ntoa(arp_detailed[8])

        if source_mac in macs:
            if macs[source_mac] == 'dash_simple':
                print "dash_simple was pressed, playing atmospheric breaks via all"
                difm("manual", "atmosphericbreaks_hi", "Home group")
            if macs[source_mac] == 'dash_cascade':
                print "dash_cascade was pressed, playin breaks via all"
                difm("manual", "breaks_hi", "Home group")
