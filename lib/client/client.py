import sys
import asyncio
from contextlib import AsyncExitStack
from typing import Optional
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configs.configuration import Configurations

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.configs = Configurations()
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic(api_key=self.configs.ANTHROPIC_API_KEY)
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, script_path: str):
        server_params = StdioServerParameters(
            command="python",
            args=[script_path]
        )
        stdio = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(*stdio))
        await self.session.initialize()

        tools = (await self.session.list_tools()).tools
        print("✅ Connected with tools:", [t.name for t in tools])

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]
        tools = (await self.session.list_tools()).tools

        tool_list = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in tools]

        resp = self.anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=messages,
            tools=tool_list
        )

        full_response = []

        for content in resp.content:
            if content.type == "text":
                full_response.append(content.text)
            elif content.type == "tool_use":
                tool_resp = await self.session.call_tool(content.name, content.input)
                full_response.append(f"[Tool: {content.name}]\n{tool_resp.content[0].text}")

        return "\n".join(full_response)

    async def chat_loop(self):
        print("🔍 Ask your questions (type 'quit' to exit):")
        while True:
            try:
                q = input("\n> ").strip()
                if q.lower() == "quit":
                    break
                result = await self.process_query(q)
                print("\n💬", result)
            except Exception as e:
                print(f"❌ Error: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py path/to/server.py")
        return

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__": 
    asyncio.run(main())
