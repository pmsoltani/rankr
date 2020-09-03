# rankr

**rankr** is a platform for aggregating the results of different academic rankings.

## What does it do!

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
- Create a virtual environment: `python -m venv .venv`
- Activate the virtual environment:

  - bash/zsh: `source .venv/bin/activate`
  - cmd.exe: `.venv\Scripts\activate.bat`

- Install poetry: `pip install poetry`
- Install the dependencies: `poetry install`

This will also install the new **rankr CLI**.

- Create a `.env` file in the root directory (More info [here](#the-env-file)).
- Create a data directory: `mkdir data`
- Download the GRID database (from the link above) and extract it inside the `data` directory.
- Crawl the ranking websites: `rankr crawl qs the shanghai`
- Initialize the database: `rankr db reset --confirm`
- Fire up the webserver: `python main.py`

### Important notice

Please note that the project is still in a pre-alpha stage and it's not ready for production. As of now, the instructions above will fail because of a small bug in the GRID database (release 2020-06-29): The line `62833` of the file `addresses.csv` inside the `grid/full_tables` directory has an additional space character at the end of the country name: "Bonaire, Saint Eustatius and Saba ". Hopefully, this will be corrected in the database's next release. Until then the file must be manually corrected. (See the [TODO](#todo) section).

## The `.env` file

For obvious security reasons, the project's environment variables file (the `.env` file) is not included in the repo, but here is a short, working version of it:

```env
APP_NAME=rankr
APP_HOST=0.0.0.0
APP_PORT=8000

USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36

DIALECT=mysql

MYSQL_DRIVER=mysqlconnector
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_NAME=rankr
MYSQL_USER=root
MYSQL_PASS=your_mysql_root_password
```

## TODO

- [x] Create a web server and an API.
- [ ] Design and develop a dashboard.
- [x] Finish the documentation.
- [x] Make `countries.csv` a public file.
- [ ] Report the country name problem of the `addresses.csv` file to the GRID database maintainers.
- [x] Update the `config.py` module to reflect the recent changes (i.e., the new rankr CLI).
- [ ] Add more functionalities to the CLI (e.g., starting the webserver and running the tests).

## Contributions

All contributions (suggestions, PRs, ...) are welcome.
