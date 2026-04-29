#!/usr/bin/env node
import process from "node:process";
import { chromium } from "playwright";

async function main() {
  const [, , url, outputPath] = process.argv;
  if (!url || !outputPath) {
    console.error("Usage: node render_slides_pdf_playwright.mjs <url> <output-pdf-path>");
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "networkidle", timeout: 180000 });

    // Ensure all images have finished loading before layout adjustments.
    await page.evaluate(async () => {
      const imageElements = Array.from(document.images || []);
      await Promise.all(
        imageElements.map(
          (img) =>
            img.complete
              ? Promise.resolve()
              : new Promise((resolve) => {
                  img.addEventListener("load", () => resolve(), { once: true });
                  img.addEventListener("error", () => resolve(), { once: true });
                })
        )
      );
    });

    // Constrain slide media to printable area to avoid clipping in generated PDFs.
    await page.addStyleTag({
      content: `
        @media print {
          .reveal {
            padding-left: 1.5vw !important;
            padding-right: 1.5vw !important;
            box-sizing: border-box !important;
          }

          .reveal .slides section img,
          .reveal .slides section video,
          .reveal .slides section canvas {
            max-width: 100% !important;
            max-height: 88vh !important;
            width: auto !important;
            height: auto !important;
            object-fit: contain !important;
          }

          .reveal .slide-background-content {
            background-size: contain !important;
            background-position: center center !important;
            background-repeat: no-repeat !important;
          }

          .reveal .slides section {
            overflow: hidden !important;
          }
        }
      `,
    });

    await page.emulateMedia({ media: "print" });

    await page.pdf({
      path: outputPath,
      printBackground: true,
      preferCSSPageSize: true,
      scale: 1,
      margin: {
        top: "0.30in",
        right: "0.45in",
        bottom: "0.30in",
        left: "0.45in",
      },
      timeout: 180000,
    });
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(String(err?.stack || err));
  process.exit(1);
});
