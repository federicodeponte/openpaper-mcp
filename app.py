"""
Floom wrapper for the OpenPaper MCP server.

Exposes each MCP tool as a Floom action so the same server code can run both
as an MCP stdio server (via server.py) and as a Floom marketplace app.

Requires the OPENPAPER_API_TOKEN secret. Users get it from openpaper.dev:
DevTools (F12) -> Application -> Cookies -> https://openpaper.dev -> the
`auth_token` cookie value (a durable 30-day token).
"""

import os

from floom import app, context

# Import the existing MCP tool functions directly. They already handle the
# OpenPaper API calls and error formatting, so the wrapper stays thin.
import server as _mcp


def _ensure_token() -> None:
    token = context.get_secret("OPENPAPER_API_TOKEN")
    if not token:
        raise ValueError(
            "OPENPAPER_API_TOKEN secret is not set. "
            "Get your token from openpaper.dev -> DevTools (F12) -> Application -> "
            "Cookies -> https://openpaper.dev -> the `auth_token` cookie value "
            "(a durable 30-day token; do not use the short-lived Authorization header)."
        )
    # server.py reads the token from the process env, so mirror it there.
    os.environ["OPENPAPER_API_TOKEN"] = token
    _mcp.API_TOKEN = token


@app.action
def start_paper_generation(
    topic: str,
    level: str = "Graduate",
    pages: str = "15-20",
    citation_style: str = "APA 7th",
    language: str = "English",
    context_notes: str = "",
) -> dict:
    """
    Start generating a fully-cited academic paper on a topic.

    Returns immediately with a generation_id. Papers take 10-20 minutes to
    complete; poll with check_paper_status.

    level: "High School" | "Undergraduate" | "Graduate" | "PhD"
    pages: "5-10" | "10-15" | "15-20" | "20-30" | "30-40" | "40-50" | "50-60"
    citation_style: "APA 7th" | "MLA 9th" | "Chicago 17th" | "Harvard" | "IEEE" | "Vancouver"
    """
    _ensure_token()
    return _mcp.start_paper_generation(
        topic=topic,
        level=level,
        pages=pages,
        citation_style=citation_style,
        language=language,
        context=context_notes,
    )


@app.action
def check_paper_status(generation_id: str) -> dict:
    """
    Check the status and progress of a paper generation.

    When status is "completed", the response includes pdf_url, docx_url and
    zip_url download links.
    """
    _ensure_token()
    return _mcp.check_paper_status(generation_id=generation_id)


@app.action
def list_my_papers(limit: int = 10) -> dict:
    """
    List your previously generated papers with download links.

    limit: 1-50, default 10.
    """
    _ensure_token()
    return _mcp.list_my_papers(limit=limit)
