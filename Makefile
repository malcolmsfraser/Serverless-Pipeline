setup:
	python3 -m venv ~/.pipeline
		source ~/.pipeline/bin/activate

install:
	pip install --upgrade pip
		pip install -r requirements.txt

lint:
	pylint --disable=R,C,no-value-for-parameter visionCLI.py
	
all:
	make setup
		make install
			make lint