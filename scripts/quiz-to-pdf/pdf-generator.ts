/**
 * Quiz PDF Generator
 *
 * Uses Puppeteer to render HTML to a print-ready PDF.
 * Generates quiz and answer key separately so answer key
 * is not included in page numbering.
 */

import puppeteer, { Browser, Page } from 'puppeteer';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import * as fs from 'fs';
import type { RenderedQuiz } from './renderer';

export interface PdfGeneratorOptions {
  outputPath: string;
  margin: string;
  version?: string;
  initialsSpace?: boolean;
  includeCover?: boolean;
}

/**
 * Wait for Mermaid diagrams to render on a page.
 */
async function waitForMermaid(page: Page): Promise<void> {
  const hasMermaid = await page.evaluate(() => {
    return document.querySelectorAll('.mermaid').length > 0;
  });

  if (hasMermaid) {
    await page.waitForFunction(
      () => {
        const mermaidElements = document.querySelectorAll('.mermaid');
        return Array.from(mermaidElements).every(
          (el) => el.querySelector('svg') !== null
        );
      },
      { timeout: 10000 }
    );
  }
}

/**
 * Generate a PDF buffer from HTML content.
 */
async function generatePdfBuffer(
  browser: Browser,
  html: string,
  margin: string
): Promise<Buffer> {
  const page = await browser.newPage();

  try {
    await page.setContent(html, {
      waitUntil: 'networkidle0',
    });

    await waitForMermaid(page);

    const pdfBuffer = await page.pdf({
      format: 'Letter',
      printBackground: true,
      margin: {
        top: margin,
        right: margin,
        bottom: margin,
        left: margin,
      },
    });

    return Buffer.from(pdfBuffer);
  } finally {
    await page.close();
  }
}

/**
 * Parse a CSS margin string (e.g. "1in", "0.75in") to PDF points.
 */
function marginToPoints(margin: string): number {
  const match = margin.match(/^([\d.]+)\s*(in|cm|mm|pt|px)?$/);
  if (!match) return 72;
  const value = parseFloat(match[1]);
  switch (match[2] || 'in') {
    case 'in': return value * 72;
    case 'cm': return value * 28.35;
    case 'mm': return value * 2.835;
    case 'pt': return value;
    case 'px': return value * 0.75;
    default: return 72;
  }
}

interface StampOptions {
  margin: string;
  pageNumbers?: boolean;
  initials?: boolean;
  /** Skip initials on page index 0 (cover page). */
  skipInitialsCover?: boolean;
}

/**
 * Stamp page numbers and/or initials directly onto PDF pages using pdf-lib.
 * This embeds them as real page content so they always print.
 */
async function stampPages(
  pdfBuffer: Buffer,
  opts: StampOptions
): Promise<Buffer> {
  const pdfDoc = await PDFDocument.load(pdfBuffer);
  const font = await pdfDoc.embedFont(StandardFonts.TimesRoman);
  const pages = pdfDoc.getPages();
  const marginPts = marginToPoints(opts.margin);
  const totalPages = pages.length;

  for (let i = 0; i < pages.length; i++) {
    const page = pages[i];
    const { width, height } = page.getSize();

    // Page numbers — centered in bottom margin, close to content area
    if (opts.pageNumbers) {
      const pageText = `Page ${i + 1} / ${totalPages}`;
      const fontSize = 10;
      const textWidth = font.widthOfTextAtSize(pageText, fontSize);
      page.drawText(pageText, {
        x: (width - textWidth) / 2,
        y: marginPts * 0.75 - fontSize,
        size: fontSize,
        font,
        color: rgb(0.4, 0.4, 0.4),
      });
    }

    // Initials — top-right margin, close to content area (skip cover if requested)
    if (opts.initials && !(opts.skipInitialsCover && i === 0)) {
      const initialsText = 'Initials: ______';
      const fontSize = 9;
      const textWidth = font.widthOfTextAtSize(initialsText, fontSize);
      page.drawText(initialsText, {
        x: width - marginPts - textWidth,
        y: height - marginPts * 0.75,
        size: fontSize,
        font,
      });
    }
  }

  return Buffer.from(await pdfDoc.save());
}

/**
 * Generate a PDF from rendered quiz HTML.
 * Quiz content gets page numbers, answer key does not.
 */
export async function generatePdf(
  rendered: RenderedQuiz,
  options: PdfGeneratorOptions
): Promise<void> {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    // Generate quiz PDF and stamp page numbers + optional initials
    let quizPdfBuffer = await generatePdfBuffer(
      browser,
      rendered.quizHtml,
      options.margin
    );
    quizPdfBuffer = await stampPages(quizPdfBuffer, {
      margin: options.margin,
      pageNumbers: true,
      initials: options.initialsSpace,
      skipInitialsCover: !!options.includeCover,
    });

    // If no answer key, just write the quiz PDF
    if (!rendered.answerKeyHtml) {
      fs.writeFileSync(options.outputPath, quizPdfBuffer);
      return;
    }

    // Generate answer key PDF (no page numbers or initials)
    const answerKeyPdfBuffer = await generatePdfBuffer(
      browser,
      rendered.answerKeyHtml,
      options.margin
    );

    // Merge the two PDFs
    const quizDoc = await PDFDocument.load(quizPdfBuffer);
    const answerKeyDoc = await PDFDocument.load(answerKeyPdfBuffer);

    const mergedDoc = await PDFDocument.create();

    // Copy quiz pages
    const quizPages = await mergedDoc.copyPages(quizDoc, quizDoc.getPageIndices());
    for (const page of quizPages) {
      mergedDoc.addPage(page);
    }

    // Copy answer key pages
    const answerKeyPages = await mergedDoc.copyPages(answerKeyDoc, answerKeyDoc.getPageIndices());
    for (const page of answerKeyPages) {
      mergedDoc.addPage(page);
    }

    // Save merged PDF
    const mergedPdfBytes = await mergedDoc.save();
    fs.writeFileSync(options.outputPath, mergedPdfBytes);
  } finally {
    await browser.close();
  }
}
