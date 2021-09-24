<p align="center">
  <a href="https://rankr.online"><img src="https://rankr.online/static/media/appLogo.250b85cc.svg" height="100" alt="rankr logo"></a>
</p>

# rankr

**rankr** is a platform for aggregating the results of different academic rankings.

## What does it do?

rankr crawls university ranking tables and stores the results in `.csv` files, after some pre-processing. At the moment, it supports [QS](https://www.topuniversities.com/), [Shanghai (ARWU)](http://www.shanghairanking.com), and [Times Higher Education (THE)](https://www.timeshighereducation.com) for both their **world university rankings** and **subject rankings**.

To match academic institutions across ranking systems (to aggregate their results), it is necessary to have an identification system that assigns unique IDs to institutions. After some research, the [GRID ID](https://grid.ac) system was chosen, which provides a free database of about 100,000 research institutions; for example, the GRID ID for Sharif University of Technology is `grid.412553.4`.

rankr first stores the entire GRID ID data ([release 2020-06-29](https://digitalscience.figshare.com/articles/GRID_release_2020-06-29/12587828)) in a database (using [SQLAlchemy](https://www.sqlalchemy.org)) and then iterates through each crawled ranking table and tries to match institutions with their respective GRID counterparts.

To achieve this, several methods are employed using:

- Institution profile URL in each ranking table
- Institution name & country
- Fuzzy matching of institutions
- Manual matching

It should be noted that the metadata from the GRID database is preferred in case of any discrepancy. For example, if a ranking website lists an institution under `Country A`, but the GRID database records it under `Country B`, the latter will be selected.

## Usage

- Clone the repo: `git clone https://github.com/pmsoltani/rankr.git`
- Switch to the repo directory: `cd rankr`
- Make sure Docker is running.
- Create a `.env` file in the root directory (More info [here](#the-env-file)).
- Create a data directory: `mkdir backend/data`
- Download the GRID database (from the link above) and extract it inside the new `data` directory.
- Start the application: `docker-compose up -d`
- Crawl the ranking tables: `docker-compose exec backend rankr crawl rankings`
- Initialize the database for the first time: `docker-compose exec backend rankr db reset --confirm`
- And you're done! Visit the following URL in your browser: [http://0.0.0.0:8000](http://0.0.0.0:8000)

### Important notice

Please note that the project is still in a pre-alpha stage and it's not ready for production. As of now, the instructions above will fail because of a small bug in the GRID database (release 2020-06-29): The line `62833` of the file `addresses.csv` inside the `grid/full_tables` directory has an additional space character at the end of the country name: "Bonaire, Saint Eustatius and Saba ". Hopefully, this will be corrected in the database's next release. Until then the file must be manually corrected. (See the [TODO](#todo) section).

## The `.env` file

For obvious security reasons, the project's environment variables file (the `.env` file) is not included in the repo, but here is a short, working version of it:

```env
COMPOSE_PROJECT_NAME=rankr
INSTALL_PATH=/home/rankr
APP_ENV=development
POETRY_VERSION=1.0.10

APP_NAME=rankr
APP_HOST=0.0.0.0
APP_PORT=8000

USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36

DIALECT=postgresql

POSTGRESQL_DRIVER=psycopg2
# database host is the docker compose service name
POSTGRESQL_HOST=postgres
POSTGRESQL_PORT=5432
POSTGRESQL_NAME=rankr
POSTGRESQL_USER=rankr
POSTGRESQL_PASS=postgres_super_secret_password

ADMINER_HOST=0.0.0.0
ADMINER_PORT=5050
ADMINER_DRIVER=pgsql
ADMINER_SERVER=postgres
ADMINER_DB=rankr
ADMINER_USERNAME=rankr
ADMINER_PASSWORD=postgres_super_secret_password
```

## Docker containers

The stack currently has three containers:

1. `postgres`, used to store the data in a persistant manner.
2. `adminer` (optional), serves as a GUI for managing the database. Can be removed by commenting out/deleteing the `adminer` section of the `docker-compose.yml` file.
3. `backend`, hosts the API server.

## TODO

- [x] Create a web server and an API.
- [ ] Design and develop a dashboard.
- [x] Finish the documentation.
- [x] Make `countries.csv` a public file.
- [ ] Report the country name problem of the `addresses.csv` file to the GRID database maintainers.
- [x] Update the `config.py` module to reflect the recent changes (i.e., the new rankr CLI).
- [x] Add more functionalities to the CLI (e.g., starting the webserver and running the tests).
- [x] Dockerize the app.

## Contributions

All contributions (suggestions, PRs, ...) are welcome.
