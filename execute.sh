
python3 -m pip install -r requirements.txt
#python3 scripts/prepare.py data/raw_total.csv data/prepared_total.csv
#python3 src/app.py
cd src && gunicorn src.app:app