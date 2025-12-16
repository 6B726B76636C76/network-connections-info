import ipaddress
import json
from DataExporter.NetworkData import get_all_connections


async def get_connections_json(db_path: str) -> list[str]:

    listening, local_connections, external_connections = await get_all_connections(db_path)
    
    all_connections = listening + local_connections + external_connections
    json_lines = []

    for conn in all_connections:

        if conn["status"] == "LISTEN":
            
            category = "listening"
            
        elif conn["remote_ip"] == "None":
            
            category = "other"
        
        else:
            
            try:
                ip_obj = ipaddress.ip_address(conn["remote_ip"])
                
                if ip_obj.is_loopback or ip_obj.is_private:
                    category = "local"
                
                else:
                    category = "external"
            
            except ValueError:
                category = "invalid"

        log_entry = {
            
            "timestamp": conn["timestamp"],          
            "level": "info",
            "msg": "network_connection",
            "pid": int(conn["pid"]) if conn["pid"] != "None" else None,
            "process": conn["process"],
            "local": conn["local"],
            "remote_ip": conn["remote_ip"],
            "remote": conn["remote"],
            "hostname": conn["hostname"],
            "status": conn["status"],
            "proto": conn["proto"],
            "family": conn["family"],
            "network": conn["network"],
            "address": conn["addr"],
            "category": category,
        }

        json_lines.append(json.dumps(log_entry, ensure_ascii=False))

    return json_lines