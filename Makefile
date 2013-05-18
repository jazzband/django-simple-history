all: init docs test

init:
	pip install tox coverage Sphinx

test:
	./runtests.sh

docs: documentation

documentation:
	sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html
