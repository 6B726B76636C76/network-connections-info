import yaml
from dataclasses import dataclass
from Logger.logger import logger

@dataclass
class Data:
    db_path: str
    logs_output_path: str
    loki: str
    
def config_loader() -> Data:
    config: Data
    
    try:
        with open("config.yml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            config = Data(
                db_path=data["data"]["db_path"],
                logs_output_path=data["data"]["logs_output_path"],
                loki=data["data"]["loki"]
            )
            print(config)
        return config
    except Exception as e:
        logger.error(f"{e}")
        raise