from agents.sql.tools.functions.register_patient.extract_patient_info import extract_patient_info

async def check_query_relevance(query: str, current_step: str, current_tool: str, department: str, required_input:str) -> str:
   
      sql_flow = {

        'current_step':current_step,
        'current_tool':current_tool,
        'department':department,
        'required_input':required_input
      }
      response = await extract_patient_info(query,'check_relevance',sql_flow_context=sql_flow)
    
      return response['value']