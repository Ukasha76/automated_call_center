import uuid
from typing import Dict, Any
import logging

import time
from supabase import create_client, Client
logger = logging.getLogger(__name__)
import os
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

async def store_full_trace(context: Dict[str, Any]) -> Dict:
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
                # 'query_id': agent_metadata.get('query_id'),
                # 'query_text': agent_metadata.get('query_text'),
                'tool_id': agent_metadata.get('tool_id', 'unknown'),
                'tool_name': agent_metadata.get('tool_name', 'unknown'),
                'tool_decision_duration_ms': agent_metadata.get('tool_decision_duration', 0) * 1000,
                'agent_starting_time': agent_metadata.get('agent_starting_time'),
                'agent_completion_time': agent_metadata.get('agent_completion_time', time.time()),
                'status': agent_metadata.get('status', 'completed')
            }
            
            agent_response = supabase.table("agent_logs").insert(agent_log).execute()
            agent_log_id = agent_response.data[0].get('id')

        # 3. Tool Logs (from context_updates and agent_metadata)
        tool_log_id = None
        if agent_log_id:
            tool_log = {
                'agent_log_id': agent_log_id,
                'tool_id': agent_metadata.get('tool_id', 'unknown'),
                'routed_tool_name': context.get('context_updates', {}).get('current_tool'),
                'status': 'completed'
            }
            
            if 'tool_starting_time' in agent_metadata and 'tool_completion_time' in agent_metadata:
                tool_log.update({
                    'tool_starting_time': agent_metadata['tool_starting_time'],
                    'tool_completion_time': agent_metadata['tool_completion_time'],
                    'total_tool_execution_time_ms': (
                        agent_metadata['tool_completion_time'] - agent_metadata['tool_starting_time']
                    ) * 1000
                })
            
            tool_response = supabase.table("tool_logs").insert(tool_log).execute()
            tool_log_id = tool_response.data[0].get('id')

            # 4. Process all tool metrics entries (each representing a query)
            tool_metrics_list = context.get('agent_metrics', {}).get('tool_metrics', [])
            for tool_metrics in tool_metrics_list:
                query_data = tool_metrics.get('query_data', {})
                
                # Create step log for each query with query information
                for step in tool_metrics.get('steps_logs', []):
                    step_log = {
                        'tool_log_id': tool_log_id,
                        'step_name': step.get('step_name'),
                        'step_duration_ms': step.get('step_duration_ms'),
                        'query_id': query_data.get('query_id'),
                        'query_text': query_data.get('query'),
                        'response_text': query_data.get('response')
                    }
                    step_response = supabase.table("step_logs").insert(step_log).execute()
                    step_id = step_response.data[0].get('id')

                    # Process substeps for this query
                    for sub in tool_metrics.get('step_subaction_logs', []):
                        substep_log = {
                            'step_log_id': step_id,
                            'action_name': sub.get('action_name'),
                            'action_type': sub.get('action_type'),
                            'success': sub.get('success', True),
                            'reason': str(sub.get('reason'))[:500] if sub.get('reason') and not sub.get('success', True) else None,
                            'duration_ms': sub.get('duration_ms')
                        }
                        supabase.table("step_subactions").insert(substep_log).execute()

        return {
            'success': True,
            'router_log_id': router_log_id,
            'agent_log_id': agent_log_id,
            'tool_log_id': tool_log_id
        }

    except Exception as e:
        logger.error(f"Failed to store full trace: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'router_log_id': None,
            'agent_log_id': None,
            'tool_log_id': None
        }
