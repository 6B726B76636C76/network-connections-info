import psutil
import socket
import ipaddress
from datetime import datetime, timezone
from Geo.GeoIpData import get_ip_data_by_db
from Geo.GeoModel import GeoData
from Logger.logger import logger

LOOPBACK_IPS = {"127.0.0.1", "::1"}
BIND_ALL_IPS = {"0.0.0.0", "::"}


def is_loopback(ip: str | None) -> bool:
    if ip in LOOPBACK_IPS:
        return True

    if ip and ip.startswith("::ffff:"):

        ipv4_part = ip.rsplit(":", 1)[-1]
        return ipv4_part.startswith("127.")
    return False


def resolve_host(ip: str | None) -> str:
    if ip is None or is_loopback(ip) or ip in BIND_ALL_IPS:
        return "None"

    try:
        result = socket.getnameinfo((ip, 0), 0)
        hostname = result[0]

        numeric = socket.getnameinfo((ip, 0), socket.NI_NUMERICHOST)[0]

        if hostname == numeric or hostname == ip:
            logger.debug(f"No reverse DNS for {ip}")
            return "None"

        return hostname

    except socket.gaierror as e:
        logger.debug(f"Reverse lookup failed for {ip}: {e}")
        return "None"

    except Exception as e:
        logger.error(f"Unexpected error resolving {ip}: {e}")
        return "None"

def classify_process(conn) -> str:
    if conn.pid is None:
        return "system"

    try:
        p = psutil.Process(conn.pid)
        name = p.name()
        if p.pid <= 2 or (name.startswith('[') and name.endswith(']')):
            return "kernel"
        if name == "systemd":
            return "systemd"
        try:
            exe = p.exe()
            if exe and "systemd" in exe:
                return "systemd"
        except Exception as e:
            logger.error(f"{e}")

        uids = p.uids()
        if uids.real == 0 or uids.effective == 0:
            return "root"

        return name

    except psutil.AccessDenied:
        return "privileged"

    except psutil.NoSuchProcess:
        return "unknown"


async def get_all_connections(db_path: str):
    timestamp = datetime.now(timezone.utc).isoformat()

    conns = psutil.net_connections(kind='inet')
    seen = set()

    listening = []
    local_connections = []
    external_connections = []

    for c in conns:
        key = (c.fd, c.family, c.type, c.laddr, c.raddr, c.status)
        if key in seen or not c.laddr:
            continue
        seen.add(key)

        local = f"{c.laddr.ip}:{c.laddr.port}"
        remote_ip = c.raddr.ip if c.raddr else "None"
        remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "None"

        hostname = resolve_host(c.raddr.ip if c.raddr else None)
        proc_name = classify_process(c)
        pid = c.pid if c.pid is not None else "None"

        geo_db: GeoData = GeoData.localhost()
        network = "None"
        address = "None"

        if remote_ip != "None":
            try:
                ip_obj = ipaddress.ip_address(remote_ip)

                if not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast):
                    geo_db = await get_ip_data_by_db(remote_ip, db_path) or GeoData.localhost()
                    network = getattr(geo_db, "network", "None")
                    address = ", ".join(filter(None, [geo_db.city, geo_db.country])) or "None"

            except ValueError:
                logger.warning(f"Invalid IP format: {remote_ip}")

        info = {
            "timestamp": timestamp,
            "pid": pid,
            "process": proc_name,
            "local": local,
            "remote_ip": remote_ip,
            "remote": remote,
            "hostname": hostname or "None",
            "status": c.status,
            "proto": "TCP" if c.type == socket.SOCK_STREAM else "UDP",
            "family": "IPv6" if c.family == socket.AF_INET6 else "IPv4",
            "network": network,
            "addr": address,
        }

        if c.status == 'LISTEN':
            listening.append(info)

        elif remote_ip == "None":
            local_connections.append(info)

        else:
            try:

                ip_obj = ipaddress.ip_address(remote_ip)

                if ip_obj.is_loopback or ip_obj.is_private:
                    local_connections.append(info)
                else:
                    external_connections.append(info)
            except ValueError:
                local_connections.append(info)

    return listening, local_connections, external_connections