
build:
	python setup.py sdist

push:
	python -m twine upload dist/*

update: build push
