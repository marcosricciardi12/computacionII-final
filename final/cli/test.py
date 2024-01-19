import argparse
import os

parser = argparse.ArgumentParser(description="sdasdas")
parser.add_argument("-j", "--host", type=str, required=True, help="Ingrese la direccion ip del host")
parser.add_argument("-p", "--port", type=int, required=True, help="Ingrese el numero de puerto del host")
parser.add_argument("-r", "--receive", action='store_true',)
parser.add_argument("-s", "--send", action='store_true',)
args = parser.parse_args()

print(args.host, args.port, args.receive)

if args.receive and args.send:
    print("Elija solo una opcion: send o receive")
    os._exit(0)

if not (args.receive or args.send):
    print("Elija al menos una opcion: send o receive")
    os._exit(0)

if args.receive:
    a = input("ingresa algo para recibir: ")
    print(a)

if args.send:
    a = input("ingresa algo para enviar: ")
    print(a)

