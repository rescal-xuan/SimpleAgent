from typing import List, Optional, Dict, Any, Callable, Union
from abc import ABC, abstractmethod
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCallback(ABC):
    """Abstract base class defining the callback interface"""
    
    @abstractmethod
    def on_llm_start(self, prompt: str, **kwargs) -> None:
        """Called when LLM starts processing"""
        pass

    @abstractmethod
    def on_llm_end(self, response: str, **kwargs) -> None:
        """Called when LLM finishes processing"""
        pass

    @abstractmethod
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM processing fails"""
        pass

    @abstractmethod
    def on_rag_start(self, file_path: str, query: str, **kwargs) -> None:
        """Called when RAG processing starts"""
        pass

    @abstractmethod
    def on_rag_end(self, result: str, **kwargs) -> None:
        """Called when RAG processing completes"""
        pass

    @abstractmethod
    def on_rag_error(self, error: Exception, **kwargs) -> None:
        """Called when RAG processing fails"""
        pass

    @abstractmethod
    def on_tool_start(self, tool_name: str, params: Dict[str, Any], **kwargs) -> None:
        """Called when tool execution starts"""
        pass

    @abstractmethod
    def on_tool_end(self, tool_name: str, result: Any, **kwargs) -> None:
        """Called when tool execution completes"""
        pass

    @abstractmethod
    def on_tool_error(self, tool_name: str, error: Exception, **kwargs) -> None:
        """Called when tool execution fails"""
        pass


class CallbackHandler:
    """Manages multiple callbacks and dispatches events to them"""
    
    def __init__(self, callbacks: Optional[List[BaseCallback]] = None, name: str = "CallbackHandler"):
        """
        Initialize the callback handler
        
        Args:
            callbacks: List of callbacks to register initially
            name: Name for this handler
        """
        self.name = name
        self.callbacks: List[BaseCallback] = callbacks or []
        
    def add_callback(self, callback: BaseCallback) -> None:
        """Register a new callback"""
        if not isinstance(callback, BaseCallback):
            raise TypeError(f"Callback must inherit from BaseCallback, got {type(callback)}")
        self.callbacks.append(callback)
        logger.info(f"Added callback: {callback.__class__.__name__}")
        
    def remove_callback(self, callback: BaseCallback) -> bool:
        """Remove a callback"""
        try:
            self.callbacks.remove(callback)
            logger.info(f"Removed callback: {callback.__class__.__name__}")
            return True
        except ValueError:
            logger.warning(f"Callback not found: {callback.__class__.__name__}")
            return False
    
    def _safe_execute(self, method_name: str, *args, **kwargs) -> None:
        """Safely execute a callback method across all registered callbacks"""
        for callback in self.callbacks:
            try:
                method = getattr(callback, method_name)
                method(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing {method_name} on {callback.__class__.__name__}: {str(e)}")

    # Event dispatch methods
    def on_llm_start(self, prompt: str, **kwargs) -> None:
        self._safe_execute('on_llm_start', prompt, **kwargs)

    def on_llm_end(self, response: str, **kwargs) -> None:
        self._safe_execute('on_llm_end', response, **kwargs)

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        self._safe_execute('on_llm_error', error, **kwargs)

    def on_rag_start(self, file_path: str, query: str, **kwargs) -> None:
        self._safe_execute('on_rag_start', file_path, query, **kwargs)

    def on_rag_end(self, result: str, **kwargs) -> None:
        self._safe_execute('on_rag_end', result, **kwargs)

    def on_rag_error(self, error: Exception, **kwargs) -> None:
        self._safe_execute('on_rag_error', error, **kwargs)

    def on_tool_start(self, tool_name: str, params: Dict[str, Any], **kwargs) -> None:
        self._safe_execute('on_tool_start', tool_name, params, **kwargs)

    def on_tool_end(self, tool_name: str, result: Any, **kwargs) -> None:
        self._safe_execute('on_tool_end', tool_name, result, **kwargs)

    def on_tool_error(self, tool_name: str, error: Exception, **kwargs) -> None:
        self._safe_execute('on_tool_error', tool_name, error, **kwargs)


class LoggingCallback(BaseCallback):
    """Simple callback that logs all events"""
    
    def on_llm_start(self, prompt: str, **kwargs) -> None:
        logger.info(f"LLM started processing prompt: {prompt[:50]}...")

    def on_llm_end(self, response: str, **kwargs) -> None:
        logger.info(f"LLM generated response: {response[:50]}...")

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        logger.error(f"LLM error: {str(error)}")

    def on_rag_start(self, file_path: str, query: str, **kwargs) -> None:
        logger.info(f"RAG started - File: {file_path}, Query: {query}")

    def on_rag_end(self, result: str, **kwargs) -> None:
        logger.info(f"RAG completed - Result: {result[:100]}...")

    def on_rag_error(self, error: Exception, **kwargs) -> None:
        logger.error(f"RAG error: {str(error)}")

    def on_tool_start(self, tool_name: str, params: Dict[str, Any], **kwargs) -> None:
        logger.info(f"Tool {tool_name} started with params: {params}")

    def on_tool_end(self, tool_name: str, result: Any, **kwargs) -> None:
        logger.info(f"Tool {tool_name} completed - Result: {result}")

    def on_tool_error(self, tool_name: str, error: Exception, **kwargs) -> None:
        logger.error(f"Tool {tool_name} error: {str(error)}")
        
        
if __name__ == "__main__":
# Create handler with logging callback
    handler = CallbackHandler([LoggingCallback()])

    # Simulate LLM workflow
    handler.on_llm_start("What is the meaning of life?")
    handler.on_llm_end("42")

    # Simulate tool workflow
    handler.on_tool_start("calculator", {"operation": "add", "values": [2, 2]})
    handler.on_tool_end("calculator", 4)

    # Simulate error
    try:
        raise ValueError("Example error")
    except Exception as e:
        handler.on_tool_error("weather", e)