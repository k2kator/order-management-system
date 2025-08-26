.PHONY: docs
docs:
	cd docs && make html

.PHONY: clean-docs
clean-docs:
	cd docs && make clean

.PHONY: serve-docs
serve-docs:
	cd docs/build/html && python -m http.server 8000