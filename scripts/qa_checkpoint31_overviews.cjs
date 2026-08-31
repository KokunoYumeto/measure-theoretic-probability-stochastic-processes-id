"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const site = path.join(root, "build", "site");
const output = path.join(root, "qa", "render", "checkpoint31_overviews");
const reportPath = path.join(root, "qa", "CHECKPOINT_31_OVERVIEW_BROWSER_QA.json");
const executablePath =
  process.env.O009_CHROME ||
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const pages = [
  {
    slug: "martingales",
    relpath: "martingales/index.html",
    requiredIds: ["Summary", "External"],
    scopeNote: null,
    metadata: { previous: "../markov/index.html", next: "../brown/index.html" },
  },
  {
    slug: "markov",
    relpath: "markov/index.html",
    requiredIds: ["sum", "cha", "spe", "con", "spe2", "Apps", "External"],
    scopeNote: "markov-index-edition-scope",
    metadata: { next: "../martingales/index.html" },
  },
  {
    slug: "brown",
    relpath: "brown/index.html",
    requiredIds: ["sum", "apps", "ext", "Grimmett2"],
    scopeNote: "brown-index-edition-scope",
    metadata: { previous: "../martingales/index.html" },
  },
];

const viewports = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
];

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

async function main() {
  if (!fs.existsSync(executablePath)) {
    throw new Error(`Chrome executable is missing: ${executablePath}`);
  }
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    executablePath,
    headless: true,
    args: ["--disable-gpu", "--allow-file-access-from-files"],
  });
  const observations = [];
  try {
    for (const viewport of viewports) {
      for (const spec of pages) {
        const localPath = path.join(site, ...spec.relpath.split("/"));
        if (!fs.existsSync(localPath)) throw new Error(`Reader page missing: ${spec.relpath}`);
        const page = await browser.newPage({ viewport });
        const consoleErrors = [];
        const pageErrors = [];
        page.on("console", (message) => {
          if (message.type() === "error") consoleErrors.push(message.text());
        });
        page.on("pageerror", (error) => pageErrors.push(String(error)));
        await page.goto(pathToFileURL(localPath).href, { waitUntil: "load" });
        await page.waitForTimeout(250);
        const state = await page.evaluate(({ requiredIds, scopeNote, metadata }) => {
          const ids = Array.from(document.querySelectorAll("[id]"), (node) => node.id);
          const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
          const metadataObserved = {};
          for (const relation of Object.keys(metadata)) {
            const nodes = Array.from(document.head.querySelectorAll(`link[rel~="${relation}"]`));
            metadataObserved[relation] = nodes.map((node) => node.getAttribute("href"));
          }
          const brokenFragments = Array.from(document.querySelectorAll('a[href*="#"]'))
            .map((node) => node.getAttribute("href"))
            .filter((href) => href && href.startsWith("#") && !document.getElementById(href.slice(1)));
          const horizontalOverflow = Math.max(
            document.documentElement.scrollWidth - document.documentElement.clientWidth,
            document.body.scrollWidth - document.body.clientWidth,
          );
          const text = document.body.innerText;
          return {
            lang: document.documentElement.lang,
            title: document.title,
            heading: document.querySelector("h1, h2")?.textContent?.trim() || "",
            idCount: ids.length,
            duplicateIds: [...new Set(duplicates)],
            missingRequiredIds: requiredIds.filter((id) => !ids.includes(id)),
            scopeNoteCount: scopeNote ? document.querySelectorAll(`#${scopeNote}`).length : 0,
            metadataObserved,
            brokenFragments,
            horizontalOverflow,
            bodyCharacters: text.length,
            readerHeaderCount: document.querySelectorAll("body > header").length,
            attributionCount: document.querySelectorAll(".component-attribution").length,
          };
        }, spec);
        for (const [relation, href] of Object.entries(spec.metadata)) {
          if (JSON.stringify(state.metadataObserved[relation]) !== JSON.stringify([href])) {
            throw new Error(`${spec.relpath} ${relation} metadata differs`);
          }
        }
        if (!/^id(?:-|$)/i.test(state.lang)) {
          throw new Error(`${spec.relpath} does not declare an Indonesian language tag`);
        }
        if (!state.title || !state.heading || state.bodyCharacters < 500) {
          throw new Error(`${spec.relpath} lacks a usable reader surface`);
        }
        if (state.duplicateIds.length || state.missingRequiredIds.length || state.brokenFragments.length) {
          throw new Error(`${spec.relpath} failed ID/fragment validation`);
        }
        if (state.horizontalOverflow > 1) {
          throw new Error(`${spec.relpath} overflows ${viewport.name} by ${state.horizontalOverflow}px`);
        }
        if (spec.scopeNote && state.scopeNoteCount !== 1) {
          throw new Error(`${spec.relpath} scope note is missing or duplicated`);
        }
        if (state.readerHeaderCount !== 1 || state.attributionCount !== 1) {
          throw new Error(`${spec.relpath} reader provenance header differs`);
        }
        if (consoleErrors.length || pageErrors.length) {
          throw new Error(`${spec.relpath} browser errors: ${consoleErrors.concat(pageErrors).join(" | ")}`);
        }
        const screenshotPath = path.join(output, `${spec.slug}-${viewport.name}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        observations.push({
          relpath: spec.relpath,
          viewport,
          state,
          sourceBytes: fs.statSync(localPath).size,
          sourceSha256: sha256(localPath),
          screenshot: path.relative(root, screenshotPath).replaceAll("\\", "/"),
          screenshotBytes: fs.statSync(screenshotPath).size,
          screenshotSha256: sha256(screenshotPath),
          consoleErrors,
          pageErrors,
        });
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }
  const report = {
    schema: "o009.checkpoint31-overview-browser-qa.v1",
    checkpoint: 31,
    status: "PASS",
    executablePath,
    pages: pages.length,
    viewports: viewports.length,
    observations,
  };
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  process.stdout.write(`${JSON.stringify({ status: report.status, observations: observations.length, reportPath }, null, 2)}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
