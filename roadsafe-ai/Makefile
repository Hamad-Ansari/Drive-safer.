.PHONY: data train test lint run

data:
	python -m roadsafe.ml.generate_data

train:
	python -m roadsafe.ml.train

test:
	python -m pytest -q

lint:
	python -m ruff check .

run:
	streamlit run app.py --server.address 0.0.0.0
