# MCP Streamlit Interface

A modern, Claude-like web interface for interacting with your MCP (Model Context Protocol) server using Streamlit.

## Features

- **Clean, Modern UI**: Inspired by Claude's interface with a sidebar for tools and main chat area
- **Tool Management**: Enable/disable individual tools or disable all tools at once
- **Real-time Chat**: Interactive chat interface with message history
- **Connection Status**: Visual indicators for server connection status
- **Responsive Design**: Works well on different screen sizes

## Screenshots Reference

The interface is designed to match the Claude-like interface shown in your screenshots:
- Left sidebar with tools, prompts, and resources
- Main chat area with user and assistant messages
- Toggle switches for enabling/disabling tools
- Clean, professional styling

## Installation

1. Make sure you have all dependencies installed:
```bash
uv sync
```

Or if you prefer pip:
```bash
pip install streamlit>=1.28.0
```

## Usage

### Option 1: Using the launcher script (Recommended)
```bash
python run_ui.py
```

### Option 2: Direct streamlit command
```bash
streamlit run streamlit_ui.py
```

### Option 3: Using uv
```bash
uv run streamlit run streamlit_ui.py
```

## How to Use

1. **Start the Interface**: Run one of the commands above
2. **Open Browser**: Navigate to `http://localhost:8501`
3. **Connect to Server**: Click "Connect to Server" in the sidebar
4. **Select Tools**: Enable/disable tools you want to use from the sidebar
5. **Start Chatting**: Type your messages in the chat input at the bottom

## Interface Components

### Sidebar
- **Connection Status**: Shows if you're connected to the MCP server
- **Tools Section**: List of available tools with toggle switches
- **Prompts Section**: Available prompts from your MCP server
- **Resources Section**: Available resources from your MCP server

### Main Area
- **Chat History**: Displays conversation between you and the assistant
- **Message Input**: Type your queries here
- **Clear Chat**: Button to clear the conversation history

## Tool Management

- **Individual Control**: Toggle each tool on/off independently
- **Disable All**: Quick option to disable all tools at once
- **Tool Descriptions**: Hover over tool names to see descriptions

## Styling

The interface uses custom CSS to provide:
- Claude-like color scheme and typography
- Hover effects for interactive elements
- Clear visual distinction between user and assistant messages
- Professional, clean appearance

## Troubleshooting

### Connection Issues
- Make sure your `server.py` is working correctly
- Check that `uv` is installed and accessible
- Verify your environment variables are set up properly

### Tool Issues
- Ensure tools are properly defined in your MCP server
- Check server logs for any tool-related errors
- Try disabling problematic tools individually

### Performance
- The interface creates a new MCP session for each query to ensure reliability
- If you experience slowness, check your server.py performance
- Consider reducing the number of enabled tools for faster responses

## Customization

You can customize the interface by modifying:
- **CSS Styles**: Edit the `st.markdown()` section with custom CSS
- **Colors**: Change the color scheme in the CSS variables
- **Layout**: Modify the Streamlit layout components
- **Functionality**: Add new features by extending the `MCPStreamlitInterface` class

## Comparison with Other Interfaces

### vs Gradio Interface
- **Pros**: More modern styling, better tool management, cleaner code
- **Cons**: Requires Streamlit dependency

### vs Command Line Interface
- **Pros**: Visual interface, better UX, tool management
- **Cons**: Requires web browser, more resource intensive

## Development

To extend the interface:
1. Modify `streamlit_ui.py` for functionality changes
2. Update CSS in the markdown section for styling changes
3. Add new features by extending the class methods
4. Test thoroughly with your MCP server

## Dependencies

- `streamlit>=1.28.0`
- `anthropic>=0.57.1`
- `mcp[cli]>=1.12.0`
- `nest-asyncio>=1.6.0`
- All other dependencies from your existing `pyproject.toml`
