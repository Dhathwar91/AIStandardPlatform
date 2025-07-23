import gradio as gr
import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import nest_asyncio

nest_asyncio.apply()
load_dotenv()

class MCPChatInterface:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic()
        self.available_tools: List[Dict] = []
        self.available_prompts: List[Dict] = []
        self.available_resources: List[Dict] = []
        self.chat_history: List[Dict] = []
        self.is_connected = False
        self.uploaded_files: List[Dict] = []  # Store uploaded file info

    async def connect_to_server(self):
        """Connect to the MCP server and initialize available tools, prompts, and resources"""
        try:
            server_params = StdioServerParameters(
                command="uv",
                args=["run", "server.py"],
                env=None,
            )

            self.server_params = server_params
            return "✅ Server connection configured successfully!"
        except Exception as e:
            return f"❌ Error configuring server: {str(e)}"

    async def initialize_mcp_session(self):
        """Initialize MCP session and fetch available tools, prompts, resources"""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Get prompts
                    try:
                        prompts_response = await session.list_prompts()
                        self.available_prompts = [
                            {
                                "name": prompt.name,
                                "description": getattr(prompt, 'description', 'No description available')
                            }
                            for prompt in prompts_response.prompts
                        ]
                    except Exception as e:
                        print(f"Error getting prompts: {e}")
                        self.available_prompts = []

                    # Get resources
                    try:
                        resources_response = await session.list_resources()
                        self.available_resources = [
                            {
                                "name": resource.name,
                                "description": getattr(resource, 'description', 'No description available'),
                                "uri": resource.uri
                            }
                            for resource in resources_response.resources
                        ]
                    except Exception as e:
                        print(f"Error getting resources: {e}")
                        self.available_resources = []

                    # Get tools
                    try:
                        tools_response = await session.list_tools()
                        self.available_tools = [
                            {
                                "name": tool.name,
                                "description": tool.description,
                                "input_schema": tool.inputSchema
                            }
                            for tool in tools_response.tools
                        ]
                    except Exception as e:
                        print(f"Error getting tools: {e}")
                        self.available_tools = []

                    self.is_connected = True
                    return True
        except Exception as e:
            print(f"Error initializing MCP session: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def process_chat_message(self, message: str, history: List[Dict]):
        """Process a chat message and return the response"""
        if not await self.initialize_mcp_session():
            return history + [{"role": "user", "content": message}, {"role": "assistant", "content": "❌ Failed to connect to MCP server. Please try again."}]

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    await session.initialize()

                    # Prepare tools for Anthropic
                    tools_for_anthropic = [
                        {
                            "name": tool["name"],
                            "description": tool["description"],
                            "input_schema": tool["input_schema"]
                        }
                        for tool in self.available_tools
                    ]

                    # Add context about uploaded files if any
                    context_message = message
                    if self.uploaded_files:
                        file_context = "\n\nUploaded files context:\n"
                        for file_info in self.uploaded_files:
                            file_context += f"- {file_info['name']}: {file_info.get('preview', 'No preview available')}\n"
                        context_message = message + file_context

                    messages = [{'role': 'user', 'content': context_message}]
                    response = self.anthropic.messages.create(
                        max_tokens=2024,
                        model='claude-3-5-sonnet-20241022',
                        tools=tools_for_anthropic,
                        messages=messages
                    )

                    assistant_response = ""
                    process_query = True

                    while process_query:
                        assistant_content = []
                        for content in response.content:
                            if content.type == 'text':
                                assistant_response += content.text
                                assistant_content.append(content)
                                if len(response.content) == 1:
                                    process_query = False
                            elif content.type == 'tool_use':
                                assistant_content.append(content)
                                messages.append({'role': 'assistant', 'content': assistant_content})
                                
                                tool_name = content.name
                                tool_args = content.input
                                tool_id = content.id

                                assistant_response += f"\n🔧 Calling tool: {tool_name}\n"
                                
                                # Call the tool through MCP
                                result = await session.call_tool(tool_name, arguments=tool_args)
                                
                                messages.append({
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "tool_result",
                                            "tool_use_id": tool_id,
                                            "content": result.content
                                        }
                                    ]
                                })

                                response = self.anthropic.messages.create(
                                    max_tokens=2024,
                                    model='claude-3-5-sonnet-20241022',
                                    tools=tools_for_anthropic,
                                    messages=messages
                                )

                                if len(response.content) == 1 and response.content[0].type == "text":
                                    assistant_response += response.content[0].text
                                    process_query = False

                    return history + [{"role": "user", "content": message}, {"role": "assistant", "content": assistant_response}]

        except Exception as e:
            error_msg = f"❌ Error processing message: {str(e)}"
            return history + [{"role": "user", "content": message}, {"role": "assistant", "content": error_msg}]

    def get_tools_info(self):
        """Return formatted information about available tools"""
        if not self.available_tools:
            return "No tools available. Please connect to the server first."
        
        info = "🔧 **Available Tools:**\n\n"
        for tool in self.available_tools:
            info += f"**{tool['name']}**\n"
            info += f"Description: {tool['description']}\n"
            if 'input_schema' in tool and 'properties' in tool['input_schema']:
                info += f"Parameters: {', '.join(tool['input_schema']['properties'].keys())}\n"
            info += "\n"
        return info

    def get_prompts_info(self):
        """Return formatted information about available prompts"""
        if not self.available_prompts:
            return "No prompts available. Please connect to the server first."

        info = "💬 **Available Prompts:**\n\n"
        for prompt in self.available_prompts:
            info += f"**{prompt['name']}**\n"
            info += f"Description: {prompt['description']}\n\n"
        return info

    async def use_prompt_template(self, prompt_name: str, **kwargs):
        """Use a prompt template with given arguments"""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Get the prompt with arguments
                    prompt_result = await session.get_prompt(prompt_name, arguments=kwargs)

                    # Extract the prompt content
                    if hasattr(prompt_result, 'messages') and prompt_result.messages:
                        # If it returns messages, combine them
                        content = "\n".join([
                            msg.content.text if hasattr(msg.content, 'text') else str(msg.content)
                            for msg in prompt_result.messages
                        ])
                    elif hasattr(prompt_result, 'content'):
                        # If it has direct content
                        content = prompt_result.content
                    else:
                        # If it's a simple string prompt or other format
                        content = str(prompt_result)

                    return content
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Detailed error: {error_details}")
            return f"❌ Error using prompt template: {str(e)}"

    def get_resources_info(self):
        """Return formatted information about available resources"""
        if not self.available_resources:
            return "No resources available. Please connect to the server first."
        
        info = "📁 **Available Resources:**\n\n"
        for resource in self.available_resources:
            info += f"**{resource['name']}**\n"
            info += f"URI: {resource['uri']}\n"
            info += f"Description: {resource['description']}\n\n"
        return info

# Initialize the MCP interface
mcp_interface = MCPChatInterface()

def create_interface():
    """Create and return the Gradio interface"""
    
    with gr.Blocks(title="MCP Chat Interface", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🤖 MCP Chat Interface")
        gr.Markdown("Chat with your MCP server and explore available tools, prompts, and resources.")
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    height=500,
                    show_label=False,
                    container=True,
                    type="messages"
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Type your message here...",
                        show_label=False,
                        scale=4,
                        container=False
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Add file upload section
                with gr.Row():
                    file_upload = gr.File(
                        label="📎 Attach Documents",
                        file_types=[".pdf", ".txt", ".docx", ".doc", ".md"],
                        file_count="multiple",
                        scale=3
                    )
                    upload_btn = gr.Button("📤 Upload & Analyze", variant="secondary", scale=1)
                
                clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### 🔍 Explore MCP Server")

                tools_btn = gr.Button("🔧 Show Available Tools", variant="secondary")
                prompts_btn = gr.Button("💬 Show Available Prompts", variant="secondary")
                resources_btn = gr.Button("📁 Show Available Resources", variant="secondary")

                info_display = gr.Markdown("Click the buttons above to explore server capabilities.")

                gr.Markdown("### 📄 Uploaded Documents")
                uploaded_files_display = gr.Markdown("No documents uploaded yet.")

                gr.Markdown("### 🎭 Use Prompt Templates")

                # Movie Actor Analysis Prompt
                with gr.Group():
                    gr.Markdown("**Movie Actor Analysis**")
                    actor_input = gr.Textbox(
                        placeholder="Enter actor name (e.g., Leonardo DiCaprio)",
                        label="Actor Name",
                        scale=1
                    )
                    analyze_actor_btn = gr.Button("🎬 Analyze Actor", variant="primary")

                # Code Review Prompt
                with gr.Group():
                    gr.Markdown("**Code Review**")
                    code_input = gr.Textbox(
                        placeholder="Enter code to review",
                        label="Code",
                        lines=3
                    )
                    review_code_btn = gr.Button("🔍 Review Code", variant="primary")

                # Debug Assistant Prompt
                with gr.Group():
                    gr.Markdown("**Debug Assistant**")
                    error_input = gr.Textbox(
                        placeholder="Enter error message",
                        label="Error Message",
                        lines=2
                    )
                    debug_error_btn = gr.Button("🐛 Debug Error", variant="primary")

        # Event handlers
        def respond(message, history):
            if message.strip():
                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(mcp_interface.process_chat_message(message, history))
                    return result, ""
                finally:
                    loop.close()
            return history, message

        def handle_file_upload(files, history):
            """Handle file upload and process documents"""
            if not files:
                return history, "No files selected."
            
            uploaded_info = "📄 **Uploaded Documents:**\n\n"
            processed_files = []
            
            for file in files:
                if file is not None:
                    file_name = os.path.basename(file.name)
                    file_size = os.path.getsize(file.name) if os.path.exists(file.name) else 0
                    
                    # Read file content based on type
                    try:
                        if file_name.lower().endswith('.pdf'):
                            content_preview = f"PDF file: {file_name} ({file_size} bytes)"
                        elif file_name.lower().endswith(('.txt', '.md')):
                            with open(file.name, 'r', encoding='utf-8') as f:
                                content = f.read()
                                content_preview = content[:200] + "..." if len(content) > 200 else content
                        else:
                            content_preview = f"Document: {file_name} ({file_size} bytes)"
                        
                        file_info = {
                            'name': file_name,
                            'path': file.name,  # This is the actual temporary file path
                            'preview': content_preview,
                            'size': file_size
                        }
                        
                        processed_files.append(file_info)
                        
                        uploaded_info += f"✅ **{file_name}**\n"
                        uploaded_info += f"   Size: {file_size} bytes\n"
                        uploaded_info += f"   Path: {file.name}\n"  # Show the actual path for debugging
                        uploaded_info += f"   Preview: {content_preview[:100]}...\n\n"
                        
                    except Exception as e:
                        uploaded_info += f"❌ **{file_name}**: Error reading file - {str(e)}\n\n"
            
            # Store uploaded files in the interface
            mcp_interface.uploaded_files = processed_files
            
            # Add to chat history
            if processed_files:
                file_names = [f['name'] for f in processed_files]
                user_message = f"📎 Uploaded {len(processed_files)} document(s): {', '.join(file_names)}"
                assistant_message = f"✅ Successfully processed {len(processed_files)} document(s). You can now ask questions about these files or request analysis using their full paths:\n\n"
                
                for file_info in processed_files:
                    assistant_message += f"• **{file_info['name']}**: `{file_info['path']}`\n"
                
                assistant_message += "\nExample: 'Analyze the document at path: [file_path]' or 'What is the summary of [filename]?'"
                
                new_history = history + [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": assistant_message}
                ]
                
                return new_history, uploaded_info
            else:
                return history, "❌ No files were successfully processed."

        def clear_chat():
            mcp_interface.uploaded_files = []  # Clear uploaded files
            return [], "", "No documents uploaded yet."

        def show_tools():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(mcp_interface.initialize_mcp_session())
                return mcp_interface.get_tools_info()
            finally:
                loop.close()

        def show_prompts():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(mcp_interface.initialize_mcp_session())
                return mcp_interface.get_prompts_info()
            finally:
                loop.close()

        def show_resources():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(mcp_interface.initialize_mcp_session())
                return mcp_interface.get_resources_info()
            finally:
                loop.close()

        def use_actor_prompt(actor_name, history):
            if not actor_name.strip():
                return history, "Please enter an actor name"

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Get the prompt template
                prompt_content = loop.run_until_complete(
                    mcp_interface.use_prompt_template("analyze_actor", actor_name=actor_name)
                )

                # Process the prompt through Claude to get the actual analysis
                response = mcp_interface.anthropic.messages.create(
                    max_tokens=2024,
                    model='claude-3-5-sonnet-20241022',
                    messages=[{'role': 'user', 'content': prompt_content}]
                )

                # Extract Claude's response
                claude_response = response.content[0].text

                # Add both the user request and Claude's analysis to chat
                new_history = history + [
                    {"role": "user", "content": f"Analyze actor: {actor_name}"},
                    {"role": "assistant", "content": claude_response}
                ]
                return new_history, ""
            except Exception as e:
                error_msg = f"❌ Error generating actor analysis: {str(e)}"
                new_history = history + [
                    {"role": "user", "content": f"Analyze actor: {actor_name}"},
                    {"role": "assistant", "content": error_msg}
                ]
                return new_history, ""
            finally:
                loop.close()

        def use_code_review_prompt(code, history):
            if not code.strip():
                return history, "Please enter code to review"

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Get the prompt template
                prompt_content = loop.run_until_complete(
                    mcp_interface.use_prompt_template("review_code", code=code)
                )

                # Process the prompt through Claude to get the actual review
                response = mcp_interface.anthropic.messages.create(
                    max_tokens=2024,
                    model='claude-3-5-sonnet-20241022',
                    messages=[{'role': 'user', 'content': prompt_content}]
                )

                # Extract Claude's response
                claude_response = response.content[0].text

                new_history = history + [
                    {"role": "user", "content": "Code review request"},
                    {"role": "assistant", "content": claude_response}
                ]
                return new_history, ""
            except Exception as e:
                error_msg = f"❌ Error generating code review: {str(e)}"
                new_history = history + [
                    {"role": "user", "content": "Code review request"},
                    {"role": "assistant", "content": error_msg}
                ]
                return new_history, ""
            finally:
                loop.close()

        def use_debug_prompt(error, history):
            if not error.strip():
                return history, "Please enter an error message"

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Get the prompt template
                prompt_content = loop.run_until_complete(
                    mcp_interface.use_prompt_template("debug_error", error=error)
                )

                # Process the prompt through Claude to get the actual debug help
                response = mcp_interface.anthropic.messages.create(
                    max_tokens=2024,
                    model='claude-3-5-sonnet-20241022',
                    messages=[{'role': 'user', 'content': prompt_content}]
                )

                # Extract Claude's response
                claude_response = response.content[0].text

                new_history = history + [
                    {"role": "user", "content": f"Debug error: {error}"},
                    {"role": "assistant", "content": claude_response}
                ]
                return new_history, ""
            except Exception as e:
                error_msg = f"❌ Error generating debug assistance: {str(e)}"
                new_history = history + [
                    {"role": "user", "content": f"Debug error: {error}"},
                    {"role": "assistant", "content": error_msg}
                ]
                return new_history, ""
            finally:
                loop.close()

        # Connect events
        send_btn.click(respond, [msg, chatbot], [chatbot, msg])
        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        upload_btn.click(handle_file_upload, [file_upload, chatbot], [chatbot, uploaded_files_display])
        clear_btn.click(clear_chat, outputs=[chatbot, msg, uploaded_files_display])

        tools_btn.click(show_tools, outputs=info_display)
        prompts_btn.click(show_prompts, outputs=info_display)
        resources_btn.click(show_resources, outputs=info_display)

        # Prompt template events
        analyze_actor_btn.click(use_actor_prompt, inputs=[actor_input, chatbot], outputs=[chatbot, actor_input])
        review_code_btn.click(use_code_review_prompt, inputs=[code_input, chatbot], outputs=[chatbot, code_input])
        debug_error_btn.click(use_debug_prompt, inputs=[error_input, chatbot], outputs=[chatbot, error_input])

    return interface

if __name__ == "__main__":
    # Initialize connection
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        connection_result = loop.run_until_complete(mcp_interface.connect_to_server())
        print(connection_result)
    finally:
        loop.close()
    
    # Launch the interface
    interface = create_interface()
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True,
        debug=True
    )
