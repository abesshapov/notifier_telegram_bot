include .env
export

# enumeration of * .py files storage or folders is required.
files_to_fmt 	?= app tests
files_to_check 	?= app tests


## Default target
.DEFAULT_GOAL := run

## Build api docker containers
docker_up:
	docker-compose up --build -d

run:
	uvicorn app:create_app --host localhost --reload --port ${API__PORT}

## Format all
fmt: format
format: remove_imports isort black docformatter add-trailing-comma ruff


## Check code quality
chk: check
lint: check
check: flake8 pylint ruff_check black_check docformatter_check safety bandit

## Remove unused imports
remove_imports:
	autoflake -ir --remove-unused-variables \
		--ignore-init-module-imports \
		--remove-all-unused-imports \
		${files_to_fmt}


## Sort imports
isort:
	isort ${files_to_fmt}


## Format code
black:
	black ${files_to_fmt}


## Check code formatting
black_check:
	black --check ${files_to_check}


## Format docstring PEP 257
docformatter:
	docformatter -ir ${files_to_fmt}


## Check docstring formatting
docformatter_check:
	docformatter -cr ${files_to_check}


## Check pep8
flake8:
	flake8 ${files_to_check}

## Check google spec.
pylint:
	pylint ${files_to_check}

## Check ruff rules
ruff_check:
	ruff ${files_to_check}

## Reformat ruff
ruff:
	ruff ${files_to_fmt} --fix

## Check typing
mypy:
	mypy ${files_to_check}


## Check if all dependencies are secure and do not have any known vulnerabilities
safety:
	safety check --full-report


## Check code security
bandit:
	bandit -r ${files_to_check} -x tests

## Add trailing comma works only on unix.
# an error is expected on windows.
add-trailing-comma:
	find app tests -name "*.py" -exec add-trailing-comma '{}' --py36-plus \;
