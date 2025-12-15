/**
 * PDF Report Generator for Legal Analysis
 */

import jsPDF from 'jspdf';
import { parseAnalysisText, ParsedSection } from './analysisParser';

export async function generatePDFReport(
  analysisText: string,
  documentFilename: string
): Promise<Blob> {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  const contentWidth = pageWidth - 2 * margin;
  let yPosition = margin;

  const checkPageBreak = (requiredSpace: number) => {
    if (yPosition + requiredSpace > pageHeight - margin) {
      doc.addPage();
      yPosition = margin;
      return true;
    }
    return false;
  };

  const wrapText = (text: string, maxWidth: number, fontSize: number): string[] => {
    doc.setFontSize(fontSize);
    return doc.splitTextToSize(text, maxWidth);
  };

  doc.setFillColor(102, 126, 234); 
  doc.rect(0, 0, pageWidth, 40, 'F');
  
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(24);
  doc.setFont('helvetica', 'bold');
  doc.text('📋 Legal Analysis Report', pageWidth / 2, 20, { align: 'center' });
  
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text('Powered by Lauyami AI Legal Assistant', pageWidth / 2, 30, { align: 'center' });
  
  yPosition = 55;

  doc.setTextColor(80, 80, 80);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text(`Document: ${documentFilename}`, margin, yPosition);
  yPosition += 6;
  doc.text(`Generated: ${new Date().toLocaleString()}`, margin, yPosition);
  yPosition += 15;

  doc.setDrawColor(200, 200, 200);
  doc.line(margin, yPosition, pageWidth - margin, yPosition);
  yPosition += 10;

  const sections = parseAnalysisText(analysisText);
  
  // If no sections were parsed, add the raw text as a text section
  if (sections.length === 0) {
    sections.push({
      type: 'text',
      content: analysisText
    });
  }
  
  for (const section of sections) {
    checkPageBreak(20);

    switch (section.type) {
      case 'intro':
        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(60, 60, 60);
        const introLines = wrapText(section.content, contentWidth, 11);
        introLines.forEach(line => {
          checkPageBreak(8);
          doc.text(line, margin, yPosition);
          yPosition += 7;
        });
        yPosition += 5;
        break;

      case 'right':
        checkPageBreak(25);

        doc.setFillColor(220, 252, 231); 
        doc.roundedRect(margin, yPosition - 3, contentWidth, 0, 3, 3, 'F');
        
        const rightLines = wrapText(section.content, contentWidth - 20, 10);
        const rightHeight = rightLines.length * 6 + 8;
        doc.roundedRect(margin, yPosition - 3, contentWidth, rightHeight, 3, 3, 'F');
        
        doc.setDrawColor(134, 239, 172); 
        doc.setLineWidth(0.5);
        doc.roundedRect(margin, yPosition - 3, contentWidth, rightHeight, 3, 3, 'S');
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(22, 163, 74); 
        doc.text('✓ Your Right', margin + 5, yPosition + 4);
        
    
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(21, 128, 61); 
        yPosition += 10;
        rightLines.forEach(line => {
          doc.text(line, margin + 5, yPosition);
          yPosition += 6;
        });
        yPosition += 8;
        break;

      case 'warning':
        checkPageBreak(25);

        const warningLines = wrapText(section.content, contentWidth - 20, 10);
        const warningHeight = warningLines.length * 6 + 8;
        
        doc.setFillColor(254, 252, 232); 
        doc.roundedRect(margin, yPosition - 3, contentWidth, warningHeight, 3, 3, 'F');
        
        doc.setDrawColor(253, 224, 71);
        doc.setLineWidth(0.5);
        doc.roundedRect(margin, yPosition - 3, contentWidth, warningHeight, 3, 3, 'S');
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(202, 138, 4); 
        doc.text('⚠ Warning Found', margin + 5, yPosition + 4);
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(161, 98, 7); 
        yPosition += 10;
        warningLines.forEach(line => {
          doc.text(line, margin + 5, yPosition);
          yPosition += 6;
        });
        yPosition += 8;
        break;

      case 'predatory':
        checkPageBreak(25);

        const predatoryLines = wrapText(section.content, contentWidth - 20, 10);
        const predatoryHeight = predatoryLines.length * 6 + 8;
        
        doc.setFillColor(254, 242, 242); 
        doc.roundedRect(margin, yPosition - 3, contentWidth, predatoryHeight, 3, 3, 'F');
        
        doc.setDrawColor(252, 165, 165); 
        doc.setLineWidth(0.5);
        doc.roundedRect(margin, yPosition - 3, contentWidth, predatoryHeight, 3, 3, 'S');
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(220, 38, 38);
        doc.text('🚨 Predatory Clause Detected', margin + 5, yPosition + 4);
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(153, 27, 27); 
        yPosition += 10;
        predatoryLines.forEach(line => {
          doc.text(line, margin + 5, yPosition);
          yPosition += 6;
        });
        yPosition += 8;
        break;

      case 'text':
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(80, 80, 80);
        const textLines = wrapText(section.content, contentWidth, 10);
        textLines.forEach(line => {
          checkPageBreak(7);
          doc.text(line, margin, yPosition);
          yPosition += 6;
        });
        yPosition += 3;
        break;
    }
  }

  const totalPages = doc.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.setFont('helvetica', 'italic');
    doc.text(
      'This report is for informational purposes only and does not constitute legal advice.',
      pageWidth / 2,
      pageHeight - 10,
      { align: 'center' }
    );
    doc.text(`Page ${i} of ${totalPages}`, pageWidth - margin, pageHeight - 10, { align: 'right' });
  }

  return doc.output('blob');
}

