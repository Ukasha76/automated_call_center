import secrets
from datetime import datetime

def transform_metrics(original_metrics):
    transformed = {
        "execution_metrics": {
            "session_info": {
                "agent_id": original_metrics["agent_metrics"]["metadata"]["agent_id"],
                "agent_type": original_metrics["session_metadata"]["routed_agent"],
                "start_time": original_metrics["session_metadata"]["created_at"]
            },
            "tool_executions": []
        },
        "context_history": {
            "initial_query": original_metrics["session_metadata"]["initial_query"],
            "last_activity": original_metrics["session_metadata"]["last_activity"],
            "interaction_count": len(original_metrics["agent_metrics"]["tool_metrics"])
        }
    }

    for tool_metric in original_metrics["agent_metrics"]["tool_metrics"]:
        execution_record = {
            "execution_id": f"exec_{tool_metric['query_data']['timestamp'][:19].replace('-', '').replace(':', '')}_{secrets.token_hex(2)}",
            "timestamp": tool_metric["query_data"]["timestamp"],
            "tool": original_metrics["agent_metrics"]["metadata"]["tool_name"],
            "status": "completed" if tool_metric["tool_metrics"]["tool_completion_time_ms"] > 0 else "failed",
            "steps": []
        }

        # Process steps
        for step in tool_metric.get("steps_logs", []):
            step_record = {
                "name": step["step_name"],
                "duration_ms": step["step_duration_ms"],
                "status": "completed"
            }

            # Process subactions
            subactions = []
            for subaction in tool_metric.get("step_subaction_logs", []):
                subaction_record = {
                    "action": subaction["action_name"],
                    "type": subaction["action_type"],
                    "duration_ms": subaction["duration_ms"],
                    "status": "success" if subaction["success"] else "failed"
                }
                
                # Add reason if the subaction failed
                if not subaction["success"] and "reason" in subaction:
                    subaction_record["reason"] = subaction["reason"]
                
                subactions.append(subaction_record)
            
            if subactions:
                step_record["subactions"] = subactions
                # Update step status if any subactions failed
                if any(sa["status"] == "failed" for sa in subactions):
                    step_record["status"] = "failed"
                    # Add step-level reason by combining subaction reasons
                    failed_subactions = [sa for sa in subactions if sa["status"] == "failed"]
                    if len(failed_subactions) > 0:
                        step_record["reason"] = " | ".join(
                            sa.get("reason", "unknown error") 
                            for sa in failed_subactions
                        )

            execution_record["steps"].append(step_record)

        transformed["execution_metrics"]["tool_executions"].append(execution_record)

    return transformed