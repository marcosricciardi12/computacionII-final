import argparse
from multiprocessing import Process
from tcp_service import service4, service6
from load_env import load_env

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hola")
    parser.add_argument("-p", "--port", type=int, required=True, help="Ingrese el numero de puerto")
    parser.add_argument("-c", "--concurrency", type=str, required=True, help="Concurrencia: forking o threading")
    args = parser.parse_args()
    ipv4_list, ipv6_list = load_env()
    print(ipv4_list, ipv6_list)
    procesos = []
    for addr in ipv4_list:
        procesos.append(Process(target=service4, args = (str(addr), args.port, args.concurrency,)))
    for addr in ipv6_list:
        procesos.append(Process(target=service6, args = (str(addr), args.port, args.concurrency,)))

    for p in procesos:
        p.start()