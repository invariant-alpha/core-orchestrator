from pydantic import BaseModel
from typing import Literal, Dict, Any, List

class OrchestratorTaskRequest(BaseModel):
    flow_name: str
    flow_version: str = "latest"
    input_data: dict
    priority: Literal["low", "normal", "high"] = "normal"
    correlation_id: str

class OrchestratorTaskCompleted(BaseModel):
    flow_name: str
    output_data: dict
    steps_executed: List[str]
    total_cost_usd: float
    duration_ms: int
    correlation_id: str
