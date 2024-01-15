from dotenv import load_dotenv
import os

def load_env():
    load_dotenv()
    ipv4_list = os.getenv('IPV4').split(', ')
    ipv6_list = os.getenv('IPV6').split(', ')
    return ipv4_list, ipv6_list

