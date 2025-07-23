# 🤖 BroadAxis-AI

**Advanced AI-Powered HR Services Platform with Multi-Model Support and RAG Integration**

BroadAxis-AI is a sophisticated AI assistant platform designed specifically for HR services, featuring multiple Claude model support, company knowledge integration, and comprehensive document processing capabilities.

## ✨ Features

### 🎯 **Multi-Model AI Support**
- **Claude 3.5 Sonnet** (Default) - Balanced performance and speed
- **Claude Opus 4** (Latest) - Most advanced reasoning capabilities
- **Claude 3 Opus** - Premium model for complex tasks
- **Claude 3 Haiku** - Ultra-fast responses
- **Claude 3 Sonnet** - Reliable general-purpose model

### 🏢 **Company Knowledge Integration**
- **RAG (Retrieval-Augmented Generation)** for company-specific information
- **Pinecone Vector Database** for intelligent document search
- **Automatic Query Detection** for company-related questions
- **Document Management** with real-time knowledge base updates

### 📄 **Document Processing**
- **Multi-format Support**: PDF, DOCX, DOC, TXT, MD, JSON, XML, CSV
- **Intelligent Text Extraction** with content analysis
- **Context-Aware Processing** for better AI responses
- **File Upload Interface** with drag-and-drop functionality

### 🛠️ **MCP Tools & Resources**
- **Weather Services** - Real-time weather data and alerts
- **Research Tools** - arXiv paper search and analysis
- **Web Search** - Tavily-powered intelligent web search
- **Company Knowledge** - RAG-powered company information retrieval
- **File Management** - Document reading and processing tools

### 🎨 **Modern UI/UX**
- **Clean Streamlit Interface** with professional design
- **Chat History Management** with session persistence
- **Real-time Model Switching** without losing context
- **Responsive Layout** optimized for all screen sizes
- **Interactive Toolbars** with prompt templates and resources

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Anthropic API Key
- Pinecone API Key (for RAG features)
- Tavily API Key (for web search)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rfp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

4. **Start the MCP Server**
   ```bash
   python server.py
   ```

5. **Launch the Streamlit UI**
   ```bash
   streamlit run streamlit_ui_fixed.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## 📁 Project Structure

```
rfp-server/
├── 📄 README.md                 # This file
├── 🔧 server.py                 # MCP server with tools and resources
├── 🖥️ streamlit_ui_fixed.py     # Main Streamlit application
├── 📋 requirements.txt          # Python dependencies
├── ⚙️ .env                      # Environment variables (create this)
├── 📊 client.py                 # MCP client utilities
├── 🚀 run_ui.py                 # UI launcher script
├── 📚 papers/                   # Research papers storage
├── 🔒 __pycache__/              # Python cache files
└── 📖 STREAMLIT_UI_README.md    # UI-specific documentation
```

## 🛠️ Available MCP Tools

### Weather Services
- `get_alerts(state)` - Get weather alerts for US states
- `get_forecast(lat, lon)` - Get detailed weather forecasts

### Research & Knowledge
- `search_papers(topic, max_results)` - Search arXiv for research papers
- `extract_info(paper_id)` - Get detailed paper information
- `query_company_knowledge(query)` - Search company knowledge base
- `web_search(query)` - Intelligent web search with Tavily

### Utility Tools
- `sum(a, b)` - Basic arithmetic operations
- `add_company_document(content, title)` - Add documents to knowledge base
- `get_company_knowledge_stats()` - View knowledge base statistics

## 📚 MCP Resources

### Configuration
- `config://settings` - Application settings
- `config://word_formatting_instructions` - Document formatting guidelines

### Company Information
- `company://info` - BroadAxis company overview
- `company://knowledge-base` - Knowledge base statistics

### File System
- `file://desktop/{name}` - Read documents from desktop
- `greeting://{name}` - Personalized greetings

## 🎯 Usage Examples

### Basic Chat
1. Select your preferred AI model from the dropdown
2. Type your question in the chat input
3. Get intelligent responses with context awareness

### Document Analysis
1. Click the 📎 button to upload files
2. Select documents (PDF, DOCX, TXT, etc.)
3. Ask questions about the uploaded content
4. Get detailed analysis and insights

### Company Knowledge Queries
1. Ask questions about BroadAxis services
2. Get automatic responses from the knowledge base
3. Add new company documents to expand knowledge

### Research & Web Search
1. Use the ➕ button to access prompts
2. Select research-related prompts
3. Get comprehensive analysis with web search integration

## ⚙️ Configuration

### Model Selection
The application supports multiple Claude models. Change models using the dropdown in the main interface:

- **Default**: Claude 3.5 Sonnet (balanced performance)
- **Premium**: Claude Opus 4 (latest and most capable)
- **Fast**: Claude 3 Haiku (quick responses)

### Environment Variables
Required environment variables in `.env`:

```env
# Core API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pcsk_...
TAVILY_API_KEY=tvly-...

# Optional Configuration
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=broadaxis-knowledge
```

## 🔧 Development

### Running in Development Mode

1. **Start the MCP Server with debugging**
   ```bash
   python server.py --debug
   ```

2. **Run Streamlit with auto-reload**
   ```bash
   streamlit run streamlit_ui_fixed.py --server.runOnSave true
   ```

### Adding New Tools

To add new MCP tools to the server:

1. **Define the tool function**
   ```python
   @mcp.tool()
   def your_new_tool(parameter: str) -> str:
       """Description of your tool"""
       # Your implementation here
       return result
   ```

2. **Add to server.py** and restart the server

3. **The tool will automatically appear** in the Streamlit UI

### Adding New Resources

To add new MCP resources:

1. **Define the resource**
   ```python
   @mcp.resource("your-resource://{param}")
   def get_your_resource(param: str) -> str:
       """Resource description"""
       return resource_content
   ```

2. **Access via the UI** using the 📄 Resources button

## 🧪 Testing

### Manual Testing
1. **Test MCP Server**
   ```bash
   python server.py
   # Check for successful startup and tool loading
   ```

2. **Test Streamlit UI**
   ```bash
   streamlit run streamlit_ui_fixed.py
   # Verify all features work correctly
   ```

### Feature Testing Checklist
- [ ] Model selection works correctly
- [ ] File upload and processing
- [ ] Chat history persistence
- [ ] MCP tools integration
- [ ] Company knowledge queries
- [ ] Web search functionality
- [ ] Document analysis capabilities

## 🚨 Troubleshooting

### Common Issues

#### 1. **Connection Failed**
```
Error: Failed to connect to MCP server
```
**Solution**: Ensure the MCP server is running before starting the Streamlit UI

#### 2. **Missing API Keys**
```
Error: API key not found
```
**Solution**: Check your `.env` file and ensure all required API keys are set

#### 3. **Import Errors**
```
ModuleNotFoundError: No module named 'package_name'
```
**Solution**: Install missing dependencies
```bash
pip install -r requirements.txt
```

#### 4. **Pinecone Connection Issues**
```
Error: Failed to connect to Pinecone
```
**Solution**:
- Verify your Pinecone API key
- Check if the index exists
- Ensure correct region configuration

#### 5. **Model Not Available**
```
Error: Model not found
```
**Solution**:
- Check if you have access to the selected Claude model
- Verify your Anthropic API key has the required permissions
- Try switching to a different model

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=true
python server.py
```

## 📊 Performance

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **CPU**: Multi-core processor recommended
- **Storage**: 1GB+ free space for documents and cache
- **Network**: Stable internet connection for API calls

### Performance Tips
1. **Use Claude 3 Haiku** for faster responses
2. **Limit document size** to under 10MB for better processing
3. **Clear chat history** periodically to improve performance
4. **Use specific queries** for better RAG results

## 🔐 Security

### API Key Management
- Store API keys in `.env` file (never commit to version control)
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage and costs

### Data Privacy
- Documents are processed locally when possible
- API calls are made over HTTPS
- No persistent storage of sensitive data
- Chat history stored locally in session state

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to functions
- Keep functions focused and small

### Adding Features
1. **New MCP Tools**: Add to `server.py`
2. **UI Improvements**: Modify `streamlit_ui_fixed.py`
3. **Documentation**: Update README.md and inline docs

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude AI models
- **Streamlit** for the web framework
- **MCP (Model Context Protocol)** for tool integration
- **Pinecone** for vector database services
- **Tavily** for web search capabilities

## 📞 Support

For support and questions:
- 📧 Email: support@broadaxis-hr.com
- 🌐 Website: www.broadaxis-hr.com
- 📖 Documentation: See STREAMLIT_UI_README.md for UI details

---

**Built with ❤️ by the BroadAxis Team**

*Empowering HR services through advanced AI technology*