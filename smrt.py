#!/usr/bin/env python3

import socket, time, random, argparse, logging

from protocol import Protocol
from network import Network
from binary import ports2byte, ports2list

def loglevel(x):
    try:
        return getattr(logging, x.upper())
    except AttributeError:
        raise argparse.ArgumentError('Select a proper loglevel')

def main():
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--switch-mac', '-s')
    parser.add_argument('--host-mac', )
    parser.add_argument('--ip-address', '-i')
    parser.add_argument('--username', '-u')
    parser.add_argument('--password', '-p')
    parser.add_argument('--vlan', type=int)
    parser.add_argument('--vlan_name')
    parser.add_argument('--vlan_member')
    parser.add_argument('--vlan_tagged')
    parser.add_argument('--vlan_pvid')
    parser.add_argument('--delete', action="store_true")
    parser.add_argument('--loglevel', '-l', type=loglevel, default='INFO')
    parser.add_argument('action', default=None, nargs='?')
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    net = Network(args.ip_address, args.host_mac, args.switch_mac)
    actions = Protocol.tp_ids

    if args.action not in Protocol.tp_ids and not args.vlan:
            print("Actions:" , *actions.keys())
    else:
        net.login(args.username, args.password)
        if args.vlan:
            if args.vlan_member or args.vlan_tagged or args.delete:
                if (args.delete):
                    v = Protocol.set_vlan(int(args.vlan), 0, 0, "")
                else:
                    v = Protocol.set_vlan(int(args.vlan), ports2byte(args.vlan_member), ports2byte(args.vlan_tagged), args.vlan_name)
                l = [(actions["vlan"], v)]

            if args.vlan_pvid is not None:
                l = []
                for port in ports2list(args.vlan_pvid):
                    if port != 0:
                        l.append( (actions["pvid"], Protocol.set_pvid(args.vlan, port)) )
            header, payload = net.set(args.username, args.password, l)
        elif args.action in actions:
            header, payload = net.query(Protocol.GET, [(actions[args.action], b'')])
        print(*payload, sep="\n")

if __name__ == "__main__":
    main()
