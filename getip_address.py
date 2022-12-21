import netifaces

print("Found interfaces:")
for iface in netifaces.interfaces():
    print(iface)

print("\n")

out_addrs = dict()
for iface in netifaces.interfaces():
    allAddrs = netifaces.ifaddresses(iface)

    if netifaces.AF_INET in allAddrs.keys():
        out_addrs[iface] = allAddrs[netifaces.AF_INET]

print(out_addrs)
