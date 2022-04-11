import dpkt
import socket

from snortunsock import snort_listener


def mac_addr(address):
    return ':'.join('%02x' % ord(b) for b in address)


def ip_to_str(address):
    return socket.inet_ntop(socket.AF_INET, address)


def main():
    for msg in snort_listener.start_recv("/tmp/snort_alert"):
        print('alertmsg: %s' % ''.join(msg.alertmsg))
        buf = msg.pkt
        eth = dpkt.ethernet.Ethernet(buf)
        print('Ethernet Frame: ', mac_addr(eth.src), mac_addr(eth.dst), eth.type)

        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            print('Non IP Packet type not supported %s\n' % eth.data.__class__.__name__)
        ip = eth.data
        do_not_fragment = bool(ip.off & dpkt.ip.IP_DF)
        more_fragments = bool(ip.off & dpkt.ip.IP_MF)
        fragment_offset = ip.off & dpkt.ip.IP_OFFMASK

        # Print out the info
        print('IP: %s -> %s   (len=%d ttl=%d DF=%d MF=%d offset=%d)\n' % \
              (ip_to_str(ip.src), ip_to_str(ip.dst), ip.len, ip.ttl, do_not_fragment, more_fragments, fragment_offset))

if __name__ == '__main__':
    main()