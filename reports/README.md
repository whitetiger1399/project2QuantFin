# Report build

`build_report_ai_capability.py` is the only active report builder. It reads pinned, immutable AI-capability runs and does not train or modify a model.

After the revised pipeline and all verification commands pass, export the
`REPORT_*` evidence variables listed in the canonical runbook and run:

```bash
python reports/build_report_ai_capability.py
python /Users/whitetiger/.codex/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/render_docx.py \
  reports/Project2_Team16_Report.docx \
  --output_dir reports/_render_final \
  --emit_pdf
cp reports/_render_final/Project2_Team16_Report.pdf \
  reports/Project2_Team16_Report.pdf
```

The local `_render_final` directory is ignored because it is reproducible QA
output. Inspect every rendered page at full size before copying the PDF. Confirm
figure labels, equations, tables, captions, page numbering, contents-page
references, the alphabetical author list, and the Appendix A evidence IDs.

The final deliverables are:

- `Project2_Team16_Report.docx`
- `Project2_Team16_Report.pdf`

The report currently presents 2025 as a historical protocol replication and January–September 2026 as a separate retrospective no-reselection extension. Do not relabel either period as a new pristine holdout.
