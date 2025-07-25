import traceback
import sys
import os
from pathlib import Path
import hashlib
# Add the FYP directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import StructuredTool
from agents.sql.prompt import agent_instructions
from agents.sql.llm import llm
from agents.sql.tools.doctors_details import doctor_info_tool
from agents.sql.tools.cancel_appointment import cancel_appointment_tool
from agents.sql.tools.book_appointment import book_appointment_tool
# from agents.sql.tools.register_patient import register_patient_tool
from agents.sql.tools.prescription_refill import prescription_refill_tool
from agents.sql.tools.appointmentSlots_info import appointment_slotsInfo_tool
from agents.sql.tools.appointment_rescheduling import rescheduling_appointment_tool
from agents.sql.connection import supabase
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import asyncio
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime
import json

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers for both file and console output
file_handler = logging.FileHandler('sql_agent_debug.log')
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
import time

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class SQLAgent:
    def __init__(self, session_context: Optional[Dict] = None):
        """Initialize with optional session context"""
        logger.info("Creating SQL Agent instance")
        self.session_context = session_context or {}
        logger.debug(f"Initial session context: {self.session_context}")
        self._initialized = False
        self.tools = None
        self.memory = None
        self.agent_executor = None
    
    @classmethod
    async def create(cls, session_context: Optional[Dict] = None) -> 'SQLAgent':
        """Factory method to create and initialize a SQLAgent instance"""
        try:
            logger.info("Creating SQL Agent instance")
            self = cls(session_context)
            await self.initialize()
            return self
        except Exception as e:
            logger.error(f"Error creating SQL Agent: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def initialize(self) -> None:
        """Asynchronously initialize the agent"""
        if self._initialized:
            return

        try:
            # Initialize Supabase connection
            logger.info("Initializing Supabase connection")
            await supabase.initialize()

            # Initialize tools
            logger.info("Initializing tools")
            self.tools = [
                doctor_info_tool,
                cancel_appointment_tool,
                book_appointment_tool,
                prescription_refill_tool,
                appointment_slotsInfo_tool,
                rescheduling_appointment_tool
            ]
            logger.debug(f"Tools initialized: {len(self.tools)}")

            # Initialize memory with session context
            logger.info("Initializing memory")
            self.memory = self._initialize_memory()
            logger.debug("Memory initialized")

            # Create prompt template
            logger.info("Creating prompt template")
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=agent_instructions),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            # Create agent with proper tool input handling
            logger.info("Creating agent")
            agent = create_openai_tools_agent(
                llm=llm,
                tools=self.tools,
                prompt=prompt
            )

            # Create agent executor with async support
            logger.info("Creating agent executor")
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                return_intermediate_steps=True,  # Enable tracking of intermediate steps
                handle_tool_error=True  # Enable error handling for tools
            )

            self._initialized = True
            logger.info("SQL Agent initialization complete")

        except Exception as e:
            logger.error(f"Error initializing SQL Agent: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def verify(self) -> bool:
        """Verify agent is properly initialized"""
        try:
            # Check required components
            if not all([self.tools, self.memory]):
                logger.error("SQL Agent missing required components")
                return False
                
            # Check database connection
            if not hasattr(supabase, '_client') or not supabase._client:
                logger.error("SQL Agent: No database connection")
                return False
                
            logger.info("SQL Agent verification successful")
            return True
            
        except Exception as e:
            logger.error(f"SQL Agent verification failed: {str(e)}")
            return False

    def _initialize_tools(self):
        """Initialize and validate all tools"""
        tools = [
            doctor_info_tool,
            appointment_slotsInfo_tool,
            book_appointment_tool,  
            prescription_refill_tool,
            cancel_appointment_tool,
            rescheduling_appointment_tool
        ]

        for tool in tools:
            if not hasattr(tool, 'name'):
                raise ValueError(f"Tool {tool} is not properly initialized")
            if not hasattr(tool, 'coroutine') and not hasattr(tool, '_run'):
                raise ValueError(f"Tool {tool.name} is missing required coroutine/run method")
        return tools

    def _initialize_memory(self):
        """Configure conversation memory with session context"""
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Load previous conversation if exists in session
        if "chat_history" in self.session_context:
            for exchange in self.session_context["chat_history"]:
                if "query" in exchange and "response" in exchange:
                    memory.chat_memory.add_message(HumanMessage(content=exchange["query"]))
                    memory.chat_memory.add_message(AIMessage(content=exchange["response"]))
        
        return memory

    async def handle_query(self, query_data: Dict) -> Dict:
        logger.info("SQL Agent: Received query")
        logger.debug(f"Query data: {query_data}")

        try:

            query_text = query_data.get('text', '')
            context_updates = query_data.get('context', {}).get('context_updates', {})

            agent_metadata = query_data.get('context', {}).get('agent_metadata', {})


            is_new_session = False
            agent_metadata = None

            is_new_session = query_data.get('context', {}).get('is_new_session')

            if is_new_session:
                agent_starting_time= time.time()


            # Update session context
            if 'context' in query_data:
                self.session_context.update(query_data['context'])
                logger.debug(f"Updated session context: {self.session_context}")

            if context_updates and "output" in context_updates:
                query_text = context_updates["output"]

            agent_input = {
                "query_text": query_text,
                "context": context_updates or {}
            }

            logger.debug(f"Prepared agent input: {agent_input}")

            tool_map = {
                "booking_appointment": book_appointment_tool,
                "prescription_refill": prescription_refill_tool,
                "doctor_info": doctor_info_tool,
                "appointment_slots_info": appointment_slotsInfo_tool,
                "cancel_appointment": cancel_appointment_tool,
                "appointment_rescheduling": rescheduling_appointment_tool
            }

            current_tool_name = context_updates.get("current_tool")
            tool_function = tool_map.get(current_tool_name)

            if tool_function:
                correct_input = {
                    "input": {
                        "query_text": agent_input["query_text"],
                        "context": agent_input["context"]
                    }
                }
                raw_response = await tool_function.arun(correct_input)
                response = json.loads(raw_response)
            else:
                logger.debug("Running query through agent executor")
                context_updates['tool_decison_start_time'] = time.time()
                agent_input["context"] = context_updates
                tool_starting_time = time.time()

                agent_input_json = json.dumps(agent_input)
                raw_response = await self.agent_executor.ainvoke({"input": agent_input_json})
                
                response = json.loads(raw_response["output"])

                tool_decision_duration = response.get('decision_duration_ms', '')
                routed_tool_name = response.get('current_tool', '')

            # Extract response details
            status = response.get("status", '')
            response_text = response.get('output', '')
            collected_data = response.get("collected_data", {})
            
            # Store chat messages in memory
            self.memory.chat_memory.add_message(HumanMessage(content=query_text))
            self.memory.chat_memory.add_message(AIMessage(content=response_text))

            # Prepare step metrics
            step_metrics = response.get("step_metrics", {})
            steps_logs = []
            step_subaction_logs = []

            # If this is part of a multi-step tool, get the current step
            current_step = response.get("current_step")
            

            #storing individual steps of tool
            if step_metrics.get('step_duration_ms'):
            # if current_step:
                steps_logs.append({
                    "step_name": response.get("current_step", "Unknown Step"),
                    
                    "step_duration_ms": step_metrics['step_duration_ms']
                })
                # if step_metrics.get('step_duration_ms'):
                #     "step_duration_ms": step_metrics['step_duration_ms']

            # Add subactions if they exist
            for subaction in step_metrics.get("subactions", []):
                step_subaction_logs.append({
                    "action_name": subaction.get("action_name"),
                    "action_type": subaction.get("action_type"),
                    "success": subaction.get("success"),
                    "reason":subaction.get("reason"),
                    "duration_ms": subaction.get("duration_ms"),
                })


            # Prepare chat history
            chat_history = {
                'query_id': query_data.get('context', {}).get('query_id', {}),
                'query': query_text,
                'response': response_text,
                'timestamp': datetime.now().isoformat()
            }
            
            # Prepare context updates
            context = {
                "current_step": current_step,
                "collected_data": collected_data,
                "current_tool": response.get("current_tool")
            }
           

            # For book appointment tool
            # if response.get("sub_step"):
            if step_metrics.get('registration_substep'):
                context.update({
                    "registration_substep": step_metrics.get('registration_substep'),
                    "registration_data": step_metrics.get('registration_data')
                })

            # Prepare the full metrics package
            metrics_package = {
                "query_data":chat_history,
                "steps_logs": steps_logs,
                "step_subaction_logs": step_subaction_logs
            }

                        # Store agent meta data

            if is_new_session:
                # Initialize agent metadata with required fields
                agent_metadata = {
                    'agent_starting_time': agent_starting_time,
                    'agent_id': query_data.get('context', {}).get('agent_id', 'unknown'),
                    'agent_name': 'SQL',
                    'query_id': query_data.get('context', {}).get('query_id'),
                    'query_text': query_text,
                    'tool_id': self._generate_tool_id(query_text),
                    'tool_name': routed_tool_name or 'unknown'
                }
                
                # Add timing metrics if available
                if 'tool_decision_duration' in locals():
                    agent_metadata['tool_decision_duration'] = tool_decision_duration
                if 'tool_starting_time' in locals():
                    agent_metadata['tool_starting_time'] = tool_starting_time
            else:
                # Get existing metadata or initialize empty dict
                agent_metadata = query_data.get('context', {}).get('agent_metadata', {})

            # Update completion times if resolved
            if status == 'resolved':
                current_time = time.time()
                agent_metadata.update({
                    'agent_completion_time': current_time,
                    'tool_completion_time': current_time,
                    'status': 'completed'
                })
                
            response = {
                "response": response_text,
                "context_updates": context,
                "metrics": metrics_package,
                "suggested_next": None,
                "status": status,
                "chat_history": chat_history
            }

            if is_new_session:
                response["agent_metadata"] = agent_metadata

            return response


        except Exception as e:
            logger.error(f"Error in handle_query: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "response": f"I encountered an error: {str(e)}",
                "context_updates": {},
                "suggested_next": None,
                "status": "error"
            }

    def _generate_tool_id(self, query: str) -> str:
        """Generate a unique tool ID based on query, tool name, and timestamp"""
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        query_hash = hashlib.md5(query.encode()).hexdigest()[:6]
        return f"tool_{timestamp}_{query_hash}"


    def _extract_context_updates(self, response_text: str, status: str) -> Dict:
        updates = {}

        # Detect patient registration
        if "successfully registered" in response_text.lower():
            updates["status"] = "registered"
            # Extract patient ID if possible
            id_match = re.search(r"ID:? (\d+)", response_text)
            if id_match:
                updates["patient_id"] = id_match.group(1)

        # Detect appointment booking
        elif "appointment booked" in response_text.lower() or "appointment confirmed" in response_text.lower():
            updates["last_action"] = "appointment_booking"
            # Extract appointment details if possible
            date_match = re.search(r"on (\d{4}-\d{2}-\d{2})", response_text)
            if date_match:
                updates["last_appointment"] = date_match.group(1)

        # Extract doctor details only if status is resolved
        if status == "resolved":  
            updates["doctor_name"] = "to be added"
            updates["output"] = f"Doctor information extracted successfully here is the details {response_text}"
        else:
            updates["output"] = "No doctor information found."
        

        return updates

# Router-compatible interface
# Configure logging
logger = logging.getLogger(__name__)

async def handle_query(query_data: Dict) -> Dict:
    """
    Public interface for router compatibility
    Args:
        query_data: {
            "text": "the user query",
            "context": {"session_id": "abc123", ...},
            "history": [previous exchanges]
        }
    Returns:
        Dict: {
            "response": "the generated response",
            "context_updates": {"new_info": "value"},
            "suggested_next": "optional department suggestion"
        }
    """
    logger.info("SQL Agent: Received query")
    logger.debug(f"Query data: {query_data}")
    
    try:
        # Get or create agent instance
        agent = await get_agent()
        
        # Ensure agent is initialized
        if not agent._initialized:
            logger.info("Initializing SQL Agent")
            await agent.initialize()
        
        # Update context if provided
        if "context" in query_data:
            agent.session_context.update(query_data["context"])
            logger.debug(f"Updated session context: {agent.session_context}")
        
        logger.info("Forwarding query to SQL Agent instance")
        response = await agent.handle_query(query_data)
        logger.info("Received response from SQL Agent instance")
        logger.debug(f"Agent response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error in SQL Agent handle_query: {str(e)}")
        return {
            "response": f"Appointment system error: {str(e)}. Please try again later.",
            "context_updates": {},
            "suggested_next": "HUMAN"
        }

async def get_agent() -> SQLAgent:
    """Get the agent instance for routing system"""
    if 'sql_agent_instance' not in globals():
        global sql_agent_instance
        sql_agent_instance = await SQLAgent.create()
    return sql_agent_instance

if __name__ == "__main__":
    # Test mode with basic session simulation
    print("Appointment Management Agent - Test Mode")
    print("Type 'exit' to end the session\n")
    
    async def async_main():
        agent = SQLAgent()
        while True:
            try:
                user_input = input("Patient: ").strip()
                if not user_input:
                    continue
                    
                if user_input.lower() in ["exit", "bye"]:
                    print("Agent: Goodbye!")
                    break
                    
                response = await agent.handle_query({"text": user_input})
                print(f"Agent: {response['response']}")
                
            except KeyboardInterrupt:
                print("\nSession ended by user")
                break
            except Exception as e:
                print(f"Critical error: {str(e)}")
                break

    asyncio.run(async_main())