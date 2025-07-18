from scapy.all import ARP, Ether, srp
import requests


def scan_local_network(ip_range):
    # 创建 ARP 请求包
    arp = ARP(pdst=ip_range)
    # 创建以太网帧，用于封装 ARP 请求
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    # 组合以太网帧和 ARP 请求
    packet = ether / arp
    # 发送数据包并接收响应，timeout=3 表示等待响应的最长时间为 3 秒
    result = srp(packet, timeout=3, verbose=0)[0]

    clients = []
    for sent, received in result:
        # 提取响应中的 IP 地址和 MAC 地址
        clients.append({'ip': received.psrc, 'mac': received.hwsrc})
    return clients


def get_manufacturer(mac):
    # 提取 OUI
    oui = mac[:8].replace(':', '').replace('-', '').upper()
    url = f"https://api.macvendors.com/{oui}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "Unknown"
    except requests.RequestException:
        return "Error in query"


if __name__ == "__main__":
    # 定义局域网的 IP 地址范围，这里假设是 192.168.1.0/24
    ip_range = "192.168.18.0/24"
    print("Scanning network...")
    clients = scan_local_network(ip_range)
    print("Available devices in the network:")
    print("IP" + " " * 18 + "MAC" + " " * 18 + "Manufacturer")
    for client in clients:
        ip = client['ip']
        mac = client['mac']
        manufacturer = get_manufacturer(mac)
        print(f"{ip:16}    {mac:18}    {manufacturer}")
    print(f"Total number of devices in the network: {len(clients)}")