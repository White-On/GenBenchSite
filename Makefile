help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "Be careful ! some commands require the installation of dev requirements"
	@echo "  install    to install requirements"
	@echo "  dev        to install dev requirements"
	@echo "  docs       to generate docs"
	@echo "  test       to run tests"
	@echo "  black      to run black"
	@echo "  clean      to remove cache and black"

install:
	python -m pip install -r requirements.txt

dev:
	python -m pip install -r requirements-dev.txt

remove_cache : 
	rm -rf __pycache__ 

docs:

test:

black:
	black .

clean :
	remove_cache black
