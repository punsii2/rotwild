all: venv/stamp

venv/stamp: requirements.txt
	test -d venv || python3 -m venv venv
	. ./venv/bin/activate; pip install -Ur requirements.txt
	touch venv/stamp

#test: venv
#    . venv/bin/activate; nosetests project/test

clean:
	rm -rf venv
	find -iname "*.pyc" -delete
