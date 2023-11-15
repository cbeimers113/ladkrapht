import sys
from mcrcon import MCRcon

cmd = " ".join(sys.argv[1:])

ip = ""
with open(".ip", 'r') as f:
    ip = f.read().strip()

with MCRcon(ip, "ladkrapht") as mcr:
    print(mcr.command(cmd))

