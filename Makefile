.PHONY: validate test render-sample render-html-sample import-sample ingest-sample rtw-sample clean

PYRUN := $(shell if command -v uv >/dev/null 2>&1; then echo "uv run python"; else echo "python3"; fi)

validate:
	$(PYRUN) scripts/validate.py

test:
	$(PYRUN) -m unittest discover -s tests

render-sample:
	$(PYRUN) -m rv_logbook render examples/sample-trip.json output/sample-binder.md

render-html-sample:
	$(PYRUN) -m rv_logbook render-html examples/sample-trip.json output/sample-report.html

import-sample:
	$(PYRUN) -m rv_logbook import-csv fuel-stop examples/sample-fuel-stops.csv output/fuel-stops.json
	$(PYRUN) -m rv_logbook import-csv expense examples/sample-expenses.csv output/expenses.json

ingest-sample:
	$(PYRUN) -m rv_logbook ingest-csv fuel-stop examples/sample-trip.json examples/sample-fuel-stops-single.csv output/ingested-trip.json

rtw-sample:
	$(PYRUN) -m rv_logbook import-rtw examples/sample-rtw-export.json output/rtw-trip.json

clean:
	rm -rf output
