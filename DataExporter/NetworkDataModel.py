from dataclasses import dataclass
from datetime import datetime
from typing import List
from DataExporter.NetworkData import get_all_connections
from Geo.GeoIpData import get_ip_data_by_db, GeoData

class Connection:
    pid: int|str
    process: str
    local: str
    remote_ip: str|None
    remote: str
    hostname: str
    status: str
    proto: str
    family: str
    network: str
    address: str

@dataclass
class IncomingConnections:
    data: list

@dataclass
class OutgoingConnections:
    data: list

@dataclass
class ListeningConnections:
    data: list
