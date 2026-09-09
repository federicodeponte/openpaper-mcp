<!-- mcp-name: io.github.federicodeponte/openpaper-mcp -->
# OpenPaper MCP Server

OpenPaper is an autonomous research engine for Claude Desktop and any MCP client. Auto research from a prompt to a fully-cited academic paper, exported as PDF, DOCX, or ZIP.

OpenPaper uses 18 specialized AI agents to search 500M+ academic sources (OpenAlex, Crossref, Semantic Scholar) and write thesis-level papers with every citation linked to a real publication.

## Setup

### 1. Get your API token

1. Go to [openpaper.dev](https://openpaper.dev) and sign in
2. Open DevTools (F12) → **Application** tab → **Storage → Cookies → `https://openpaper.dev`**
3. Copy the value of the `auth_token` cookie — that's your token

This `auth_token` is a durable 30-day token and works whether you signed in with Google or email. Do not copy the `Authorization` header from the Network tab: on most pages the browser sends no such header (the app forwards the cookie server-side), and where one does appear it is a short-lived session token that expires in about an hour, so the MCP server would stop working soon after. When the token expires, repeat these steps to get a fresh one.

### 2. Configure Claude Desktop

Add to your `claude_desktop_config.json` (no manual install needed — `uvx` fetches the published package on first run):

```json
{
  "mcpServers": {
    "openpaper": {
      "command": "uvx",
      "args": ["openpaper-mcp"],
      "env": {
        "OPENPAPER_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

<details>
<summary>Run from source instead</summary>

```bash
pip install mcp httpx
```

```json
{
  "mcpServers": {
    "openpaper": {
      "command": "python",
      "args": ["/path/to/openpaper-mcp/server.py"],
      "env": {
        "OPENPAPER_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

</details>

## Tools

### `start_paper_generation`
Start generating a paper. Returns a `generation_id` immediately.

```
Generate a graduate-level paper on "The neurobiological basis of PTSD"
using APA 7th citation style, 20-30 pages
```

### `check_paper_status`
Poll for progress and get download links when done.

```
Check the status of generation abc123
```

### `list_my_papers`
See all your previous papers with download links.

```
List my last 5 papers
```

## Example workflow

```
User: Write a paper on the impact of social media on adolescent mental health

Claude: [calls start_paper_generation("impact of social media on adolescent mental health")]
→ Generation started (ID: abc123). Checking back in a few minutes...

[later]
Claude: [calls check_paper_status("abc123")]
→ Status: processing, phase: writing, 65% complete

[later]
Claude: [calls check_paper_status("abc123")]
→ Status: completed! PDF: https://... DOCX: https://...
```

## Credits

Papers cost 1-3 credits depending on length:
- 5-30 pages: 1 credit
- 30-50 pages: 2 credits
- 50-60 pages: 3 credits

New accounts get free credits. Buy more at [openpaper.dev](https://openpaper.dev).
