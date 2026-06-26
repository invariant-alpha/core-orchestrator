# Prompt Operativo — CORE_ORCHESTRATOR

## Ruolo nel Sistema
Core Engine (Livello 1). È il Cervello del sistema e l'**Unico modulo** a conoscere i flussi di business (freelance, sfw_content, nsfw_content). 
Traduce input di alto livello in richieste tecniche per l'executor/dag manager e altri componenti. Gestisce il lifecycle dei flussi di business.
Carica le definizioni dei flussi da file YAML in `orchestrator/flows/`.

## Lifecycle
Controllabile (RUNNING, PAUSED, STOPPED). 

## Configurazione
```python
from pydantic import BaseModel, Field

class OrchestratorConfig(BaseModel):
    max_concurrent_tasks_per_flow: int = Field(default=10)
    saga_timeout_minutes: int = Field(default=60)
    graceful_stop_timeout_minutes: int = Field(default=5)
```

## Dipendenze
- Moduli già implementati: `core-bus`.
- PyYAML per leggere i config.

## Schema Pydantic Completo
```python
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
```

## Contratto Redis Streams
- Stream sottoscritti: `orchestrator.task.requested`, `module.lifecycle.requested`, `config.update.requested`
- Stream pubblicati: `orchestrator.task.completed`, `orchestrator.task.failed`, `config.updated`
- Invia eventi ad altri moduli (es. `executor.task.requested`, `ai.request.created` a seconda del flusso YAML).
- DLQ: `system.dlq.orchestrator`

## Flusso Principale
1. Carica i file YAML da `src/core_orchestrator/flows/`.
2. Riceve `orchestrator.task.requested` per un flow_name.
3. Trova la definizione YAML del flow.
4. Genera e pubblica gli eventi tecnici (es. verso `core-executor` o `worker-orchestrator`) in base agli step definiti nello YAML. 
   *(In questo mock, simuliamo l'avanzamento emettendo l'evento al downstream).*

## Struttura Directory
```
core-orchestrator/
├── Dockerfile
├── pyproject.toml
├── docs/
│   └── prompts/
│       └── CORE_ORCHESTRATOR.md
├── src/
│   └── core_orchestrator/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── schemas.py
│       ├── flow_manager.py
│       └── flows/
│           ├── freelance.yaml
│           ├── sfw_content.yaml
│           └── nsfw_content.yaml
└── tests/
    ├── unit/
    └── integration/
```

## Test Richiesti
- Unit test: parser dei YAML dei flussi.
- Unit test: orchestrazione task richiesta.

## Definition of Done
- [ ] Tutti i test passano
- [ ] Parser YAML funzionante
- [ ] Integrazione col bus
