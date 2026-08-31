"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

// Pin print magnification explicitly. Relying on host display text/DPI scale
// produced a much smaller reader after a host restart. This preserves the
// established, visually verified reading size across hosts and restarts.
const PRINT_SCALE = 1.25;

/*
 * Units are serialized after local MathJax settles, namespaced, and printed as
 * one Chromium document.  No PDF page from another document is ever overlaid.
 */
const PRINT_CSS = String.raw`
  @page {
    size: A4 portrait;
    margin: 16mm 15mm 19mm 15mm;
  }

  :root {
    color-scheme: light !important;
    --o009-paper: #ffffff !important;
    --o009-ink: #18242d !important;
    --o009-muted: #52616b !important;
    --o009-border: #aebec8 !important;
    --o009-accent: #174f78 !important;
    --o009-panel: #eef5f8 !important;
  }

  #reader-units { margin: 0 !important; padding: 0 !important; }

  .reader-unit {
    width: auto !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    color: #18242d !important;
    background: #ffffff !important;
    font-family: "Segoe UI", Arial, sans-serif !important;
    font-size: 10pt !important;
    line-height: 1.43 !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    break-before: page !important;
  }

  .reader-unit, .reader-unit * { box-sizing: border-box !important; }

  .reader-unit-boundary {
    display: flex;
    justify-content: space-between;
    gap: 4mm;
    margin: 0 0 2.5mm !important;
    color: #52616b !important;
    font-size: 7.4pt !important;
    font-weight: 700 !important;
    letter-spacing: 0.045em !important;
    line-height: 1.2 !important;
    text-transform: uppercase !important;
  }

  .reader-unit-boundary__title {
    min-width: 0;
    overflow-wrap: anywhere;
    text-align: right;
  }

  .reader-unit-boundary__marker { letter-spacing: 0 !important; }

  .reader-unit > header,
  .reader-unit > main,
  .reader-unit > aside,
  .reader-unit > p,
  .reader-unit > ol,
  .reader-unit > ul,
  .reader-unit > h1,
  .reader-unit > h2,
  .reader-unit > h3,
  .reader-unit > h4,
  .reader-unit > blockquote,
  .reader-unit > figure,
  .reader-unit > .unit,
  .reader-unit > .lab,
  .reader-unit > .component-attribution,
  .reader-unit > .edition-note {
    max-width: none !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
  }

  .reader-unit .latex,
  .reader-unit > header > ol.map,
  .reader-unit > nav[aria-label="Navigasi edisi"],
  .reader-unit > footer,
  .reader-unit button,
  .reader-unit .details button { display: none !important; }

  .reader-unit > header,
  .reader-unit #title-block-header {
    margin: 0 0 6mm !important;
    padding: 0 0 3.2mm !important;
    color: #18242d !important;
    background: transparent !important;
    border-bottom: 1.3pt solid #174f78 !important;
    break-inside: avoid-page !important;
  }

  .reader-unit > header > h1,
  .reader-unit #title-block-header h1,
  .reader-unit h1.title {
    margin: 0 !important;
    padding: 3mm 4mm !important;
    color: #ffffff !important;
    background: #174f78 !important;
    border: 0 !important;
    font-family: Georgia, "Times New Roman", serif !important;
    font-size: 22pt !important;
    font-weight: 700 !important;
    letter-spacing: -0.015em !important;
    line-height: 1.14 !important;
    text-align: left !important;
  }

  .reader-unit > header > h1 *,
  .reader-unit #title-block-header h1 *,
  .reader-unit h1.title * { color: inherit !important; }

  .reader-unit #title-block-header p.author {
    margin: 1.5mm 0 0 !important;
    color: #52616b !important;
    font-size: 8.8pt !important;
    line-height: 1.3 !important;
  }

  .reader-unit h2,
  .reader-unit h2.reader-level-2 {
    margin: 7mm 0 2.3mm !important;
    padding: 0 0 1.2mm !important;
    color: #123d5a !important;
    background: transparent !important;
    border: 0 !important;
    border-bottom: 0.7pt solid #b9c9d2 !important;
    font-family: Georgia, "Times New Roman", serif !important;
    font-size: 15pt !important;
    line-height: 1.2 !important;
    break-after: avoid-page !important;
  }

  .reader-unit h3,
  .reader-unit h3.reader-level-3 {
    margin: 5mm 0 1.8mm !important;
    color: #174f78 !important;
    font-family: Georgia, "Times New Roman", serif !important;
    font-size: 12pt !important;
    line-height: 1.24 !important;
    break-after: avoid-page !important;
  }

  .reader-unit h4 {
    margin: 4mm 0 1.4mm !important;
    color: #263f50 !important;
    font-size: 10.6pt !important;
    break-after: avoid-page !important;
  }

  .reader-unit p, .reader-unit li { orphans: 3 !important; widows: 3 !important; }
  .reader-unit p { margin: 0 0 2.5mm !important; }
  .reader-unit ol, .reader-unit ul {
    margin-top: 1.5mm !important;
    margin-bottom: 2.5mm !important;
    padding-left: 7mm !important;
  }
  .reader-unit a { color: #174f78 !important; text-decoration: none !important; }

  .reader-unit .component-attribution,
  .reader-unit .edition-note,
  .reader-unit .original-addition,
  .reader-unit .exercise,
  .reader-unit .hint,
  .reader-unit .answer,
  .reader-unit .solution,
  .reader-unit .lab {
    margin: 3mm 0 !important;
    padding: 3mm 3.5mm !important;
    border: 0.65pt solid #aebec8 !important;
    border-radius: 2.5mm !important;
    background: #f1f6f8 !important;
    box-shadow: none !important;
  }
  .reader-unit .component-attribution {
    margin-bottom: 5mm !important;
    border-left: 2.3pt solid #174f78 !important;
    font-size: 8.7pt !important;
    line-height: 1.35 !important;
  }
  .reader-unit .edition-note { border-left: 2.3pt solid #8a5a00 !important; }

  .reader-unit div.unit {
    margin: 3.2mm 0 !important;
    padding: 3mm 3.5mm !important;
    color: #18242d !important;
    background: #eef5f8 !important;
    border: 0.65pt solid #aebec8 !important;
    border-radius: 2.5mm !important;
    box-shadow: none !important;
  }

  .reader-unit div.unit > :first-child,
  .reader-unit .lab > :first-child,
  .reader-unit .exercise > :first-child,
  .reader-unit .hint > :first-child,
  .reader-unit .answer > :first-child,
  .reader-unit .solution > :first-child { margin-top: 0 !important; }

  .reader-unit div.unit > :last-child,
  .reader-unit .lab > :last-child,
  .reader-unit .exercise > :last-child,
  .reader-unit .hint > :last-child,
  .reader-unit .answer > :last-child,
  .reader-unit .solution > :last-child { margin-bottom: 0 !important; }

  .reader-unit details {
    display: block !important;
    margin: 3mm 0 0 !important;
    padding-top: 2.5mm !important;
    border-top: 0.55pt solid #b8c7d1 !important;
  }
  .reader-unit details > summary {
    display: block !important;
    margin: 0 0 2mm !important;
    color: #174f78 !important;
    font-weight: 700 !important;
    list-style: none !important;
  }
  .reader-unit details > summary::-webkit-details-marker { display: none !important; }

  .reader-unit figure,
  .reader-unit img,
  .reader-unit table,
  .reader-unit pre,
  .reader-unit mjx-container[display="true"] { break-inside: avoid-page !important; }
  .reader-unit figure { margin: 4mm auto !important; text-align: center !important; }
  .reader-unit figure.execution-figure img {
    max-height: 220mm !important;
    width: auto !important;
    object-fit: contain !important;
  }
  .reader-unit figcaption {
    margin: 0 0 2mm !important;
    color: #40515d !important;
    font-size: 8.7pt !important;
    line-height: 1.3 !important;
  }
  .reader-unit img, .reader-unit svg { max-width: 100% !important; height: auto !important; }
  .reader-unit mjx-container { color: #111820 !important; }
  .reader-unit mjx-container[display="true"] {
    display: block !important;
    max-width: 100% !important;
    margin: 3mm auto !important;
    overflow: visible !important;
    text-align: center !important;
  }
  .reader-unit .reader-original-solution mjx-container[display="true"] {
    margin: 2mm auto !important;
  }
  .reader-unit mjx-container[display="true"] > svg { max-width: 100% !important; height: auto !important; }

  .reader-unit pre, .reader-unit code {
    font-family: "Cascadia Mono", Consolas, monospace !important;
  }
  .reader-unit pre {
    max-width: 100% !important;
    margin: 3mm 0 !important;
    padding: 3mm !important;
    color: #15212a !important;
    background: #f3f5f6 !important;
    border: 0.55pt solid #bcc8cf !important;
    border-radius: 2mm !important;
    font-size: 7.3pt !important;
    line-height: 1.35 !important;
    overflow: visible !important;
    overflow-wrap: anywhere !important;
    white-space: pre-wrap !important;
  }
  .reader-unit pre > code.sourceCode,
  .reader-unit pre > code.sourceCode > span { white-space: pre-wrap !important; }

  .reader-unit table {
    display: table !important;
    width: auto !important;
    max-width: 100% !important;
    margin: 3mm auto !important;
    border-collapse: collapse !important;
    overflow: visible !important;
    font-size: 8.3pt !important;
  }
  .reader-unit th, .reader-unit td {
    padding: 1.4mm 2mm !important;
    color: #18242d !important;
    background: #ffffff !important;
    border: 0.55pt solid #aebec8 !important;
  }

  .reader-unit table.o009-print-paired-result {
    width: 100% !important;
    table-layout: fixed !important;
    font-size: 7.8pt !important;
  }
  .reader-unit table.o009-print-paired-result caption {
    margin-bottom: 1.5mm !important;
    color: #52616b !important;
    font-size: 7.6pt !important;
    text-align: left !important;
  }
  .reader-unit table.o009-print-paired-result th {
    width: 23% !important;
    text-align: left !important;
    overflow-wrap: anywhere !important;
  }
  .reader-unit table.o009-print-paired-result td {
    width: 27% !important;
    text-align: right !important;
    overflow-wrap: anywhere !important;
  }
  .reader-unit table.o009-print-brownian-result tbody + tbody tr:first-child > * {
    border-top-width: 1.4pt !important;
    border-top-color: #607d8b !important;
  }
  .reader-unit th { background: #e8f0f4 !important; }

  /* Keep the compact Drift boundary reader-first in print.  The screen reader
     remains unchanged; this only prevents the final strong-Markov unit from
     becoming a nearly empty fifth page after the static simulator snapshot. */
  #o009-unit-032 p { margin-bottom: 1.6mm !important; }
  #o009-unit-032 h2,
  #o009-unit-032 h2.reader-level-2 { margin-top: 5mm !important; }
  #o009-unit-032 h3,
  #o009-unit-032 h3.reader-level-3 { margin-top: 3.5mm !important; }
  #o009-unit-032 div.unit {
    margin: 2mm 0 !important;
    padding: 2.2mm 3mm !important;
  }
  #o009-unit-032 details {
    margin-top: 1.8mm !important;
    padding-top: 1.5mm !important;
  }
  #o009-unit-032 details > summary {
    margin-bottom: 1.2mm !important;
    break-after: avoid-page !important;
  }
  #brown-drift-offline-lab { margin-bottom: 1.5mm !important; }
  #brown-drift-chart {
    width: auto !important;
    max-height: 72mm !important;
    margin: 0 auto !important;
  }
  #brown-drift-offline-lab table { margin: 1.5mm auto !important; }
`;

const FOOTER_TEMPLATE = String.raw`
  <style>
    * { box-sizing: border-box; }
    html, body { width: 100%; margin: 0; padding: 0; }
    .reader-footer {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 22mm;
      column-gap: 4mm;
      width: 100%;
      margin: 0;
      padding: 2.1mm 15mm 0;
      color: #66757e;
      border-top: 0.35pt solid #c7d1d7;
      font-family: Arial, sans-serif;
      font-size: 7.2pt;
      line-height: 1;
      -webkit-print-color-adjust: exact;
    }
    .reader-footer__pages {
      width: 22mm;
      white-space: nowrap;
      text-align: right;
    }
  </style>
  <div class="reader-footer">
    Probabilitas Teoretis-Ukuran dan Proses Stokastik &middot; edisi kerja id-ID
    <span class="reader-footer__pages"><span class="pageNumber"></span></span>
  </div>
`;

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function settlePage(page) {
  await page.evaluate(async () => {
    const bounded = (promise, milliseconds) => Promise.race([
      Promise.resolve(promise).catch(() => undefined),
      new Promise((resolve) => setTimeout(resolve, milliseconds)),
    ]);
    if (document.fonts && document.fonts.ready) {
      await bounded(document.fonts.ready, 30000);
    }
    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
      await bounded(window.MathJax.startup.promise, 30000);
    }
    document.querySelectorAll("img[loading]").forEach((image) => {
      image.removeAttribute("loading");
    });
    await Promise.all(Array.from(document.images).map((image) => {
      if (image.complete) {
        return image.decode ? bounded(image.decode(), 5000) : undefined;
      }
      return bounded(new Promise((resolve) => {
        image.addEventListener("load", resolve, { once: true });
        image.addEventListener("error", resolve, { once: true });
      }), 5000);
    }));
  });
}

async function prepareUnit(browser, unit, index, includedTargets) {
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 1 });
  try {
    await page.emulateMedia({ media: "screen", colorScheme: "light" });
    await page.goto(unit.url, { waitUntil: "networkidle", timeout: 120000 });
    await page.evaluate(() => {
      document.querySelectorAll("details").forEach((node) => { node.open = true; });
      document.querySelectorAll("img[loading]").forEach((image) => {
        image.removeAttribute("loading");
      });
    });
    await settlePage(page);
    await page.waitForTimeout(250);
    return await page.evaluate(({ unitIndex, unitTargets }) => {
      const images = Array.from(document.images);
      const bodyText = document.body.innerText || "";
      const diagnostics = {
        title: document.title,
        details: document.querySelectorAll("details").length,
        openDetails: document.querySelectorAll("details[open]").length,
        mathJax: document.querySelectorAll("mjx-container").length,
        images: images.length,
        brokenImages: images.filter((image) => !image.complete || image.naturalWidth === 0).map((image) => image.getAttribute("src")),
        emptyAltImages: images.filter((image) => !(image.getAttribute("alt") || "").trim()).map((image) => image.getAttribute("src")),
        externalRuntime: Array.from(document.querySelectorAll("script[src], link[rel~='stylesheet'][href], link[rel~='preload'][href]"))
          .map((node) => node.src || node.href)
          .filter((value) => /^https?:/i.test(value) && !value.startsWith(window.location.origin)),
        bodyTextCharacters: bodyText.length,
        mathErrors: Array.from(document.querySelectorAll(
          "mjx-merror, .MathJax_Error, [data-mjx-error]",
        )).map((node) => (
          node.getAttribute("data-mjx-error") || node.textContent || ""
        ).trim()),
        rawMystRoles: Array.from(bodyText.matchAll(
          /\{(?:cite|ref|prf:ref)\}`[^`]+`/g,
        ), (match) => match[0]),
        rawMathMacros: Array.from(bodyText.matchAll(
          /\\(?:Exp|Binomial|Poisson|BB|EE|PP|RR|NN|ZZ|dD|fF|lL|linop|linopell)\b/g,
        ), (match) => match[0]),
      };

      document.querySelectorAll("img").forEach((image) => {
        image.setAttribute("data-o009-current-src", image.currentSrc || image.src);
      });
      const root = document.body.cloneNode(true);
      root.querySelectorAll("script, .latex, button, nav[aria-label='Navigasi edisi']").forEach((node) => node.remove());
      Array.from(root.children)
        .filter((node) => node.tagName.toLowerCase() === "footer")
        .forEach((node) => node.remove());
      root.querySelectorAll("details").forEach((node) => { node.open = true; });
      const clonedImages = Array.from(root.querySelectorAll("img"));
      clonedImages.forEach((image) => {
        const currentSource = image.getAttribute("data-o009-current-src");
        if (currentSource) image.setAttribute("src", currentSource);
        image.removeAttribute("data-o009-current-src");
        image.removeAttribute("srcset");
        image.removeAttribute("sizes");
        image.removeAttribute("loading");
      });
      root.querySelectorAll("picture > source").forEach((node) => node.remove());

      // The Lab 04 audit has one exact 18-column result row. Its canonical
      // HTML remains horizontally scrollable, but an A4 PDF cannot expose all
      // columns that way. Reflow only that table into two name/value pairs per
      // row, preserving every label and value in source order.
      const conditionalAuditTable = root.querySelector(
        "#o009-results-conditional-martingale",
      );
      if (conditionalAuditTable) {
        const headerCells = Array.from(
          conditionalAuditTable.tHead?.rows[0]?.cells || [],
        );
        const valueRows = Array.from(
          conditionalAuditTable.tBodies?.[0]?.rows || [],
        );
        if (headerCells.length !== 18 || valueRows.length !== 1) {
          throw new Error(
            "Lab 04 print-table topology changed; refusing lossy reflow",
          );
        }
        const valueCells = Array.from(valueRows[0].cells);
        if (valueCells.length !== headerCells.length) {
          throw new Error("Lab 04 print-table header/value count mismatch");
        }
        const paired = document.createElement("table");
        paired.id = conditionalAuditTable.id;
        paired.className = "o009-print-paired-result";
        paired.setAttribute(
          "aria-label",
          "Hasil audit bersyarat dan martingal, direflow sebagai pasangan nama dan nilai untuk PDF",
        );
        const caption = document.createElement("caption");
        caption.textContent = "Hasil audit — pasangan nama dan nilai (reflow khusus PDF)";
        paired.appendChild(caption);
        const body = document.createElement("tbody");
        const half = Math.ceil(headerCells.length / 2);
        for (let index = 0; index < half; index += 1) {
          const row = document.createElement("tr");
          for (const fieldIndex of [index, index + half]) {
            if (fieldIndex >= headerCells.length) continue;
            const label = document.createElement("th");
            label.scope = "row";
            label.textContent = headerCells[fieldIndex].textContent.trim();
            const value = document.createElement("td");
            Array.from(valueCells[fieldIndex].childNodes).forEach((node) => {
              value.appendChild(node.cloneNode(true));
            });
            row.append(label, value);
          }
          body.appendChild(row);
        }
        paired.appendChild(body);
        conditionalAuditTable.replaceWith(paired);
        diagnostics.printTableReflows = [
          {
            id: "o009-results-conditional-martingale",
            sourceColumns: 18,
            sourceRows: 1,
            outputRows: half,
            fieldsPreserved: headerCells.length,
          },
        ];
      } else {
        diagnostics.printTableReflows = [];
      }

      // Lab 05 freezes four exact Brownian-diagnostic records with fifteen
      // fields each. Preserve the canonical screen table unchanged, but make
      // every one of its 60 label/value pairs visible on A4. Each source row
      // becomes eight print rows, in strict source-row and source-field order.
      const brownianAuditTable = root.querySelector(
        "#o009-results-brownian-diagnostics",
      );
      if (brownianAuditTable) {
        const headerCells = Array.from(
          brownianAuditTable.tHead?.rows[0]?.cells || [],
        );
        const valueRows = Array.from(
          brownianAuditTable.tBodies?.[0]?.rows || [],
        );
        if (
          headerCells.length !== 15 ||
          valueRows.length !== 4 ||
          valueRows.some((row) => row.cells.length !== 15)
        ) {
          throw new Error(
            "Lab 05 print-table topology changed; refusing lossy reflow",
          );
        }
        const normalizedText = (node) => (
          node.textContent || ""
        ).replace(/\s+/g, " ").trim();
        if (headerCells.some((cell) => normalizedText(cell).length === 0)) {
          throw new Error("Lab 05 print-table contains an empty field label");
        }
        const sourcePairs = valueRows.flatMap((sourceRow) => (
          headerCells.map((headerCell, fieldIndex) => [
            normalizedText(headerCell),
            normalizedText(sourceRow.cells[fieldIndex]),
          ])
        ));
        if (sourcePairs.some((pair) => pair[1].length === 0)) {
          throw new Error("Lab 05 print-table contains an empty field value");
        }

        const paired = document.createElement("table");
        paired.id = brownianAuditTable.id;
        paired.className = "o009-print-paired-result o009-print-brownian-result";
        paired.setAttribute(
          "aria-label",
          "Empat baris audit gerak Brown, direflow sebagai pasangan nama dan nilai untuk PDF",
        );
        const caption = document.createElement("caption");
        caption.textContent = "Hasil audit gerak Brown — empat rekaman sebagai pasangan nama dan nilai (reflow khusus PDF)";
        paired.appendChild(caption);

        for (let sourceRowIndex = 0; sourceRowIndex < valueRows.length; sourceRowIndex += 1) {
          const sourceRow = valueRows[sourceRowIndex];
          const body = document.createElement("tbody");
          body.setAttribute("data-o009-source-row", String(sourceRowIndex + 1));
          for (let fieldIndex = 0; fieldIndex < headerCells.length; fieldIndex += 2) {
            const row = document.createElement("tr");
            for (
              let pairedIndex = fieldIndex;
              pairedIndex < Math.min(fieldIndex + 2, headerCells.length);
              pairedIndex += 1
            ) {
              const label = document.createElement("th");
              label.scope = "row";
              label.textContent = normalizedText(headerCells[pairedIndex]);
              const value = document.createElement("td");
              Array.from(sourceRow.cells[pairedIndex].childNodes).forEach((node) => {
                value.appendChild(node.cloneNode(true));
              });
              row.append(label, value);
            }
            body.appendChild(row);
          }
          paired.appendChild(body);
        }

        const outputPairs = Array.from(paired.querySelectorAll("tbody tr")).flatMap((row) => {
          const cells = Array.from(row.children);
          if (cells.length !== 2 && cells.length !== 4) {
            throw new Error("Lab 05 print-table emitted an invalid paired row");
          }
          const pairs = [];
          for (let index = 0; index < cells.length; index += 2) {
            if (cells[index].tagName !== "TH" || cells[index + 1].tagName !== "TD") {
              throw new Error("Lab 05 print-table emitted an invalid label/value pair");
            }
            pairs.push([
              normalizedText(cells[index]),
              normalizedText(cells[index + 1]),
            ]);
          }
          return pairs;
        });
        if (JSON.stringify(outputPairs) !== JSON.stringify(sourcePairs)) {
          throw new Error(
            "Lab 05 print-table label/value sequence changed; refusing lossy reflow",
          );
        }
        const outputRows = paired.querySelectorAll("tbody tr").length;
        if (outputRows !== 32 || outputPairs.length !== 60) {
          throw new Error("Lab 05 print-table did not preserve all 60 fields");
        }

        brownianAuditTable.replaceWith(paired);
        diagnostics.printTableReflows.push({
          id: "o009-results-brownian-diagnostics",
          sourceColumns: 15,
          sourceRows: 4,
          outputRows,
          fieldsPreserved: outputPairs.length,
          sourceOrderPreserved: true,
        });
      }

      const prefix = `o009-u${String(unitIndex + 1).padStart(2, "0")}-`;
      const idMap = new Map();
      root.querySelectorAll("[id]").forEach((node) => {
        const oldId = node.id;
        const newId = `${prefix}${oldId}`;
        idMap.set(oldId, newId);
        node.id = newId;
      });

      const rewriteUrlFragments = (value) => value.replace(
        /url\(\s*(['"]?)#([^)'"\s]+)\1\s*\)/g,
        (match, quote, id) => idMap.has(id) ? `url(${quote}#${idMap.get(id)}${quote})` : match,
      );
      const rewriteTokenList = (value) => value.split(/\s+/).map((token) => idMap.get(token) || token).join(" ");
      const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const absoluteUrl = (value, base = document.baseURI) => {
        try { return new URL(value, base).href; } catch (_error) { return value; }
      };
      const absolutizeCssUrls = (value, base = document.baseURI) => value.replace(
        /url\(\s*(['"]?)([^)'"\s]+)\1\s*\)/g,
        (match, _quote, target) => {
          if (/^(?:#|data:|blob:)/i.test(target)) return match;
          return `url("${absoluteUrl(target, base)}")`;
        },
      );
      const rewriteStyleText = (value) => {
        let result = absolutizeCssUrls(rewriteUrlFragments(value));
        for (const [oldId, newId] of idMap) {
          result = result.replace(
            new RegExp(`#${escapeRegExp(oldId)}(?![\\w-])`, "g"),
            `#${newId}`,
          );
        }
        return result;
      };
      const absoluteSrcset = (value) => {
        if (/^\s*data:/i.test(value)) return value;
        return value.split(",").map((candidate) => {
          const parts = candidate.trim().split(/\s+/);
          if (!parts[0]) return candidate;
          parts[0] = absoluteUrl(parts[0]);
          return parts.join(" ");
        }).join(", ");
      };

      root.querySelectorAll("*").forEach((node) => {
        for (const attribute of [
          "aria-labelledby", "aria-describedby", "aria-controls", "aria-flowto",
          "aria-owns", "headers", "itemref", "for", "list", "form",
          "aria-activedescendant", "aria-details", "aria-errormessage",
        ]) {
          if (node.hasAttribute(attribute)) node.setAttribute(attribute, rewriteTokenList(node.getAttribute(attribute)));
        }
        for (const attribute of ["clip-path", "fill", "filter", "mask", "marker-start", "marker-mid", "marker-end"]) {
          if (node.hasAttribute(attribute)) node.setAttribute(attribute, rewriteUrlFragments(node.getAttribute(attribute)));
        }
        if (node.hasAttribute("style")) node.setAttribute("style", rewriteStyleText(node.getAttribute("style")));
        for (const attribute of ["src", "poster", "data"]) {
          if (node.hasAttribute(attribute)) node.setAttribute(attribute, absoluteUrl(node.getAttribute(attribute)));
        }
        if (node.hasAttribute("srcset")) node.setAttribute("srcset", absoluteSrcset(node.getAttribute("srcset")));

        for (const attribute of ["usemap", "data-target", "data-bs-target"]) {
          if (!node.hasAttribute(attribute)) continue;
          const raw = node.getAttribute(attribute);
          if (raw.startsWith("#") && idMap.has(raw.slice(1))) {
            node.setAttribute(attribute, `#${idMap.get(raw.slice(1))}`);
          }
        }

        for (const attribute of ["href", "xlink:href"]) {
          if (!node.hasAttribute(attribute)) continue;
          const raw = node.getAttribute(attribute);
          if (raw.startsWith("#")) {
            const id = raw.slice(1);
            if (idMap.has(id)) node.setAttribute(attribute, `#${idMap.get(id)}`);
            continue;
          }
          if (node.tagName.toLowerCase() === "a" && attribute === "href") {
            let target;
            try { target = new URL(raw, document.baseURI); } catch (_error) { continue; }
            if (target.origin === window.location.origin) {
              const targetInfo = unitTargets[`${target.origin}${target.pathname}`];
              if (target.pathname === window.location.pathname && target.hash) {
                const id = target.hash.slice(1);
                if (idMap.has(id)) node.setAttribute("href", `#${idMap.get(id)}`);
                else node.removeAttribute("href");
              } else if (targetInfo) {
                node.setAttribute(
                  "href",
                  target.hash
                    ? `#${targetInfo.prefix}${target.hash.slice(1)}`
                    : `#${targetInfo.wrapperId}`,
                );
              } else {
                node.removeAttribute("href");
              }
            } else {
              node.setAttribute("href", target.href);
            }
          } else {
            node.setAttribute(attribute, absoluteUrl(raw));
          }
        }
      });
      root.querySelectorAll("style").forEach((node) => {
        node.textContent = rewriteStyleText(node.textContent || "");
      });

      const mathStyles = Array.from(document.querySelectorAll("head style"))
        .filter((node) => /mjx-|MathJax|MJX/i.test(`${node.id}\n${node.textContent}`))
        .map((node) => absolutizeCssUrls(node.textContent || ""));
      return { diagnostics, bodyHTML: root.innerHTML, mathStyles };
    }, { unitIndex: index, unitTargets: includedTargets });
  } finally {
    await page.close();
  }
}

async function prepareFrontmatter(browser, url) {
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  try {
    await page.goto(url, { waitUntil: "load", timeout: 120000 });
    await settlePage(page);
    return await page.evaluate(() => {
      document.querySelectorAll(".folio").forEach((node) => node.remove());
      return {
        title: document.title,
        bodyHTML: document.body.innerHTML,
        styles: Array.from(document.querySelectorAll("head style")).map((node) => node.textContent || ""),
      };
    });
  } finally {
    await page.close();
  }
}

async function renderMaster(browser, job) {
  if (!Array.isArray(job.units) || job.units.length === 0) throw new Error("Master render requires a non-empty units array");
  const frontmatter = await prepareFrontmatter(browser, job.frontmatterUrl);
  const includedTargets = Object.fromEntries(job.units.map((unit, index) => {
    const parsed = new URL(unit.url);
    return [
      `${parsed.origin}${parsed.pathname}`,
      {
        wrapperId: `o009-unit-${String(index + 1).padStart(3, "0")}`,
        prefix: `o009-u${String(index + 1).padStart(2, "0")}-`,
      },
    ];
  }));
  const prepared = [];
  for (let index = 0; index < job.units.length; index += 1) {
    prepared.push(await prepareUnit(
      browser, job.units[index], index, includedTargets,
    ));
  }

  const missingMathStyles = prepared.filter(
    (item) => item.diagnostics.mathJax > 0 && item.mathStyles.length === 0,
  );
  if (missingMathStyles.length !== 0) {
    throw new Error(
      "A TeX-bearing unit has rendered MathJax content but no MathJax style bundle",
    );
  }
  const nonEmptyMathStyleSets = prepared
    .map((item) => item.mathStyles)
    .filter((styles) => styles.length !== 0);
  const mathStyleBundles = nonEmptyMathStyleSets.map((styles) => JSON.stringify(styles));
  if (new Set(mathStyleBundles).size > 1) {
    throw new Error(
      "Non-empty MathJax SVG style bundles differ across units; refusing global-style collision",
    );
  }
  const mathStyles = nonEmptyMathStyleSets.length === 0
    ? []
    : [...new Set(nonEmptyMathStyleSets[0])];
  const unitMarkup = prepared.map((item, index) => {
    const unit = job.units[index];
    const number = String(index + 1).padStart(3, "0");
    const marker = `O009-U${number}`;
    return `<section id="o009-unit-${number}" class="reader-unit" data-reader-unit="${index + 1}" aria-label="${escapeHtml(unit.title)}"><div class="reader-unit-boundary"><span class="reader-unit-boundary__marker">${marker} &middot; ${escapeHtml(unit.kind)}</span><span class="reader-unit-boundary__title">${escapeHtml(unit.title)}</span></div>${item.bodyHTML}</section>`;
  }).join("\n");
  const documentHTML = `<!doctype html>
<html lang="id-ID"><head><meta charset="utf-8">
<title>${escapeHtml(frontmatter.title)}</title>
${frontmatter.styles.map((style) => `<style>${style}</style>`).join("\n")}
${mathStyles.map((style) => `<style>${style}</style>`).join("\n")}
<style>${PRINT_CSS}</style></head><body>
${frontmatter.bodyHTML}
<main id="reader-units">${unitMarkup}</main>
</body></html>`;

  const page = await browser.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 1 });
  try {
    await page.emulateMedia({ media: "print", colorScheme: "light" });
    await page.setContent(documentHTML, { waitUntil: "load", timeout: 120000 });
    await settlePage(page);
    await page.waitForTimeout(250);
    const masterDiagnostics = await page.evaluate(() => {
      const images = Array.from(document.images);
      return {
        bodyTextCharacters: (document.body.innerText || "").length,
        brokenImages: images.filter((image) => !image.complete || image.naturalWidth === 0).map((image) => image.getAttribute("src")),
      };
    });
    fs.mkdirSync(path.dirname(job.output), { recursive: true });
    await page.pdf({
      path: job.output,
      format: "A4",
      preferCSSPageSize: true,
      scale: PRINT_SCALE,
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate: "<span></span>",
      footerTemplate: FOOTER_TEMPLATE,
      tagged: true,
      outline: false,
    });
    return {
      mode: "master",
      output: job.output,
      unitCount: prepared.length,
      units: prepared.map((item) => item.diagnostics),
      masterBodyTextCharacters: masterDiagnostics.bodyTextCharacters,
      masterBrokenImages: masterDiagnostics.brokenImages,
      printScale: PRINT_SCALE,
    };
  } finally {
    await page.close();
  }
}

async function main() {
  if (process.argv.length !== 3) throw new Error("Usage: node render_reader_pdf.cjs MASTER_JOB.json");
  const job = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  if (job.mode !== "master") throw new Error(`Unsupported render mode: ${job.mode}`);
  const executablePath = process.env.O009_CHROME || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
  if (!fs.existsSync(executablePath)) throw new Error(`Chromium executable not found: ${executablePath}`);
  const browser = await chromium.launch({
    headless: true,
    executablePath,
    args: ["--disable-gpu", "--font-render-hinting=none", "--allow-file-access-from-files"],
  });
  try {
    const result = await renderMaster(browser, job);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
