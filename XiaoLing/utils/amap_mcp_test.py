import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@amap/amap-maps-mcp-server"],
	env={
        "AMAP_MAPS_API_KEY": "92f8382ccc5d6681429dc73c7ada2841"
    }
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # tools = await session.list_tools()
            # print("工具列表:", tools)

            result = await session.call_tool("maps_search_detail", arguments={"keywords": "美食"})
            print("调用结果:", result)

if __name__ == "__main__":
    asyncio.run(run())
