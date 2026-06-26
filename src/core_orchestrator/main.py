import asyncio
import logging
import uuid
import os
from datetime import datetime

try:
    from core_bus.client import RedisBusClient
    from core_bus.schemas import EventEnvelope
except ImportError:
    RedisBusClient = None
    EventEnvelope = None

from .config import OrchestratorConfig
from .schemas import OrchestratorTaskRequest, OrchestratorTaskCompleted
from .flow_manager import FlowManager

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting core-orchestrator...")

    config = OrchestratorConfig()
    
    # Inizializza FlowManager
    base_dir = os.path.dirname(__file__)
    flows_dir = os.path.join(base_dir, "flows")
    
    # Crea la directory se non esiste, in esecuzione base (ad es. test)
    if not os.path.exists(flows_dir):
        os.makedirs(flows_dir)
        
    manager = FlowManager(flows_dir)
    
    if not RedisBusClient:
        logger.error("core-bus missing. Running without Bus.")
        return

    bus_client = RedisBusClient()
    await bus_client.connect()

    async def emit_event(event_type: str, payload: dict, corr_id: str):
        env = EventEnvelope(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            source_module="core-orchestrator",
            timestamp=datetime.utcnow(),
            correlation_id=corr_id,
            payload=payload
        )
        await bus_client.publish(event_type, env)

    async def on_task_requested(envelope: EventEnvelope):
        logger.info(f"Received task request: {envelope.correlation_id}")
        
        req = OrchestratorTaskRequest.model_validate(envelope.payload)
        
        flow = manager.get_flow(req.flow_name)
        if not flow:
            logger.error(f"Flow {req.flow_name} not found!")
            await emit_event("orchestrator.task.failed", {
                "error": f"Flow {req.flow_name} not found"
            }, req.correlation_id)
            return
            
        logger.info(f"Executing flow {req.flow_name} (version: {req.flow_version})")
        
        # Simula esecuzione steps
        steps_executed = []
        for step in flow.get("steps", []):
            step_name = step.get("name", "unknown")
            step_action = step.get("action", "unknown")
            
            logger.info(f"Flow {req.flow_name}: Executing step {step_name} ({step_action})")
            
            # Qui il vero orchestratore manderebbe un messaggio e aspetterebbe risposta (Saga)
            # Per il mock simuliamo emit fire-and-forget al topic target del step
            if "target_topic" in step:
                await emit_event(step["target_topic"], {
                    "action": step_action,
                    "input": req.input_data
                }, req.correlation_id)
            
            steps_executed.append(step_name)
            
        # Simula completamento del task
        completed = OrchestratorTaskCompleted(
            flow_name=req.flow_name,
            output_data={"status": "all_steps_dispatched"},
            steps_executed=steps_executed,
            total_cost_usd=0.0,
            duration_ms=100,
            correlation_id=req.correlation_id
        )
        
        await emit_event("orchestrator.task.completed", completed.model_dump(), req.correlation_id)

    await bus_client.subscribe("orchestrator.task.requested", "orchestrator_group", on_task_requested)

    logger.info("core-orchestrator is listening for events...")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Shutting down core-orchestrator...")
    finally:
        await bus_client.close()

if __name__ == "__main__":
    asyncio.run(main())
