#!/usr/bin/env python3

import asyncio
import sys
from typing import Any, Dict, List
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

server = Server("hola-mundo-server")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="hola_mundo",
            description="Devuelve un simple 'hola mundo'",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    if name == "hola_mundo":
        return [
            types.TextContent(
                type="text",
                text="hola mundo"
            )
        ]
    else:
        raise ValueError(f"Herramienta desconocida: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hola-mundo-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())