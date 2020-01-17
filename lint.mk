# Make commands for linting

SHELL := /bin/bash -euxo pipefail

.PHONY: yapf
yapf:
	yapf \
	    --diff \
	    --recursive \
	    --exclude .eggs \
	    .

.PHONY: fix-yapf
fix-yapf:
	yapf \
	    --in-place \
	    --recursive \
	    --exclude .eggs \
	    .

.PHONY: mypy
mypy:
	mypy *.py src/ tests/ docs/source/

.PHONY: check-manifest
check-manifest:
	check-manifest .

.PHONY: doc8
doc8:
	doc8 .

.PHONY: flake8
flake8:
	flake8 .

.PHONY: isort
isort:
	isort --recursive --check-only

.PHONY: pip-extra-reqs
pip-extra-reqs:
	pip-extra-reqs src/

.PHONY: pip-missing-reqs
pip-missing-reqs:
	pip-missing-reqs src/

.PHONY: pylint
pylint:
	pylint *.py src/ tests/ docs/

.PHONY: pyroma
pyroma:
	pyroma --min 10 .

.PHONY: vulture
vulture:
	vulture --min-confidence 100 --exclude _vendor --exclude .eggs .

.PHONY: linkcheck
linkcheck:
	$(MAKE) -C docs/ linkcheck SPHINXOPTS=$(SPHINXOPTS)

.PHONY: spelling
spelling:
	$(MAKE) -C docs/ spelling SPHINXOPTS=$(SPHINXOPTS)

.PHONY: shellcheck
shellcheck:
	# At the time of writing, there are no shell files.
	# shellcheck --exclude SC2164,SC1091 */*.sh

.PHONY: autoflake
autoflake:
	autoflake \
	    --in-place \
	    --recursive \
	    --remove-all-unused-imports \
	    --remove-unused-variables \
	    --expand-star-imports \
	    --exclude _vendor,release \
	    .

.PHONY: pydocstyle
pydocstyle:
	pydocstyle
