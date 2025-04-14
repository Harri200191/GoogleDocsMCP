import asyncio
import sys
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic

class MCPClient:
    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect(self, server_script: str):
        command = "python"
        server_params = StdioServerParameters(command=command, args=[server_script])
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        tools = (await self.session.list_tools()).tools
        print("Connected to server with tools:", [t.name for t in tools])

    async def process_query(self, query: str) -> str:
        tools = (await self.session.list_tools()).tools
        tool_specs = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema
            } for t in tools
        ]

        messages = [{"role": "user", "content": query}]
        response = self.anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            tools=tool_specs,
            messages=messages,
        )

        final_response = []

        for item in response.content:
            if item.type == "text":
                final_response.append(item.text)
            elif item.type == "tool_use":
                result = await self.session.call_tool(item.name, item.input)
                final_response.append(result.content)

        return "\n".join(final_response)

    async def run(self):
        print("Enter query (type 'quit' to exit):")
        while True:
            query = input(">>> ").strip()
            if query.lower() == "quit":
                break
            try:
                result = await self.process_query(query)
                print(result)
            except Exception as e:
                print(f"Error: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
    client = MCPClient()
    await client.connect(sys.argv[1])
    await client.run()
    await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
