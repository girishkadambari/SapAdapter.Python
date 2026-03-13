import pythoncom
import win32com.client
from typing import Any, Callable, TypeVar, Optional
from loguru import logger
import threading

T = TypeVar("T")

class ComExecutor:
    """
    Handles safe execution of COM calls by ensuring CoInitialize is called on the executing thread.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._is_initialized = False

    def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Executes a function that interacts with COM.
        """
        try:
            # Initialize COM for the current thread if not already done
            # pythoncom.CoInitialize is safe to call multiple times on the same thread
            pythoncom.CoInitialize()
            
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"COM Execution Error in {func.__name__}: {str(e)}")
            raise
        finally:
            # We don't uninitialize here because we might be on a thread pooled by asyncio
            # and could need it again. Generally CoUninitialize should be called when thread exits.
            pass

    @staticmethod
    def get_object(prog_id: str) -> Any:
        """
        Safe GetObject wrapper.
        """
        pythoncom.CoInitialize()
        return win32com.client.GetObject(prog_id)

    @staticmethod
    def dispatch(prog_id: str) -> Any:
        """
        Safe Dispatch wrapper.
        """
        pythoncom.CoInitialize()
        return win32com.client.Dispatch(prog_id)
