from langfuse import Langfuse
from config import settings
from typing import Optional, Dict, Any
import json
import os

class LangfuseClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangfuseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        if settings.LANGFUSE_ENABLED:
            self.client = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST
            )
        else:
            self.client = None


    def track_llm_request(
        self,
        prompt: str,
        system_message: str,
        response: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track an LLM request in Langfuse.
        
        Args:
            prompt: The user prompt
            system_message: The system message
            response: The LLM response
            metadata: Additional metadata to track
        """
        print("[Langfuse] track_llm_request called")

        if not self.client:
            return

        try:
            # Create a new trace
            trace = self.client.trace(
                name="transport_request_parse",
                user_id=settings.LANGFUSE_USER_ID,
                tags=[os.getenv("ENVIRONMENT", "dev")],
                metadata=metadata or {}
            )

            # Create a generation
            generation = trace.generation(
                name="parse_transport_request",
                model=settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else "gpt-3.5-turbo",
                completion=json.dumps(response, ensure_ascii=False),
                input=prompt,
                output=response,
                metadata={
                    "system_message": system_message,
                    "provider": settings.LLM_PROVIDER
                }
            )

            # Update the generation and trace
            generation.update()
            trace.update()

            self.client.flush()


        except Exception as e:
            print(f"Error tracking LLM request in Langfuse: {str(e)}")

    def flush(self):
        """Flush any pending events to Langfuse."""
        if self.client:
            self.client.flush() 