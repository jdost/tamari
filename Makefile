PYTHONVERSION = $(shell python --version 2>&1 | sed 's/Python //g')
PYTHONMAJOR = $(firstword $(subst ., ,${PYTHONVERSION}))
PYTHONPATH = PYTHONPATH=$(PWD)/src

ifeq "${PYTHONMAJOR}" "2"
	NOSEOPTS = --with-color
else
	NOSEOPTS =
endif

LINTEROPTS= --ignore=F401 --max-complexity 12

init:
	pip install -r requirements.txt
	cp ./src/tamari/settings.py_template ./src/tamari/settings.py

populate:
	${PYTHONPATH} python ./etc/populate.py

unittest:
	nosetests ${NOSEOPTS} ./tests/test_*.py

lint:
	flake8 ${LINTEROPTS} src/
	flake8 ${LINTEROPTS} tests/

test: lint unittest

clean:
	rm -f ./src/tamari/*.pyc
	rm -f ./src/tamari/database/*.pyc
	rm -f ./tests/*.pyc

shell:
	${PYTHONPATH} python ./etc/console.py

serve:
	${PYTHONPATH} python ./bin/tamari
