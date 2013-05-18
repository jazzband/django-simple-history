all: init docs test

init:
	pip install tox coverage Sphinx

test:
	coverage erase
	tox
	coverage html

docs: documentation

documentation:
	sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html
