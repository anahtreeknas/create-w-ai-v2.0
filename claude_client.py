import os
from typing import List, Dict, Any, Optional
import litellm
from dotenv import load_dotenv

load_dotenv()


class ClaudeClient:
    """Client for interacting with Claude 3.7 LLM through Vertex AI."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Claude client.
        
        Args:
            api_key: Google Cloud API key. If not provided, will try to get from environment.
            model: Claude model to use. Defaults to claude-3-7-sonnet-20250219.
        """
        
        self.api_key = api_key or os.getenv("VERTEX_CREDENTIALS")
        if not self.api_key:
            raise ValueError(
                "Credentials not found. Set GOOGLE_API_KEY, VERTEX_CREDENTIALS, or "
                "GOOGLE_APPLICATION_CREDENTIALS, or pass --api-key."
            )
     
        
        
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
        self.location = os.getenv("GOOGLE_LOCATION", "us-east5")
        
        # Configure LiteLLM for Vertex AI
        litellm.set_verbose = False
        self.conversation_history: List[Dict[str, str]] = []
        
        # Debug info
        print(f"Using model: {self.model}")
        # print(f"Using location: {self.location}")
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        self.conversation_history.append({"role": role, "content": content})
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()
    
    def send_message(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a message to Claude and get a response.
        
        Args:
            message: User message to send
            system_prompt: Optional system prompt to guide Claude's behavior
            
        Returns:
            Claude's response as a string
        """
        try:
            # Add user message to history
            self.add_message("user", message)
            
            # Prepare messages for API call
            messages = self.get_messages()
            
            # Prepare the API call parameters
            api_params = {
                "model": f"vertex_ai/{self.model}",
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.7,
                "vertex_location": self.location,
            }
            
            if system_prompt:
                # Add system message at the beginning
                messages_with_system = [{"role": "system", "content": system_prompt}] + messages
                api_params["messages"] = messages_with_system
            
            # Make API call through LiteLLM
            response = litellm.completion(**api_params)
            
            # Extract response content
            if response and response.choices and len(response.choices) > 0:
                assistant_message = response.choices[0].message.content
                self.add_message("assistant", assistant_message)
                return assistant_message
            else:
                return "Sorry, I couldn't generate a response."
                
        except Exception as e:
            error_msg = f"Error communicating with Claude: {str(e)}"
            print(f"Error: {error_msg}")
            return error_msg
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "model": self.model,
            "api_key_set": bool(self.api_key),
            "location": self.location,
            "history_length": len(self.conversation_history)
        } 