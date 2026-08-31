"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const requestedRelpath =
  "output/reader/labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html";
const actualRelpath =
  "build/site/labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html";
const pagePath = path.join(root, ...actualRelpath.split("/"));
const output = path.join(root, "qa", "render", "lab05_brownian");
const reportPath = path.join(root, "qa", "ORIGINAL_LAB_05_BROWSER_QA.json");
const executablePath =
  process.env.O009_CHROME ||
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const viewports = [
  { name: "desktop", width: 1280, height: 720 },
  { name: "mobile", width: 390, height: 844 },
];

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  assert(fs.existsSync(executablePath), `Chrome executable is missing: ${executablePath}`);
  assert(fs.existsSync(pagePath), `Generated Lab 05 reader page is missing: ${pagePath}`);
  fs.mkdirSync(output, { recursive: true });

  const browser = await chromium.launch({
    executablePath,
    headless: true,
    args: ["--disable-gpu", "--allow-file-access-from-files"],
  });
  const observations = [];

  try {
    for (const viewport of viewports) {
      const page = await browser.newPage({ viewport });
      const consoleErrors = [];
      const pageErrors = [];
      const failedRequests = [];
      const externalRequests = [];

      page.on("console", (message) => {
        if (message.type() === "error") consoleErrors.push(message.text());
      });
      page.on("pageerror", (error) => pageErrors.push(String(error)));
      page.on("requestfailed", (request) => {
        failedRequests.push({
          url: request.url(),
          resourceType: request.resourceType(),
          failure: request.failure()?.errorText || "unknown",
        });
      });
      page.on("request", (request) => {
        if (/^https?:/i.test(request.url())) {
          externalRequests.push({ url: request.url(), resourceType: request.resourceType() });
        }
      });

      await page.goto(pathToFileURL(pagePath).href, { waitUntil: "load" });
      await page.evaluate(async () => {
        for (const detail of document.querySelectorAll("details")) detail.open = true;
        if (document.fonts?.ready) await document.fonts.ready;
        if (window.MathJax?.startup?.promise) await window.MathJax.startup.promise;
      });
      await page.waitForFunction(() => document.querySelectorAll("mjx-container").length > 0);
      await page.waitForTimeout(150);

      const state = await page.evaluate(() => {
        const ids = Array.from(document.querySelectorAll("[id]"), (node) => node.id);
        const duplicateIds = [...new Set(ids.filter((id, index) => ids.indexOf(id) !== index))];
        const text = document.body.innerText;
        const table = document.getElementById("o009-results-brownian-diagnostics");
        const code = document.querySelector("div.sourceCode");
        const main = document.querySelector("main");

        const box = (node) => {
          if (!node) return null;
          const style = getComputedStyle(node);
          const rect = node.getBoundingClientRect();
          return {
            tag: node.tagName.toLowerCase(),
            id: node.id || null,
            className: typeof node.className === "string" ? node.className : null,
            left: rect.left,
            right: rect.right,
            width: rect.width,
            clientWidth: node.clientWidth,
            scrollWidth: node.scrollWidth,
            overflowX: style.overflowX,
            localScrollEnabled: ["auto", "scroll"].includes(style.overflowX),
            contentFitsOrLocallyScrolls:
              node.scrollWidth <= node.clientWidth + 1 ||
              ["auto", "scroll"].includes(style.overflowX),
          };
        };

        const tableRows = table
          ? Array.from(table.querySelectorAll("tr"), (row) =>
              Array.from(row.querySelectorAll(":scope > th, :scope > td")).length,
            )
          : [];
        const externalResourceElements = Array.from(
          document.querySelectorAll(
            'script[src], link[rel~="stylesheet"][href], link[rel~="icon"][href], img[src], source[src], video[src], audio[src], iframe[src], object[data]',
          ),
          (node) => {
            const raw =
              node.getAttribute("src") ||
              node.getAttribute("href") ||
              node.getAttribute("data") ||
              "";
            return { tag: node.tagName.toLowerCase(), raw, resolved: new URL(raw, location.href).href };
          },
        ).filter((item) => /^https?:/i.test(item.resolved));

        const documentOverflow = Math.max(
          0,
          document.documentElement.scrollWidth - document.documentElement.clientWidth,
          document.body.scrollWidth - document.body.clientWidth,
        );
        const mathJaxErrors = Array.from(
          document.querySelectorAll("mjx-merror, .mjx-merror, [data-mjx-error]"),
          (node) => node.textContent.trim(),
        );
        const details = Array.from(document.querySelectorAll("details"));

        return {
          lang: document.documentElement.lang,
          title: document.title,
          bodyCharacters: text.length,
          idCount: ids.length,
          duplicateIds,
          documentMetrics: {
            documentClientWidth: document.documentElement.clientWidth,
            documentScrollWidth: document.documentElement.scrollWidth,
            bodyClientWidth: document.body.clientWidth,
            bodyScrollWidth: document.body.scrollWidth,
            horizontalOverflowPx: documentOverflow,
          },
          mainBox: box(main),
          tableBox: box(table),
          codeBox: box(code),
          table: {
            exists: Boolean(table),
            rows: tableRows.length,
            columnsByRow: tableRows,
            headerColumns: table?.querySelectorAll("thead th").length || 0,
            bodyRows: table?.querySelectorAll("tbody tr").length || 0,
          },
          details: { count: details.length, open: details.filter((node) => node.open).length },
          exerciseCount: document.querySelectorAll(".exercise").length,
          hintCount: document.querySelectorAll(".hint").length,
          answerCount: document.querySelectorAll(".answer").length,
          solutionCount: document.querySelectorAll(".solution").length,
          mathJaxContainerCount: document.querySelectorAll("mjx-container").length,
          mathJaxErrors,
          witnesses: {
            o006DependencyAndNoCopy:
              /O006\/C140/i.test(text) && /tidak ada byte\s+O006\s+yang disalin atau diterbitkan ulang/i.test(text),
            nonendorsement: /tidak didukung atau disahkan/i.test(text),
            model: /OpenAI\s+Codex\s+gpt-5\.6-sol,\s+Ultra\./i.test(text),
          },
          externalResourceElements,
        };
      });

      assert(/^id(?:-|$)/i.test(state.lang), `${viewport.name}: Indonesian lang tag missing`);
      assert(state.title.length > 0 && state.bodyCharacters > 1000, `${viewport.name}: unusable reader page`);
      assert(state.duplicateIds.length === 0, `${viewport.name}: duplicate DOM IDs`);
      assert(state.documentMetrics.horizontalOverflowPx <= 1, `${viewport.name}: page-level horizontal overflow`);
      assert(state.table.exists, `${viewport.name}: result table missing`);
      assert(state.table.rows === 5, `${viewport.name}: result table must contain 5 rows`);
      assert(
        state.table.columnsByRow.every((columns) => columns === 15),
        `${viewport.name}: result table must contain 15 columns in every row`,
      );
      assert(state.table.headerColumns === 15 && state.table.bodyRows === 4, `${viewport.name}: table topology differs`);
      assert(state.tableBox.localScrollEnabled, `${viewport.name}: table lacks local horizontal scrolling`);
      assert(state.tableBox.contentFitsOrLocallyScrolls, `${viewport.name}: table overflow is not locally contained`);
      assert(state.codeBox?.localScrollEnabled, `${viewport.name}: code block lacks local horizontal scrolling`);
      assert(state.codeBox?.contentFitsOrLocallyScrolls, `${viewport.name}: code overflow is not locally contained`);
      assert(state.details.open === state.details.count, `${viewport.name}: not all details are open`);
      assert(state.exerciseCount === 1, `${viewport.name}: expected one exercise`);
      assert(state.hintCount === 3, `${viewport.name}: expected three hints`);
      assert(state.answerCount === 1, `${viewport.name}: expected one answer`);
      assert(state.solutionCount === 1, `${viewport.name}: expected one solution`);
      assert(state.mathJaxContainerCount > 0, `${viewport.name}: MathJax produced no containers`);
      assert(state.mathJaxErrors.length === 0, `${viewport.name}: MathJax errors present`);
      assert(state.witnesses.o006DependencyAndNoCopy, `${viewport.name}: O006 dependency/no-copy note missing`);
      assert(state.witnesses.nonendorsement, `${viewport.name}: nonendorsement note missing`);
      assert(state.witnesses.model, `${viewport.name}: exact model phrase missing`);
      assert(state.externalResourceElements.length === 0, `${viewport.name}: external resource elements present`);
      assert(externalRequests.length === 0, `${viewport.name}: external network requests present`);
      assert(failedRequests.length === 0, `${viewport.name}: resource requests failed`);
      assert(consoleErrors.length === 0, `${viewport.name}: console errors present`);
      assert(pageErrors.length === 0, `${viewport.name}: page errors present`);

      const screenshotPath = path.join(output, `${viewport.name}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      observations.push({
        viewport,
        state,
        screenshot: path.relative(root, screenshotPath).replaceAll("\\", "/"),
        screenshotBytes: fs.statSync(screenshotPath).size,
        screenshotSha256: sha256(screenshotPath),
        consoleErrors,
        pageErrors,
        failedRequests,
        externalRequests,
      });
      await page.close();
    }
  } finally {
    await browser.close();
  }

  const report = {
    schema: "o009.original-lab-05-browser-qa.v1",
    status: "PASS",
    requestedRelpath,
    requestedPathExists: fs.existsSync(path.join(root, ...requestedRelpath.split("/"))),
    testedRelpath: actualRelpath,
    sourceBytes: fs.statSync(pagePath).size,
    sourceSha256: sha256(pagePath),
    executablePath,
    viewportCount: viewports.length,
    observations,
  };
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  process.stdout.write(
    `${JSON.stringify(
      {
        status: report.status,
        testedRelpath: report.testedRelpath,
        sourceBytes: report.sourceBytes,
        sourceSha256: report.sourceSha256,
        observations: observations.length,
        reportPath,
      },
      null,
      2,
    )}\n`,
  );
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
