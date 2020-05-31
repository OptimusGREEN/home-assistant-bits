import psutil

# cpu_pct = psutil.cpu_percent(interval=0.1, percpu=False)
# load = psutil.getloadavg()
# mem = psutil.virtual_memory()

def get_disks(return_type="all"):
    disks = psutil.disk_partitions(all=False)
    internal_disks = []
    external_disks = []
    for d in disks:
        if "/mnt/" in d.mountpoint:
            internal_disks.append(d.mountpoint)
        if "/" == d.mountpoint:
            internal_disks.append(d.mountpoint)
        if "/media/" in d.mountpoint:
            external_disks.append(d.mountpoint)
    if return_type == 'all':
        return (internal_disks, external_disks)
    elif return_type == 'internal':
        return internal_disks
    elif return_type == "external":
        return external_disks
    else:
        raise Exception("Invalid return type received. Options are 'all', 'internal', 'external'")

def get_disk_space(mount_path, return_type='percent'):
    space_dict = {}
    space = psutil.disk_usage(mount_path)
    space_dict["total"] = space.total
    space_dict["used"] = space.used
    space_dict["free"] = space.free
    space_dict["percent"] = space.percent
    return space_dict.get(return_type)

def get_temps():
    temps = psutil.sensors_temperatures()
    return temps