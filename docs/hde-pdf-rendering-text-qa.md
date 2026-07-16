# HDE PDF rendering text QA

## Problem

Bot-generated report PDFs were valid files and visually generated from full HTML, but `pdftotext` returned mostly blank/control output. The HTML sidecar contained the expected headings and chart content, so the failure was in PDF rendering, not chart/report data.

## Fix

The report renderer now avoids remote web fonts and decorative pictograph headings for wkhtmltopdf output:

- PDF CSS uses system fonts (`Arial`, `Georgia`) instead of Google web fonts.
- `_pdf_safe_html()` strips decorative emoji/pictographs before writing the wkhtmltopdf HTML sidecar.
- wkhtmltopdf is called with explicit UTF-8 encoding.

This preserves the report content while making generated PDFs searchable/text-extractable for QA and more reliable inside Telegram clients.

## Verification expectation

For a fresh generated natal PDF:

- `pdftotext` should include headings such as `Your Human Design Natal Chart`, `Design at a Glance`, and `Gates + Planets`.
- PDF file size should remain substantial (>100KB) and first-page PNG render should succeed.
- Guest bot report follow-up should still return PDF media metadata and the router should have a host-visible file to attach.

This is a focused PDF QA gate, not a full product suite.
