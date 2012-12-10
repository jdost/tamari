LINTER=$(shell if which flake8 > /dev/null; \
					then which flake8; \
					else which true; fi)
unittest:
	nosetests --with-color ./tests/*.py

lint:
	${LINTER} ./tamari/*.py
	${LINTER} ./tamari/database/*.py
	${LINTER} ./tamari/database/*/*.py

test: lint unittest

clean:
	rm ./tamari/*.pyc

serve:
	python serve.py
