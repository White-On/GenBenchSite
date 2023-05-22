help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  install    to install requirements"
	@echo "  dev        to install dev requirements"
	@echo "  docs       to generate docs"
	@echo "  test       to run tests"
	@echo "  black      to run black"
	@echo "  clean      to remove cache and black"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

remove_cache : 
	rm -rf __pycache__ 

docs:

test:

black:
	black .

clean :
	remove_cache black
