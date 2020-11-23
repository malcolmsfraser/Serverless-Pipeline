install:
	pip install --upgrade pip
		pip install -r requirements.txt

lint:
	pylint --disable=R,C,no-value-for-parameter visionCLI.py
