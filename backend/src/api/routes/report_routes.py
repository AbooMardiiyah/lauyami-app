"""API routes for generating summary reports."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

from src.api.services.report_service import generate_summary_report
from src.utils.logger_util import setup_logging

logger = setup_logging()

router = APIRouter()


class GenerateReportRequest(BaseModel):
    """Request model for generating a summary report."""
    analysis_text: str
    document_filename: str
    session_id: str
    format: str = "text" 


@router.post("/generate")
async def generate_report(request: GenerateReportRequest):
    """Generate a summary report from analysis text.
    
    Args:
        request: Report generation request
        
    Returns:
        Report in requested format (text, html, or json)
    """
    logger.info(
        f"Generating report: format={request.format}, "
        f"session={request.session_id}, file={request.document_filename}"
    )
    
    try:
        reports = generate_summary_report(
            analysis_text=request.analysis_text,
            document_filename=request.document_filename,
            session_id=request.session_id,
        )
        
        if request.format == "html":
            return Response(
                content=reports["html"],
                media_type="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename=lauyami_report_{request.session_id}.html"
                },
            )
        elif request.format == "json":
            return Response(
                content=reports["json"],
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=lauyami_report_{request.session_id}.json"
                },
            )
        else:  # text
            return Response(
                content=reports["text"],
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename=lauyami_report_{request.session_id}.txt"
                },
            )
    
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )

