from pydantic import BaseModel, Field

class OrchestratorConfig(BaseModel):
    max_concurrent_tasks_per_flow: int = Field(default=10)
    saga_timeout_minutes: int = Field(default=60)
    graceful_stop_timeout_minutes: int = Field(default=5)
