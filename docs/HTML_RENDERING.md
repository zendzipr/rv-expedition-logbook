# HTML Rendering

The project now supports a second output format from the same structured trip data: HTML.

## Render an HTML report

```bash
python3 -m rv_logbook render-html examples/sample-trip.json output/sample-report.html
```

This produces a standalone HTML report with:

- trip overview
- summary stats
- travel day details
- campground section
- captain's log entries
- fuel stops table
- expenses table
- maintenance table

## Why this matters

This proves the system is knowledge-first rather than template-first.

The same validated trip JSON and typed domain objects can now produce:

- Markdown binder output
- HTML report output

Future renderers can build on the same domain layer instead of inventing their own logic.
