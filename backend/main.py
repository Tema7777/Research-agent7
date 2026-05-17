from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI Research Agent MVP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=160)


class ResearchResponse(BaseModel):
    topic: str
    markdown_report: str
    markdown_path: str
    pdf_path: str


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/research", response_model=ResearchResponse)
def run_research(payload: ResearchRequest) -> ResearchResponse:
    topic = clean_topic(payload.topic)
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    markdown_report = build_markdown_report(topic)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = slugify(topic)
    base_name = f"{timestamp}_{slug}"

    markdown_path = REPORTS_DIR / f"{base_name}.md"
    pdf_path = REPORTS_DIR / f"{base_name}.pdf"

    markdown_path.write_text(markdown_report, encoding="utf-8")
    write_pdf(markdown_report, pdf_path)

    return ResearchResponse(
        topic=topic,
        markdown_report=markdown_report,
        markdown_path=str(markdown_path.relative_to(ROOT_DIR)),
        pdf_path=str(pdf_path.relative_to(ROOT_DIR)),
    )


@app.get("/api/reports/{filename}")
def download_report(filename: str):
    file_path = REPORTS_DIR / filename
    if not file_path.exists() or file_path.suffix.lower() not in {".md", ".pdf"}:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(file_path)


def clean_topic(topic: str) -> str:
    return re.sub(r"\s+", " ", topic).strip()


def slugify(topic: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", topic).strip().lower()
    return re.sub(r"[-\s]+", "-", cleaned)[:50] or "research-topic"


def build_markdown_report(topic: str) -> str:
    date_str = datetime.utcnow().strftime("%B %d, %Y")

    return f"""# Research Report: {topic}\n\n**Generated:** {date_str}  
**Scope:** High-level exploratory analysis for local MVP workflows.\n\n## Summary\n{topic} is an important area with broad impact across technology, operations, and long-term planning. This report provides a practical, structured overview that can guide deeper follow-up research and decision-making.\n\n## Key Insights\n- **Growing relevance:** Interest in {topic} continues to increase as organizations seek efficient and scalable approaches.\n- **Execution matters:** Outcomes depend less on theory and more on implementation quality, team readiness, and measurable goals.\n- **Risk and governance:** Responsible adoption requires attention to ethics, compliance, and transparent communication.\n- **Continuous learning:** The topic evolves quickly, so periodic review and iteration are essential.\n\n## Detailed Sections\n\n### 1) Background and Context\n{topic} has moved from niche discussions into mainstream planning conversations. Teams are evaluating it not only for innovation potential, but also for cost control, operational resilience, and competitive differentiation.\n\n### 2) Current Landscape\nThe current landscape includes a mix of mature practices and emerging methods. Some organizations focus on quick wins, while others prioritize long-term platform investments. The right path depends on maturity, budget, and stakeholder alignment.\n\n### 3) Opportunities\n- Improve efficiency by reducing manual steps and duplication.\n- Increase quality and consistency through structured processes.\n- Unlock new products, services, or internal capabilities tied to {topic}.\n\n### 4) Challenges\n- Data quality and integration issues may limit impact.\n- Skills gaps can slow implementation and increase risk.\n- Change management is often underestimated and can delay adoption.\n\n### 5) Recommended Next Steps\n1. Define clear outcomes and success metrics for {topic}.\n2. Start with a pilot project that has measurable value.\n3. Build feedback loops and governance into the process from day one.\n4. Review outcomes regularly and scale what works.\n\n## Conclusion\n{topic} presents meaningful opportunities when approached with clear goals, disciplined execution, and ongoing evaluation. A phased strategy that combines experimentation with governance typically delivers the most sustainable results.\n"""


def write_pdf(markdown_text: str, output_path: Path) -> None:
    page_width, page_height = A4
    margin = 50
    line_height = 16
    max_width = page_width - (margin * 2)

    c = canvas.Canvas(str(output_path), pagesize=A4)
    y = page_height - margin

    lines = markdown_to_lines(markdown_text)

    for line in lines:
        wrapped = wrap_line(line, max_width)
        for segment in wrapped:
            if y <= margin:
                c.showPage()
                y = page_height - margin
            c.drawString(margin, y, segment)
            y -= line_height

    c.save()


def markdown_to_lines(markdown_text: str) -> list[str]:
    lines: list[str] = []
    for raw in markdown_text.splitlines():
        line = raw.strip()
        if not line:
            lines.append("")
            continue
        line = re.sub(r"^#+\s*", "", line)
        line = line.replace("**", "")
        line = line.replace("`", "")
        lines.append(line)
    return lines


def wrap_line(line: str, max_width: float, font: str = "Helvetica", size: int = 11) -> list[str]:
    if line == "":
        return [""]

    words = line.split(" ")
    wrapped: list[str] = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                wrapped.append(current)
            current = word

    if current:
        wrapped.append(current)

    return wrapped
