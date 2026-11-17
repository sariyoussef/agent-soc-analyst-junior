from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from log_analyse import analyser_authlog, detecter_bruteforce
from base_connaissances import rechercher_base_connaissances
import json

app = Server("soc-analyst-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Expose les outils de l'agent SOC via le protocole MCP standardisé."""
    return [
        Tool(
            name="detecter_bruteforce_mcp",
            description="Détecte les attaques par force brute dans auth.log",
            inputSchema={"type": "object", "properties": {"chemin": {"type": "string"}}}
        ),
        Tool(
            name="rechercher_politique_mcp",
            description="Recherche dans la base de connaissances de sécurité",
            inputSchema={"type": "object", "properties": {"requete": {"type": "string"}}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "detecter_bruteforce_mcp":
        chemin = arguments.get("chemin", "exemples/auth.log")
        entrees = analyser_authlog(chemin)
        res = detecter_bruteforce(entrees)
        return [TextContent(type="text", text=json.dumps(res, ensure_ascii=False))]

    elif name == "rechercher_politique_mcp":
        req = arguments.get("requete", "")
        res = rechercher_base_connaissances(req)
        return [TextContent(type="text", text=res)]

    raise ValueError(fOutil MCP inconnu: {name}")

if __name__ == "__main__":
    import asyncio
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    asyncio.run(main())
