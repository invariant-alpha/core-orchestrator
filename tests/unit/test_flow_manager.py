import pytest
import os
import yaml
from core_orchestrator.flow_manager import FlowManager

@pytest.fixture
def temp_flows_dir(tmp_path):
    flows_dir = tmp_path / "flows"
    flows_dir.mkdir()
    
    test_yaml = {
        "name": "test_flow",
        "version": "1.0",
        "steps": [
            {"name": "step1", "action": "test_action", "target_topic": "test.topic"}
        ]
    }
    
    with open(flows_dir / "test.yaml", "w") as f:
        yaml.dump(test_yaml, f)
        
    return str(flows_dir)

def test_flow_manager_loads_flows(temp_flows_dir):
    manager = FlowManager(temp_flows_dir)
    flow = manager.get_flow("test_flow")
    
    assert flow is not None
    assert flow["name"] == "test_flow"
    assert len(flow["steps"]) == 1
    assert flow["steps"][0]["target_topic"] == "test.topic"

def test_flow_manager_non_existent_flow(temp_flows_dir):
    manager = FlowManager(temp_flows_dir)
    flow = manager.get_flow("non_existent")
    
    assert flow is None
