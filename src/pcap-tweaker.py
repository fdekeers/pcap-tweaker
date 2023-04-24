"""
Randomly edit packet fields in a PCAP file.
"""

import os
from pathlib import Path
import string
import argparse
import json
import scapy.all as scapy
from packet.Packet import Packet

# Useful paths
script_path = os.path.abspath(os.path.dirname(__file__))
packet_utils_dir = os.path.join(script_path, "packet")
packet_utils = [Path(f).stem for f in os.listdir(packet_utils_dir) if os.path.isfile(os.path.join(packet_utils_dir, f))]
# List of all alphanumerical characters
ALPHANUM = list(bytes(string.ascii_letters + string.digits, "utf-8"))


if __name__ == "__main__":

    ### ARGUMENT PARSING ###
    
    parser = argparse.ArgumentParser(
        prog="pcap-tweaker.py",
        description="Randomly edit packet fields in a PCAP file."
    )

    # Positional argument #1: input PCAP file
    parser.add_argument("input_pcap", type=str, help="Input PCAP file.")
    # Optional argument -o: output PCAP file
    parser.add_argument("-o", "--output_pcap", type=str, help="Output PCAP file. Default is input file name with '.tweak' appended.")

    args = parser.parse_args()
    if args.output_pcap is None:
        args.output_pcap = args.input_pcap.replace(".pcap", ".tweak.pcap")

    
    ### LOAD SUPPORTED PROTOCOLS ###
    protocols = {}
    with open("protocols.json", "r") as f:
        protocols = json.load(f)

    
    ### MAIN PROGRAM ###

    # Read input PCAP file
    packets = scapy.rdpcap(args.input_pcap)
    new_packets = []

    # Loop on packets
    i = 0
    for packet in packets:

        # Choose randomly if we edit this packet
        #if random.randint(0, 1) != 0:
        if i != 3:
            # Packet won't be edited
            # Go to next packet
            new_packets.append(packet)
            i += 1
            continue

        # Packet will be edited
        # Get packet highest layer
        layer = packet.lastlayer()

        # Check if layer is supported
        if layer.name not in protocols:
            # Layer not supported
            # Go to next packet
            new_packets.append(packet)
            i += 1
            continue

        # Layer is supported
        # Edit packet
        packet = Packet.init_packet(layer.name, packet, i)
        packet.tweak()

        new_packets.append(packet.get_packet())
        i += 1

    # Write output PCAP file
    scapy.wrpcap(args.output_pcap, new_packets)
