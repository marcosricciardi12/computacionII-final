import argparse
from multiprocessing import Process
from tcp_service import service4, service6
from dotenv import load_dotenv
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hola")
    parser.add_argument("-p", "--port", type=int, required=True, help="Ingrese el numero de puerto")
    parser.add_argument("-c", "--concurrency", type=str, required=True, help="Concurrencia: forking o threading")
    args = parser.parse_args()

    load_dotenv()
    ipv4_list = os.getenv('IPV4').split(', ')
    ipv6_list = os.getenv('IPV6').split(', ')
    st_addr_v4 = os.getenv('SV_ST_ADDR_V4').split(', ')
    st_addr_v4_ip , st_addr_v4_port = st_addr_v4[0], st_addr_v4[1]
    st_addr_v6 = os.getenv('SV_ST_ADDR_V6').split(', ')
    st_addr_v6_ip , st_addr_v6_port = st_addr_v6[0], st_addr_v6[1]
    print("Storage Adrr4: %s:%s" % (st_addr_v4_ip , st_addr_v4_port))
    print("Storage Adrr6: %s:%s" % (st_addr_v6_ip , st_addr_v6_port))

    print(ipv4_list, ipv6_list)
    procesos = []
    for addr in ipv4_list:
        procesos.append(Process(target=service4, args = (str(addr), args.port, args.concurrency,)))
    for addr in ipv6_list:
        procesos.append(Process(target=service6, args = (str(addr), args.port, args.concurrency,)))

    for p in procesos:
        p.start()