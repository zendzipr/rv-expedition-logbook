.PHONY: validate test render-sample render-html-sample import-sample ingest-sample rtw-sample clean

validate:
	uv run python scripts/validate.py

test:
	uv run python -m unittest discover -s tests

render-sample:
	uv run python -m rv_logbook render examples/sample-trip.json output/sample-binder.md

render-html-sample:
	uv run python -m rv_logbook render-html examples/sample-trip.json output/sample-report.html

import-sample:
	uv run python -m rv_logbook import-csv fuel-stop examples/sample-fuel-stops.csv output/fuel-stops.json
	uv run python -m rv_logbook import-csv expense examples/sample-expenses.csv output/expenses.json

ingest-sample:
	uv run python -m rv_logbook ingest-csv fuel-stop examples/sample-trip.json examples/sample-fuel-stops-single.csv output/ingested-trip.json

rtw-sample:
	uv run python -m rv_logbook import-rtw examples/sample-rtw-export.json output/rtw-trip.json

clean:
	rm -rf output
