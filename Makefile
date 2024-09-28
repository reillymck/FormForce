install:
	apt install pylint python3-requests

format:
	find ./code -iname "*.py" -exec black -q -l 100 {} \;

pylint: format
	pylint ./code
