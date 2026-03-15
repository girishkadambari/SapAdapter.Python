import sys
import json
import asyncio
from loguru import logger
from sap_mcp.runtime.sap_runtime import SapRuntime
from sap_mcp.mcp.mcp_adapter import McpAdapter
from sap_mcp.mcp.mcp_server import McpServer

# Suppress loguru output to stdout to avoid interfering with MCP JSON-RPC
logger.remove()
logger.add(sys.stderr, level="INFO")

async def stdio_server():
    """
    Standard input/output loop for MCP.
    """
    runtime = SapRuntime()
    mcp_adapter = McpAdapter(runtime)
    mcp_server = McpServer(mcp_adapter)
    
    logger.info("SAP MCP Stdio Server Started")
    
    while True:
        try:
            # Read line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            # Handle the MCP message
            response = await mcp_server.handle_message(line)
            
            if response:
                # Write response to stdout with a newline
                sys.stdout.write(response + "\n")
                sys.stdout.flush()
                
        except Exception as e:
            logger.error(f"Error in stdio loop: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(stdio_server())
    except KeyboardInterrupt:
        logger.info("SAP MCP Stdio Server Stopped")
