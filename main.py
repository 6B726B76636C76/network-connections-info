# import ipaddress
# import os
# import tabulate
# import pprint
# import subprocess
import os
import time
import asyncio
from typing import List
from DataExporter.NetworkData import get_all_connections
from DataExporter.NetworkDataJson import get_connections_json
from DataExporter.NetworkDataModel import Connection
from config_reader import config_loader

async def main():
    #TODO app logger
    try:
        config_data = config_loader()

        while True:
            
            json_lines = await get_connections_json(db_path=config_data.db_path)
            log_file = f"{config_data.logs_output_path}/network_connections.json"
            with open(f'{log_file}', 'a') as f:
                for line in json_lines:
                    f.write(line + '\n')
            time.sleep(60)

    except KeyboardInterrupt:
        print("\nStopped.")

asyncio.run(main())

# source venv/bin/activate