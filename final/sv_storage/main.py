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
    if not os.path.exists("files/original"):
        os.makedirs("files/original")
    if not os.path.exists("files/medium"):
        os.makedirs("files/medium")
    if not os.path.exists("files/low"):
        os.makedirs("files/low")
    load_dotenv()
    user = os.getenv('USER')
    print("Welcome '%s' to sv_storage" % user)
    ipv4_list = os.getenv('IPV4').split(', ')
    ipv6_list = os.getenv('IPV6').split(', ')

    print(ipv4_list, ipv6_list)
    procesos = []
    # for addr in ipv4_list:
    procesos.append(Process(target=service4, args = (str('0.0.0.0'), args.port, args.concurrency,)))
    for addr in ipv6_list:
        procesos.append(Process(target=service6, args = (str(addr), args.port, args.concurrency,)))

    for p in procesos:
        p.start()