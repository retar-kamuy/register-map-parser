import yaml
import sys
from typing import Dict, Any

def load() -> Dict[str, Any]:
    "Return YAML file in Dict format"
    try:
        with open('register_map_format.yml', encoding='utf-8') as file:
            obj = yaml.safe_load(file)
            return obj
    except OSError as err:
        print('Exception occurred while loading YAML...', file=sys.stderr)
        print(err, file=sys.stderr)
        sys.exit(1)
