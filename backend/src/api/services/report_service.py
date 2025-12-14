"""Service for generating summary reports of legal analysis."""

import json
from datetime import datetime

from src.utils.logger_util import setup_logging

logger = setup_logging()


def generate_summary_report(
    analysis_text: str,
    document_filename: str,
    session_id: str,
) -> dict[str, str]:
    """Generate a structured summary report from analysis text.
    
    Extracts key information and formats it for export.
    
    Args:
        analysis_text: The full analysis text
        document_filename: Name of the analyzed document
        session_id: Session ID for tracking
        
    Returns:
        dict with 'text' and 'json' versions of the report
    """
    logger.info(f"Generating summary report for session {session_id}")
    
    # Parse analysis text to extract key sections
    sections = _parse_analysis_sections(analysis_text)
    
    # Generate different formats
    text_report = _generate_text_report(
        sections, document_filename, session_id
    )
   
    json_report = _generate_json_report(
        sections, document_filename, session_id
    )
    
    return {
        "text": text_report,
        "json": json_report,
    }


def _parse_analysis_sections(analysis_text: str) -> dict[str, list[str]]:
    """Parse analysis text into structured sections.
    
    Looks for key indicators like "Your Right:", "Warning Found:", "Predatory clause".
    """
    sections = {
        "intro": [],
        "rights": [],
        "warnings": [],
        "predatory": [],
        "other": [],
    }
    
    lines = analysis_text.split("\n")
    current_section = "intro"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section markers
        if "✅" in line or "Your Right" in line:
            current_section = "rights"
        elif "⚠️" in line or "Warning Found" in line:
            current_section = "warnings"
        elif "🚨" in line or "Predatory clause" in line:
            current_section = "predatory"
        elif line.startswith("Based on") or "Introduction" in line:
            current_section = "intro"
        
        sections[current_section].append(line)
    
    return sections


def _generate_text_report(
    sections: dict[str, list[str]],
    document_filename: str,
    session_id: str,
) -> str:
    """Generate plain text report."""
    report_lines = [
        "=" * 70,
        "LAUYAMI LEGAL ANALYSIS SUMMARY REPORT",
        "=" * 70,
        f"Document: {document_filename}",
        f"Session ID: {session_id}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
    ]
    
    if sections["intro"]:
        report_lines.append("INTRODUCTION")
        report_lines.append("-" * 70)
        report_lines.extend(sections["intro"])
        report_lines.append("")
    
    if sections["rights"]:
        report_lines.append("YOUR RIGHTS")
        report_lines.append("-" * 70)
        report_lines.extend(sections["rights"])
        report_lines.append("")
    
    if sections["warnings"]:
        report_lines.append("WARNINGS")
        report_lines.append("-" * 70)
        report_lines.extend(sections["warnings"])
        report_lines.append("")
    
    if sections["predatory"]:
        report_lines.append("PREDATORY CLAUSES DETECTED")
        report_lines.append("-" * 70)
        report_lines.extend(sections["predatory"])
        report_lines.append("")
    
    if sections["other"]:
        report_lines.append("ADDITIONAL INFORMATION")
        report_lines.append("-" * 70)
        report_lines.extend(sections["other"])
        report_lines.append("")
    
    report_lines.extend([
        "=" * 70,
        "End of Report",
        "=" * 70,
    ])
    
    return "\n".join(report_lines)


def _generate_json_report(
    sections: dict[str, list[str]],
    document_filename: str,
    session_id: str,
) -> str:
    """Generate JSON report for programmatic access."""
    report = {
        "metadata": {
            "document_filename": document_filename,
            "session_id": session_id,
            "generated_at": datetime.now().isoformat(),
            "report_version": "1.0",
        },
        "analysis": {
            "introduction": sections["intro"],
            "rights": sections["rights"],
            "warnings": sections["warnings"],
            "predatory_clauses": sections["predatory"],
            "additional_info": sections["other"],
        },
        "summary": {
            "total_rights": len(sections["rights"]),
            "total_warnings": len(sections["warnings"]),
            "total_predatory_clauses": len(sections["predatory"]),
        },
    }
    
    return json.dumps(report, indent=2, ensure_ascii=False)

