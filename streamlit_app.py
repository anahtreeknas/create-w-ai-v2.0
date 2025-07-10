import streamlit as st
import json
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from claude_client import ClaudeClient
from utils import create_app, update_app
import re

load_dotenv()

st.set_page_config(
    page_title="Create with AI v2.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like styling
st.markdown("""
<style>
    /* Import Inter font for better typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global dark theme styling */
    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        background-color: #1a1a1a;
        padding: 0 0 8rem 0; /* Add bottom padding so content isn't hidden behind the fixed chat input */
        max-width: 100%;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: #e0e0e0;
        padding: 1.5rem 0;
        background-color: #1a1a1a;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0;
        border-bottom: 1px solid #333333;
        font-family: 'Inter', sans-serif;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        margin: 0;
        border-bottom: 1px solid #333333;
        font-size: 0.95rem;
        line-height: 1.6;
        font-family: 'Inter', sans-serif;
    }
    
    .chat-message:hover {
        background-color: rgba(255, 255, 255, 0.025);
    }
    
    .user-message {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border-left: none;
        margin: 0;
        position: relative;
    }
    
    .user-message::before {
        content: "You";
        position: absolute;
        top: 1rem;
        left: 1.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        color: #e0e0e0;
        margin-bottom: 0.5rem;
    }
    
    .user-message .message-content {
        padding-top: 2rem;
    }
    
    .assistant-message {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border-left: none;
        margin: 0;
        position: relative;
    }
    
    .assistant-message::before {
        content: "Claude";
        position: absolute;
        top: 1rem;
        left: 1.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        color: #e0e0e0;
        margin-bottom: 0.5rem;
    }
    
    .assistant-message .message-content {
        padding-top: 2rem;
    }
    
    .system-message {
        background-color: #404040;
        color: #cccccc;
        border: 1px solid #333333;
        border-radius: 6px;
        font-style: italic;
        text-align: center;
        margin: 1rem;
        padding: 1rem;
        font-size: 0.875rem;
    }
    
    /* Phase indicator */
    .phase-indicator {
        background-color: #4a4a4a;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        text-align: center;
        margin: 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid #5a5a5a;
    }
    
    /* JSON container */
    .json-container {
        background-color: #242424;
        color: #e0e0e0;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #333333;
        margin: 1rem 0;
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
        font-size: 0.875rem;
        line-height: 1.5;
        overflow-x: auto;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background-color: #1a1a1a !important;
        border-right: 1px solid #333333;
    }
    
    .css-1d391kg .stMarkdown, .css-1cypcdb .stMarkdown {
        color: #e0e0e0;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4a4a4a;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
    }
    
    .stButton > button:hover {
        background-color: #5a5a5a;
        transform: none;
        box-shadow: none;
    }
    
    .stButton > button:active {
        background-color: #3a3a3a;
    }
    
    /* Form styling */
    .stTextArea textarea {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #4a4a4a;
        border-radius: 6px;
        padding: 1rem;
        font-size: 0.9rem;
        font-family: 'Inter', sans-serif;
        transition: border-color 0.2s ease;
        resize: vertical;
    }
    
    .stTextArea textarea:focus {
        border-color: #5a5a5a;
        box-shadow: 0 0 0 2px rgba(90, 90, 90, 0.2);
        outline: none;
    }
    
    .stTextArea textarea::placeholder {
        color: #888888;
    }
    
    /* Input styling */
    .stTextInput input {
        background-color: #333333;
        color: #e0e0e0;
        border: 1px solid #4a4a4a;
        border-radius: 6px;
        padding: 0.75rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput input:focus {
        border-color: #5a5a5a;
        box-shadow: 0 0 0 2px rgba(90, 90, 90, 0.2);
        outline: none;
    }
    
    /* Info panels */
    .stAlert {
        border-radius: 6px;
        border: 1px solid #333333;
        background-color: #3a3a3a;
        color: #e0e0e0;
    }
    
    .stAlert > div {
        padding: 1rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #333333;
        color: #e0e0e0;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 600;
        border: 1px solid #4a4a4a;
    }
    
    .streamlit-expanderContent {
        background-color: #242424;
        border: 1px solid #333333;
        border-radius: 0 0 6px 6px;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #4a4a4a;
        border: 1px solid #5a5a5a;
        color: white;
    }
    
    .stError {
        background-color: #3a3a3a;
        border: 1px solid #4a4a4a;
        color: white;
    }
    
    .stWarning {
        background-color: #454545;
        border: 1px solid #555555;
        color: white;
    }
    
    /* Custom scrollbar */
    .stChatMessage::-webkit-scrollbar {
        width: 8px;
    }
    
    .stChatMessage::-webkit-scrollbar-track {
        background: #242424;
        border-radius: 4px;
    }
    
    .stChatMessage::-webkit-scrollbar-thumb {
        background: #4a4a4a;
        border-radius: 4px;
    }
    
    .stChatMessage::-webkit-scrollbar-thumb:hover {
        background: #5a5a5a;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Message input area */
    .stChatInputContainer {
        background-color: #1a1a1a;
        border-top: 1px solid #333333;
        padding: 1rem; /* Minimise horizontal padding so the input can use full width */
        position: fixed;   /* Pin to the bottom of the viewport */
        bottom: 0;
        left: 0;
        width: 100%;
        max-width: 100%;
        z-index: 1000;
    }

    /* Ensure any internal wrappers of st.chat_input also stretch */
    .stChatInputContainer > div,
    .stChatInputContainer [data-testid="stChatInput"] {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Finally, make the native textarea / input span full width */
    .stChatInputContainer textarea,
    .stChatInputContainer input {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #242424;
        border: 1px solid #333333;
        border-radius: 6px;
    }
    
    .stCodeBlock code {
        color: #e0e0e0;
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.25rem;
            padding: 1rem 0;
        }
        
        .chat-message {
            padding: 1rem;
        }
        
        .user-message::before,
        .assistant-message::before {
            font-size: 0.8rem;
        }
    }
    
    /* Loading animation for ChatGPT-like experience */
    .loading-dots {
        display: inline-block;
        position: relative;
        margin: 0.5rem 0;
    }
    
    .loading-dots::after {
        content: '';
        display: inline-block;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: #5a5a5a;
        animation: loading 1.4s infinite linear;
    }
    
    @keyframes loading {
        0%, 20% {
            background: #5a5a5a;
        }
        50% {
            background: #4a4a4a;
        }
        80%, 100% {
            background: #5a5a5a;
        }
    }
</style>
""", unsafe_allow_html=True)

class StreamlitChatbot:
    """Streamlit-based chatbot interface."""
    
    def __init__(self):
        """Initialize the Streamlit chatbot."""
        self.initialize_session_state()
        self.setup_client()
        self.load_prompts()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'client' not in st.session_state:
            st.session_state.client = None
        if 'first_turn' not in st.session_state:
            st.session_state.first_turn = True
        if 'spec_parsed' not in st.session_state:
            st.session_state.spec_parsed = None
        if 'phase' not in st.session_state:
            st.session_state.phase = "discovery"
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'spec_system_prompt' not in st.session_state:
            st.session_state.spec_system_prompt = None
        if 'initial_usecase' not in st.session_state:
            st.session_state.initial_usecase = self.load_initial_usecase()
    
    def setup_client(self):
        """Setup the Claude client."""
        try:
            if st.session_state.client is None:
                st.session_state.client = ClaudeClient()
        except ValueError as e:
            st.error(f"Error initializing Claude client: {e}")
            st.stop()
    
    def load_initial_usecase(self) -> str:
        """Load the initial use case from file."""
        try:
            with open("initial_usecase.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""
    
    def load_prompts(self):
        """Load prompt templates."""
        try:
            with open("v2v.j2", "r", encoding="utf-8") as f:
                st.session_state.spec_system_prompt_tpl = f.read()
            
            with open("question_generation_prompt.j2", "r", encoding="utf-8") as f:
                st.session_state.question_generation_prompt = f.read()
        except FileNotFoundError as e:
            st.error(f"Error loading prompt templates: {e}")
            st.stop()
    
    def extract_json(self, text: str) -> Optional[dict]:
        """Extract JSON from Claude's response."""
        # Direct parse attempt
        try:
            return json.loads(text)
        except Exception:
            pass

        # Look for fenced code blocks
        code_blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
        for block in code_blocks:
            try:
                return json.loads(block)
            except Exception:
                continue

        # Fallback: substring between first { and last }
        if "{" in text and "}" in text:
            candidate = text[text.find("{") : text.rfind("}") + 1]
            try:
                return json.loads(candidate)
            except Exception:
                pass
        return None
    
    def add_to_chat_history(self, role: str, content: str, message_type: str = "text"):
        """Add message to chat history."""
        st.session_state.chat_history.append({
            "role": role,
            "content": content,
            "message_type": message_type,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
    def display_chat_history(self):
        """Display the chat history."""
        if not st.session_state.chat_history:
            # No messages yet; render nothing so the interface stays clean
            return
        
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            timestamp = message["timestamp"]
            message_type = message.get("message_type", "text")
            
            if role == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-content">
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif role == "assistant":
                if message_type == "json":
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-content">
                            <div class="json-container">
                                <pre>{content}</pre>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-content">
                            {content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            elif role == "system":
                st.markdown(f"""
                <div class="chat-message system-message">
                    {content}
                </div>
                """, unsafe_allow_html=True)
    
    def run(self):
        """Main Streamlit app interface."""
        # Header
        st.markdown('<h1 class="main-header">Create with AI v2.0</h1>', unsafe_allow_html=True)
        
        # Sidebar
        self.render_sidebar()

        # Main chat area
        chat_section = st.container()
        with chat_section:
            st.subheader("💬 Chat")
            
            # Chat history container
            chat_container = st.container()
            with chat_container:
                self.display_chat_history()
            
            # Chat input pinned to bottom of the page
            user_input = st.chat_input("Your message:")
            if user_input is not None and user_input.strip():
                self.process_message(user_input.strip())
                st.rerun()
    
    def render_sidebar(self):
        """Render the sidebar with controls."""
        with st.sidebar:
            # Clear conversation
            if st.button("🗑️ Clear History"):
                st.session_state.client.clear_history()
                st.session_state.chat_history = []
                st.session_state.first_turn = True
                st.session_state.phase = "discovery"
                st.session_state.spec_parsed = None
                st.session_state.spec_system_prompt = None
                st.success("Conversation cleared!")
                st.rerun()
                return  # Exit early; no other controls
            
            # Export functionality
            if st.session_state.phase == "specification" and st.session_state.spec_parsed:
                st.divider()
                st.subheader("📤 Export")
                
                if st.button("Export Specification"):
                    self.export_specification()
                
                # App creation
                st.divider()
                st.subheader("🚀 App Management")
                
                app_name = st.text_input("App Name", key="app_name_input")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Create App") and app_name:
                        self.create_app(app_name)
                
                with col2:
                    app_id = st.text_input("App ID", key="app_id_input")
                    if st.button("Update App") and app_name and app_id:
                        self.update_app(app_name, app_id)
    
    def render_info_panel(self):
        """Render the information panel."""
        if st.session_state.phase == "discovery":
            st.info("🔍 **Discovery Phase**\n\nI'm gathering information about your use case to create a detailed specification.")
        else:
            st.info("📋 **Specification Phase**\n\nI'm helping you refine and finalize your chatbot specification.")
        
        # Show current specification if available
        if st.session_state.spec_parsed:
            st.divider()
            st.subheader("📄 Current Specification")
            with st.expander("View Specification", expanded=False):
                st.json(st.session_state.spec_parsed)
    
    def render_chat_input(self):
        """Render the chat input area."""
        # Auto-submit initial use case on first turn
        if st.session_state.first_turn and st.session_state.phase == "discovery" and st.session_state.initial_usecase:
            self.process_message(st.session_state.initial_usecase)
            st.session_state.first_turn = False
            st.rerun()
        
        # Chat input pinned to bottom of the page
        user_input = st.chat_input("Your message:")
        if user_input is not None and user_input.strip():
            self.process_message(user_input.strip())
            st.rerun()
    
    def process_message(self, user_input: str):
        """Process user message and get response."""
        # Add user message to chat history
        self.add_to_chat_history("user", user_input)
        
        try:
            # Show loading spinner
            with st.spinner("Thinking..."):
                if st.session_state.phase == "discovery":
                    self.handle_discovery_phase(user_input)
                else:
                    self.handle_specification_phase(user_input)
        
        except Exception as e:
            st.error(f"Error processing message: {e}")
            self.add_to_chat_history("system", f"Error: {e}")
    
    def handle_discovery_phase(self, user_input: str):
        """Handle discovery phase conversation."""
        response = st.session_state.client.send_message(
            user_input, 
            st.session_state.question_generation_prompt
        )
        
        # Try to extract JSON from response
        parsed = self.extract_json(response)
        
        if isinstance(parsed, dict) and parsed.get("handoff") is True:
            # Switch to specification phase
            self.add_to_chat_history("assistant", response)
            self.add_to_chat_history("system", "Switching to specification mode...")
            
            # Prepare for specification phase
            enhanced_uc = parsed.copy()
            enhanced_uc.pop("handoff", None)
            enhanced_uc_str = json.dumps(enhanced_uc, indent=4)
            
            # Build system prompt
            st.session_state.spec_system_prompt = st.session_state.spec_system_prompt_tpl.replace(
                "{{ usecase_details }}", enhanced_uc_str
            )
            
            # Clear client history for clean context
            st.session_state.client.clear_history()
            
            # Get initial specification
            spec_response = st.session_state.client.send_message(
                enhanced_uc_str, 
                st.session_state.spec_system_prompt
            )
            
            # Parse and store initial specification
            spec_parsed = self.extract_json(spec_response)
            if spec_parsed:
                st.session_state.spec_parsed = spec_parsed
                self.add_to_chat_history("assistant", json.dumps(spec_parsed, indent=2), "json")
            else:
                self.add_to_chat_history("assistant", spec_response)
            
            # Switch phase
            st.session_state.phase = "specification"
        else:
            # Continue in discovery phase
            self.add_to_chat_history("assistant", response)
    
    def handle_specification_phase(self, user_input: str):
        """Handle specification phase conversation."""
        if not st.session_state.spec_system_prompt:
            st.error("System prompt not initialized for specification phase.")
            return
        
        response = st.session_state.client.send_message(
            user_input, 
            st.session_state.spec_system_prompt
        )
        
        # Try to parse as JSON
        parsed = self.extract_json(response)
        if parsed:
            st.session_state.spec_parsed = parsed
            self.add_to_chat_history("assistant", json.dumps(parsed, indent=2), "json")
        else:
            self.add_to_chat_history("assistant", response)
    
    def export_specification(self):
        """Export the current specification to a file."""
        if st.session_state.spec_parsed:
            try:
                with open("bot_spec.json", "w", encoding="utf-8") as f:
                    json.dump(st.session_state.spec_parsed, f, indent=4)
                st.success("✅ Specification exported successfully to bot_spec.json")
                self.add_to_chat_history("system", "Specification exported to bot_spec.json")
            except Exception as e:
                st.error(f"Error exporting specification: {e}")
        else:
            st.warning("No specification available to export.")
    
    def create_app(self, app_name: str):
        """Create a new app."""
        if not st.session_state.spec_parsed:
            st.warning("No specification available. Please complete the specification first.")
            return
        
        try:
            with st.spinner(f"Creating app: {app_name}"):
                result = create_app(app_name, st.session_state.spec_parsed)
                st.success(f"✅ App '{app_name}' created successfully!")
                self.add_to_chat_history("system", f"App '{app_name}' created successfully")
                st.json(result)
        except Exception as e:
            st.error(f"Error creating app: {e}")
            self.add_to_chat_history("system", f"Error creating app: {e}")
    
    def update_app(self, app_name: str, app_id: str):
        """Update an existing app."""
        if not st.session_state.spec_parsed:
            st.warning("No specification available. Please complete the specification first.")
            return
        
        try:
            with st.spinner(f"Updating app: {app_name}"):
                result = update_app(app_name, app_id, st.session_state.spec_parsed)
                st.success(f"✅ App '{app_name}' updated successfully!")
                self.add_to_chat_history("system", f"App '{app_name}' updated successfully")
                st.json(result)
        except Exception as e:
            st.error(f"Error updating app: {e}")
            self.add_to_chat_history("system", f"Error updating app: {e}")

def main():
    """Main entry point for the Streamlit app."""
    chatbot = StreamlitChatbot()
    chatbot.run()

if __name__ == "__main__":
    main() 