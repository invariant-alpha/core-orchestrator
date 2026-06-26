import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FlowManager:
    def __init__(self, flows_dir: str):
        self.flows_dir = flows_dir
        self._flows: Dict[str, dict] = {}
        self.load_all_flows()

    def load_all_flows(self):
        if not os.path.exists(self.flows_dir):
            logger.warning(f"Flows directory {self.flows_dir} does not exist.")
            return

        for filename in os.listdir(self.flows_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(self.flows_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        flow_def = yaml.safe_load(f)
                        flow_name = flow_def.get("name", filename.split(".")[0])
                        self._flows[flow_name] = flow_def
                        logger.info(f"Loaded flow: {flow_name}")
                except Exception as e:
                    logger.error(f"Failed to load flow {filename}: {e}")

    def get_flow(self, flow_name: str) -> Optional[dict]:
        return self._flows.get(flow_name)
