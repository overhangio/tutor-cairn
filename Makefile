.DEFAULT_GOAL := help
.PHONY: docs
SRC_DIRS = ./tutorcairn
BLACK_OPTS = --exclude templates ${SRC_DIRS}

# Warning: These checks are not necessarily run on every PR.
test: test-lint test-types test-format test-pythonpackage  # Run some static checks.

test-format: ## Run code formatting tests
	black --check --diff $(BLACK_OPTS)

test-lint: ## Run code linting tests
	pylint --errors-only --enable=unused-import,unused-argument --ignore=templates --ignore=docs/_ext ${SRC_DIRS}

test-types: ## Run type checks.
	mypy --exclude=templates --ignore-missing-imports --implicit-reexport --strict ${SRC_DIRS}

build-pythonpackage: ## Build the "tutor-cairn" python package for upload to pypi
	python -m build --sdist

test-pythonpackage: build-pythonpackage ## Test that package can be uploaded to pypi
	twine check dist/tutor_cairn-$(shell make version).tar.gz

format: ## Format code automatically
	black $(BLACK_OPTS)

isort: ##  Sort imports. This target is not mandatory because the output may be incompatible with black formatting. Provided for convenience purposes.
	isort --skip=templates ${SRC_DIRS}

changelog-entry: ## Create a new changelog entry.
	scriv create

changelog: ## Collect changelog entries in the CHANGELOG.md file.
	scriv collect

version: ## Print the current tutor-cairn version
	@python -c 'import io, os; about = {}; exec(io.open(os.path.join("tutorcairn", "__about__.py"), "rt", encoding="utf-8").read(), about); print(about["__version__"])'

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/@               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' | tr '@' '\n' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
