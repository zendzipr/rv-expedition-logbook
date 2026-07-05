# Rendering Markdown Binders

The first working end-to-end slice of the project is Markdown binder generation.

## Command

```bash
python3 scripts/render_binder.py examples/sample-trip.json examples/sample-binder.md
```

Arguments:

1. input trip JSON file
2. output Markdown file

The renderer uses only the Python standard library.

## Template source

Templates live in:

```text
templates/binder/
```

Supported placeholder syntax:

```text
{{ trip.name }}
{{ travel_day.date }}
{{ campground.rating }}
```

The renderer replaces placeholders using dotted paths from the current rendering context.

## Current rendered sections

- cover
- trip summary
- travel day dashboard for each travel day
- campground review when a travel day includes a campground object
- captain's log entries when a travel day includes journal entries
- fuel log
- expense log
- maintenance log

## Privacy

Generated binders may contain private travel details. Do not commit real generated binders unless they are sanitized examples.

The committed `examples/sample-binder.md` is generated only from sanitized sample data.
