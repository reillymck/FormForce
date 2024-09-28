install:
	apt install pylint 
	pip install -r requirements.txt

format:
	find ./code -iname "*.py" -exec black -q -l 100 {} \;

pylint: format
	pylint ./code

test:
	python -m unittest discover -s test -p "test_*.py"
