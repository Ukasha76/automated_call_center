import uuid
from typing import Dict, Any
import logging
import datetime
import time
import traceback
from supabase import create_client, Client
logger = logging.getLogger(__name__)
import os
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
async def store_RAGS_log(context: Dict[str, Any]) -> Dict:
    """
    Stores the full execution trace including router, agent, tool, steps, and substeps logs.
    Now handles multiple tool metrics entries and stores query information at the step level.
    """
    try:
        # 1. Router Logs (from session_metadata)
        session_metadata = context.get('session_metadata', {})
        initial_query = session_metadata.get('initial_query', {})
        
        router_fields = {
            'session_id': session_metadata.get('session_id'),
            'query_id': initial_query.get('query_id', ''),
            'query_routing_time_ms': session_metadata.get('query_routing_time', 0) * 1000,
            'routed_agent': session_metadata.get('routed_agent'),
            'confidence': session_metadata.get('confidence'),
            'agent_id': session_metadata.get('agent_id'),
            'query_text': initial_query.get('query_text'),
            'execution_start_time': session_metadata.get('execution_start_time'),
            'created_at': session_metadata.get('created_at')
        }

        router_response = supabase.table("router_logs").insert(router_fields).execute()
        if not router_response.data:
            raise ValueError("Failed to insert router stats")
        router_log_id = router_response.data[0].get('id')

        # 2. Agent Logs (from agent_metrics.metadata)
        agent_metadata = context.get('agent_metrics', {}).get('metadata', {})
        agent_log_id = None
        
        if agent_metadata:
            agent_log = {
                'router_log_id': router_log_id,
                'agent_id': agent_metadata.get('agent_id'),
                'tool_id': agent_metadata.get('tool_id', 'unknown'),
                'tool_name': agent_metadata.get('tool_name', 'unknown'),
                'tool_decision_duration_ms': agent_metadata.get('tool_decision_duration', 0) * 1000,
                'agent_starting_time': agent_metadata.get('agent_starting_time'),
                'agent_completion_time': agent_metadata.get('agent_completion_time', time.time()),
                'status': agent_metadata.get('status', 'completed')
            }
            
            agent_response = supabase.table("agent_logs").insert(agent_log).execute()
            agent_log_id = agent_response.data[0].get('id')

        # 3. RAG Step Logs (from metrics_package.steps_logs)
        metrics_package = context.get('agent_metrics', {}).get('tool_metrics', {})
        steps_logs = metrics_package[0].get('steps_logs', [])
        
        if agent_log_id and steps_logs:
            step_records = []
            for step in steps_logs:
                step_records.append({
                    'agent_log_id': agent_log_id,
                    'step_name': step.get('step_name'),
                    'step_duration_ms': step.get('step_duration_ms', 0),
                    'created_at': datetime.datetime.now().isoformat()
                })
            
            if step_records:
                supabase.table("rags_steps_log").insert(step_records).execute()

        return {
            "status": "success",
            "router_log_id": router_log_id,
            "agent_log_id": agent_log_id,
            "steps_recorded": len(steps_logs)
        }
        
    except Exception as e:
        logger.error(f"Failed to store RAG logs: {str(e)}\n{traceback.format_exc()}")
        return {
            "status": "error",
            "error": str(e)
        }