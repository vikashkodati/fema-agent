"""
AI Task Manager Agent
Demostrates OpenAI SDK usage with tool calling
"""

from openai import OpenAI
from dotenv import load_dotenv
from taskmanager import TaskManager
import os
import json

load_dotenv()


class AITaskAgent:
    """
    An AI agent that manages tasks using OpenAI's tool calling capabilities
    """

    def __init__(self):
        self.task_manager = TaskManager()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task with optional priority",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the task",
                            },
                            "priority": {
                                "type": "string",
                                "description": "Priority level (high/medium/low)",
                                "enum": ["high", "medium", "low"],
                            },
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks sorted by priority and completion status",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to complete",
                            }
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_task_statistics",
                    "description": "Get task statistics and encouraging messages",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "retrieve_recovery_info",
                    "description": "Retrieves relevant disaster recovery planning guidance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Question about recovery plans or compliance",
                            }
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

        # execute the function
        def execute_tool(self, tool_call):
            # Map tool calls to TaskManager methods
            function_name = tool_call.function.name
            args = (
                json.loads(tool_call.function.arguments)
                if tool_call.function.arguments
                else {}
            )

            # Execute the corresponding TaskManager method
            if function_name == "add_task":
                return self.task_manager.add_task(
                    title=args.get("title"), priority=args.get("priority", "medium")
                )
            elif function_name == "list_tasks":
                return self.task_manager.list_tasks()
            elif function_name == "complete_task":
                return self.task_manager.complete_task(task_id=args["task_id"])
            elif function_name == "get_task_statistics":
                return self.task_manager.get_task_statistics()
            elif function.name == "retrieve_recovery_info":
                return self.task_manager.retrieve_recovery_info()
            else:
                return f"Unknown function: {function_name}"

        def chat(self, user_message: str) -> str:
            """
            Process user message and return ai response using the tool calling capabilities
            """
            try:
                # Initialize conversation with system and user messages
                messages = [
                    {
                        "role": "system",
                        "content": """
                        You are a helpful AI assistant that manages tasks for users. You can add tasks, list tasks, 
                        mark tasks as completed, and provide productivity insights

                        You have access to the following tools:
                        - add_task: Add a new task with optional priority
                        - list_tasks: List all tasks sorted by priority and completion status
                        - complete_task: Mark a task as completed
                        - get_task_statistics: Get task statistics and encouraging messages
                        For general conversation or questions unrelated to task management and productivity respond directly without using tools.
                        Be friendly, encouraging and helpful.
                        """,
                    },
                    {"role": "user", "content": user_message},
                ]

                # Get initial response from model
                response = self.client.responses.create(
                    model="gpt-4.1",
                    input=messages,
                    tools=self.tools,
                    tool_choice="auto",
                )

                # Check if model wants to use a tool
                if (
                    response.output
                    and response.output[0].get("type") == "function_call"
                ):
                    # Extract tool call details
                    tool_call = response.output[0]
                    args = json.loads(tool_call.arguments)

                    # Execute the tool and get result
                    tool_result = self.execute_tool(tool_call)

                    # Add tool call and result to conversation
                    messages.append(tool_call)  # Add model's function call
                    messages.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": str(tool_result),
                        }
                    )

                    # Get final response incorporating tool result
                    final_response = self.client.responses.create(
                        model="gpt-4.1", input=messages, tools=self.tools
                    )
                    return final_response.output_text

                # If no tool was called, return direct response
                return response.output_text

            except Exception as e:
                # Friendly error handling
                return f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or rephrase your request."
        
        def retrieve_recovery_info(query: str) -> str:
            assistant = self.client.beta.assistants.create(
                name="Disaster Recovery Assistant",
                instructions="You help answer disaster recovery planning and compliance questions.",
                tools=[{"type": "retrieval"}],
                model="gpt-4-turbo",
                vector_store_ids=[os.getenv("VECTORIZE_PIPELINE_ID")],
            )

            thread = self.client.beta.threads.create()
            
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=query
            )

            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )

            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            return messages.data[0].content[0].text.value
