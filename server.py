"""
OpenPaper MCP Server

Exposes OpenPaper's academic paper generation API as MCP tools.
Users need an OpenPaper account and their Bearer token.

Get your token from openpaper.dev → Network tab → any API request → Authorization header.
"""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

API_URL = os.environ.get("OPENPAPER_API_URL", "https://api.openpaper.dev")
API_TOKEN = os.environ.get("OPENPAPER_API_TOKEN", "")

mcp = FastMCP("openpaper")


def _headers() -> dict:
    if not API_TOKEN:
        raise ValueError(
            "OPENPAPER_API_TOKEN not set. "
            "Get your token from openpaper.dev → open DevTools → Network tab → "
            "any API request → Authorization header (the part after 'Bearer ')."
        )
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }


@mcp.tool()
def start_paper_generation(
    topic: str,
    level: str = "Graduate",
    pages: str = "15-20",
    citation_style: str = "APA 7th",
    language: str = "English",
    context: str = "",
) -> dict:
    """
    Start generating an academic research paper with verified citations.

    OpenPaper uses 18 specialized AI agents to search 500M+ academic sources
    (OpenAlex, Crossref, Semantic Scholar) and write a fully-cited paper.

    Args:
        topic: Research topic or question (max 500 chars). Be specific for better results.
               Examples: "The impact of microplastics on marine ecosystems",
                         "CRISPR applications in treating genetic disorders",
                         "Transformer architectures in natural language processing"
        level: Academic level. Options: "High School", "Undergraduate", "Graduate", "PhD"
        pages: Target page range. Options: "5-10", "10-15", "15-20", "20-30", "30-40", "40-50", "50-60"
               Note: 5-30 pages = 1 credit, 30-50 = 2 credits, 50-60 = 3 credits
        citation_style: Citation format. Options: "APA 7th", "MLA 9th", "Chicago 17th",
                        "Harvard", "IEEE", "Vancouver"
        language: Output language (e.g., "English", "Spanish", "French", "German")
        context: Additional context or instructions for the paper (optional, max 50,000 chars)

    Returns:
        dict with generation_id to track progress via check_paper_status()
    """
    payload = {
        "topic": topic,
        "level": level,
        "pages": pages,
        "citation_style": citation_style,
        "language": language,
        "context": context,
    }

    generation_id = None

    with httpx.Client(timeout=60) as client:
        with client.stream(
            "POST",
            f"{API_URL}/api/generate",
            headers=_headers(),
            json=payload,
        ) as response:
            if response.status_code != 200:
                body = response.read().decode()
                return {
                    "error": f"HTTP {response.status_code}",
                    "detail": body[:500],
                }

            # Read SSE stream until we get the generation_id from the 'started' event
            for line in response.iter_lines():
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                        if "generation_id" in data:
                            generation_id = data["generation_id"]
                            break
                    except json.JSONDecodeError:
                        pass
                if generation_id:
                    break

    if not generation_id:
        return {
            "error": "Failed to start generation",
            "detail": "No generation_id received from server",
        }

    return {
        "generation_id": generation_id,
        "topic": topic,
        "status": "processing",
        "message": (
            f"Paper generation started! Use check_paper_status('{generation_id}') "
            "to track progress. Papers typically take 10-20 minutes to complete."
        ),
        "track_url": f"https://openpaper.dev/generate/{generation_id}",
    }


@mcp.tool()
def check_paper_status(generation_id: str) -> dict:
    """
    Check the status and progress of a paper generation.

    Args:
        generation_id: The ID returned by start_paper_generation()

    Returns:
        dict with status, progress percentage, current phase, and download URLs when complete.

        Status values:
        - "processing": Paper is being generated. Check back in a few minutes.
        - "completed": Paper is ready! Download URLs are included.
        - "failed": Generation failed. Start a new one.

        When completed, the response includes:
        - pdf_url: Download the formatted PDF
        - docx_url: Download the Word document
        - zip_url: Download everything (PDF + DOCX + citations JSON)
        - citations_url: Download citations in JSON format
    """
    with httpx.Client(timeout=30) as client:
        response = client.get(
            f"{API_URL}/api/generate/{generation_id}/state",
            headers=_headers(),
        )

    if response.status_code == 404:
        return {"error": "Generation not found", "generation_id": generation_id}

    if response.status_code != 200:
        return {
            "error": f"HTTP {response.status_code}",
            "detail": response.text[:500],
        }

    data = response.json()
    status = data.get("status", "unknown")
    phase = data.get("current_phase", "unknown")
    progress = data.get("progress", 0)

    result = {
        "generation_id": generation_id,
        "status": status,
        "phase": phase,
        "progress_percent": progress,
        "status_message": data.get("status_message", ""),
        "topic": data.get("paper_title") or data.get("settings", {}).get("topic", ""),
        "view_url": f"https://openpaper.dev/generate/{generation_id}",
    }

    if status == "completed":
        downloads = data.get("downloads", {})
        result["downloads"] = {
            k: v for k, v in downloads.items() if v
        }
        result["tldr"] = data.get("tldr")
        result["message"] = "Paper is ready! Download URLs are in the 'downloads' field."
        # Add direct download links for easy access
        if downloads.get("pdf_url"):
            result["pdf_url"] = downloads["pdf_url"]
        if downloads.get("docx_url"):
            result["docx_url"] = downloads["docx_url"]
        if downloads.get("zip_url"):
            result["zip_url"] = downloads["zip_url"]
    elif status == "processing":
        phase_messages = {
            "connecting": "Initializing research agents...",
            "research": f"Searching academic databases ({progress}% complete)",
            "outline": "Building paper structure...",
            "writing": f"Writing paper sections ({progress}% complete)",
            "complete": "Finalizing paper...",
        }
        result["message"] = phase_messages.get(phase, f"Processing... {progress}% complete")
    elif status == "failed":
        result["message"] = "Generation failed. Use start_paper_generation() to try again."
        result["error"] = data.get("error", "Unknown error")

    return result


@mcp.tool()
def list_my_papers(limit: int = 10) -> dict:
    """
    List your previously generated papers.

    Args:
        limit: Maximum number of papers to return (1-50)

    Returns:
        dict with list of papers including their topics, status, and download URLs.
    """
    limit = max(1, min(50, limit))

    with httpx.Client(timeout=30) as client:
        response = client.get(
            f"{API_URL}/api/list",
            headers=_headers(),
        )

    if response.status_code != 200:
        return {
            "error": f"HTTP {response.status_code}",
            "detail": response.text[:500],
        }

    data = response.json()
    generations = data.get("generations", [])[:limit]

    papers = []
    for gen in generations:
        paper = {
            "generation_id": gen["id"],
            "topic": gen["topic"],
            "status": gen["status"],
            "created_at": gen.get("created_at", ""),
            "credits_used": gen.get("credits_used", 1),
        }
        if gen["status"] == "completed":
            downloads = {}
            if gen.get("pdf_url"):
                downloads["pdf"] = gen["pdf_url"]
            if gen.get("docx_url"):
                downloads["docx"] = gen["docx_url"]
            if gen.get("zip_url"):
                downloads["zip"] = gen["zip_url"]
            paper["downloads"] = downloads
            paper["tldr"] = gen.get("tldr_text", "")
        papers.append(paper)

    return {
        "total": len(papers),
        "papers": papers,
    }


if __name__ == "__main__":
    mcp.run()
