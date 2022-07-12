# Covid Dashboard

The goal for this project was to experiment with [Dash](https://plotly.com/dash/) library in Python to create a simple *interactive* visualization for Covid data in Europe. The data was used from [OurWorldinData](https://ourworldindata.org/).

For more information look into report written in folder `report`.

## Project Structure

- `data` - contains prepared data
- `report` - contains report for the project
- `scripts` - contains scripts, currently only script to prepare data
- `src` - source code of web app
- `LICENSE` - standard MIT license
- `Procfile` - Heroku Procfile
- `execute.sh` - executes the app (install requirements and then run app with gunicorn)
- `requirements.txt` - requirements for project
- `runtime.txt` - specifies Python runtime used (for Heroku)
