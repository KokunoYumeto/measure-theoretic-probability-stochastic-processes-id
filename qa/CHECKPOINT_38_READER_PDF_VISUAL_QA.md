# Checkpoint 38 PDF visual QA

Status: pass for visual integrity; the PDF is a static supplementary reader and
the offline HTML remains the canonical interactive/accessibility surface.

- Artifact: `output/pdf/00_PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_38.pdf`
- Scope: front matter and sampled pages across the 447-page A4 document,
  including the complete Lab 05 print boundary (pages 346–350), mastery pages,
  and both assessment forms.
- Checks: no clipping, overlap, broken images, missing glyphs, raw MathJax
  errors, or page-edge overflow observed; headings, links, panels, and the
  four-by-fifteen Lab 05 table reflow remain readable.
- Known non-blocking layout notes: a large intentional white area follows the
  Lab 05 code block on page 347; isolated heading widows occur at the starts of
  units on pages 379, 417, and 433; page 432 has extra lead-in space before
  Form B. These do not obscure content or alter reading order.
- Accessibility note: PDF equations are rendered as vector MathJax outlines
  and may not be exposed as `/ActualText` by PDF text extraction. The HTML
  reader retains semantic MathJax/ARIA and is the authoritative accessible
  surface; this limitation is disclosed rather than silently claimed away.

The PDF receipt records the deterministic renderer diagnostics, page census,
print-table reflow, metadata, and source-manifest bindings.
