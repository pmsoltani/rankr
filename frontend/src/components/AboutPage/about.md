# rankr

`rankr` is a free and open-source platform for aggregating the results of different academic rankings.

## What does it do?

`rankr` crawls university ranking tables and stores the results in ".csv" files, after some pre-processing. At the moment, it supports [QS](https://www.topuniversities.com/), [Shanghai (ARWU)](http://www.shanghairanking.com), and [Times Higher Education (THE)](https://www.timeshighereducation.com) for both their **world university rankings** and **subject rankings**.

To match academic institutions across ranking systems (and be able to aggregate their results), it is necessary to have an identification system that assigns unique IDs to institutions. After some research, the [GRID ID](https://grid.ac) system was chosen, which provides a free database of about 100,000 research institutions; for example, the GRID ID for Sharif University of Technology is [grid.412553.4](https://www.grid.ac/institutes/grid.412553.4).

`rankr` first stores the entire GRID ID data in a database and then iterates through each crawled ranking table and tries to match institutions with their respective GRID counterparts.

To achieve this, several methods are employed using:

- Institution profile URL in each ranking table
- Institution name & country
- Fuzzy matching of institutions
- Manual matching

It should be noted that the metadata from the GRID database is preferred in case of any discrepancy. For example, if a ranking website lists an institution under _Country A_, but the GRID database records it under _Country B_, the latter will be selected.

## Technologies

`rankr` is developed using these open-source packages:

- Backend: the server was written in python

  - 🕷 [Requests](https://github.com/psf/requests) & [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): crawling and parsing ranking tables
  - 🗄 [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/) & [Alembic](https://github.com/sqlalchemy/alembic): managing database operations
  - ⚡ [FastAPI](https://github.com/tiangolo/fastapi): developing the API
  - 🧠 [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy): fuzzy matching of institution names
  - ✅ [pydantic](https://github.com/samuelcolvin/pydantic): data validation and manipulation

- Frontend:

  - ⚛️ [React](https://github.com/facebook/react): the frontend library used to develop this website
  - 💅 [Elastic UI](https://github.com/elastic/eui): a collection of React UI components
  - ⚛️ [Redux](https://github.com/reduxjs/redux): managing state
  - 📈 [ApexCharts](https://github.com/apexcharts/apexcharts.js): the beautiful charts you see here
  - 🔃 [axios](https://github.com/axios/axios): sending requests to the API
  - 📙 [Wikipedia](https://github.com/dopecodez/wikipedia): getting wikipedia summaries for institutions
  - 🖼 icons: provided by [FlatIcon](https://www.flaticon.com), [Tabler icons](https://tablericons.com), and [IconPark](https://iconpark.oceanengine.com/official)

- Database: 🐘 [PostgreSQL](https://www.postgresql.org)

- Container management: 🐳 [Docker](https://www.docker.com)

## Contributions

`rankr` lives on [GitHub](https://github.com/pmsoltani/rankr). All suggestions/contributions are welcome.
