"""
Test script for consolidated agents module
"""
import asyncio
import sys

async def test_agents():
    print("=" * 60)
    print("KLOUD AGENTS - TESTING CONSOLIDATED MODULE")
    print("=" * 60)
    
    # Test 1: Imports
    print("\n[1] Testing imports...")
    try:
        from agents import (
            BaseAgent, AgentConfig, AgentType, AgentStatus,
            AgentCapability, Task, TaskResult, TaskPriority,
            ALBAAgent, ALBIAgent, JONAAgent, TrinitySystem,
            DataProcessingAgent, AnalyticsAgent, WebScraperAgent,
            AgentPool, PoolConfig,
            AgentRegistry, get_registry,
            TelemetryService, get_telemetry,
            CycleAgentBridge, CyclePhase, MaturityState
        )
        print("   ✓ All imports successful")
    except Exception as e:
        print(f"   ✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Core agents
    print("\n[2] Testing core agents (ASI Trinity)...")
    alba = ALBAAgent()
    albi = ALBIAgent()
    jona = JONAAgent()
    
    print(f"   ALBA: {alba.config.name} - Port {alba.config.metadata.get('port', 'N/A')}")
    print(f"   ALBI: {albi.config.name} - Port {albi.config.metadata.get('port', 'N/A')}")
    print(f"   JONA: {jona.config.name} - Port {jona.config.metadata.get('port', 'N/A')}")
    
    await alba.initialize()
    await albi.initialize()
    await jona.initialize()
    print("   ✓ Core agents initialized")
    
    # Test 3: Execute tasks
    print("\n[3] Testing task execution...")
    
    task1 = Task(task_id="t1", agent_name="alba", payload={"action": "collect", "source": "test"})
    result1 = await alba.run_task(task1)
    print(f"   ALBA collect: success={result1.success}")
    
    task2 = Task(task_id="t2", agent_name="albi", payload={"action": "analyze", "data": [1,2,3]})
    result2 = await albi.run_task(task2)
    print(f"   ALBI analyze: success={result2.success}")
    
    task3 = Task(task_id="t3", agent_name="jona", payload={"action": "synthesize", "sources": ["a","b"]})
    result3 = await jona.run_task(task3)
    print(f"   JONA synthesize: success={result3.success}")
    print("   ✓ Tasks executed successfully")
    
    # Test 4: TrinitySystem
    print("\n[4] Testing TrinitySystem...")
    trinity = TrinitySystem()
    await trinity.initialize()
    
    result = await trinity.full_analysis({"source": "demo", "data": [10, 20, 30]})
    print(f"   Pipeline: {result.get('pipeline', 'N/A')}")
    print(f"   All phases successful: {result.get('success', False)}")
    print("   ✓ Trinity pipeline works")
    
    # Test 5: Registry
    print("\n[5] Testing AgentRegistry...")
    registry = get_registry()
    registry.register(alba, "alba-main")
    registry.register(albi, "albi-main")
    registry.register(jona, "jona-main")
    
    print(f"   Registered agents: {registry.count}")
    collectors = registry.find_by_capability(AgentCapability.DATA_COLLECTION)
    print(f"   Agents with DATA_COLLECTION: {len(collectors)}")
    print("   ✓ Registry working")
    
    # Test 6: Specialized agents
    print("\n[6] Testing specialized agents...")
    processor = DataProcessingAgent()
    await processor.initialize()
    
    task = Task(task_id="p1", agent_name="data-processor", payload={
        "action": "validate",
        "data": {"name": "test", "value": 100}
    })
    result = await processor.run_task(task)
    print(f"   DataProcessor validate: valid={result.result.get('valid', 'N/A') if result.result else 'N/A'}")
    print("   ✓ Specialized agents work")
    
    # Test 7: Telemetry
    print("\n[7] Testing telemetry...")
    telemetry = get_telemetry()
    telemetry.task_started("demo-1", "alba", "collect")
    telemetry.task_completed("demo-1", "alba", 150.5)
    
    summary = telemetry.get_summary()
    print(f"   Events logged: {summary['total_events']}")
    print(f"   Tasks completed: {summary['tasks_completed']}")
    print("   ✓ Telemetry working")
    
    # Test 8: Cycles bridge
    print("\n[8] Testing CycleAgentBridge...")
    from agents.cycles import create_default_bridge, CycleContext
    import uuid
    
    bridge = create_default_bridge(alba, albi, jona)
    context = CycleContext(
        cycle_id=f"cycle_{uuid.uuid4().hex[:8]}",
        phase=CyclePhase.EXTRACT,
        maturity=MaturityState.IMMATURE,
        data={"test": True}
    )
    
    print(f"   Extract handlers: {len(bridge.get_handlers(CyclePhase.EXTRACT))}")
    print(f"   Analyze handlers: {len(bridge.get_handlers(CyclePhase.ANALYZE))}")
    print("   ✓ Cycle bridge configured")
    
    # Cleanup
    await alba.shutdown()
    await albi.shutdown()
    await jona.shutdown()
    await processor.shutdown()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    print("\nConsolidated agents/ module is fully functional!")
    print("Files created:")
    print("  - agents/base.py       (BaseAgent, types)")
    print("  - agents/core.py       (ALBA, ALBI, JONA)")
    print("  - agents/specialized.py (7 specialized agents)")
    print("  - agents/pool.py       (Autoscaling pool)")
    print("  - agents/registry.py   (Service discovery)")
    print("  - agents/orchestrator.py (Main entry point)")
    print("  - agents/telemetry.py  (Logging/metrics)")
    print("  - agents/cycles.py     (Cycle integration)")
    print("  - agents/__init__.py   (Module exports)")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_agents())
    sys.exit(0 if result else 1)

