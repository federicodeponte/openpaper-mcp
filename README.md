<!-- mcp-name: io.github.federicodeponte/openpaper-mcp -->
# OpenPaper MCP Server

Generate fully-cited academic research papers from Claude Desktop or any MCP client.

OpenPaper uses 18 specialized AI agents to search 500M+ academic sources (OpenAlex, Crossref, Semantic Scholar) and write thesis-level papers with every citation linked to a real publication.

## Setup

### 1. Get your API token

1. Go to [openpaper.dev](https://openpaper.dev) and sign in
2. Open DevTools → Network tab
3. Click any request → find the `Authorization` header
4. Copy the value after `Bearer ` — that's your token

### 2. Install dependencies

```bash
pip install mcp httpx
```

### 3. Configure Claude Desktop

Add to your `claude_desktop_config.json`:

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
