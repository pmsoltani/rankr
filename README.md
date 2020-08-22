# rankr

**rankr** is a platform for aggregating the results of different academic rankings.

## What does it do?

rankr crawls university ranking tables and stores the results in `.csv` files, after some pre-processing. At the moment, it supports [QS](https://www.topuniversities.com/), [Shanghai (ARWU)](http://www.shanghairanking.com), and [Times Higher Education (THE)](https://www.timeshighereducation.com) for both their **world university rankings** and **subject rankings**.

To match academic institutions across ranking systems (to aggregate their results), it is necessary to have an identification system that assigns unique IDs to institutions. After some research, [GRID ID](https://grid.ac) system was chosen, which provides a free database of about 100,000 research institutions; for example, the GRID ID for Sharif University of Technology is `grid.412553.4`.

rankr first stores the entire GRID ID data ([release 2020-06-29](https://digitalscience.figshare.com/articles/GRID_release_2020-06-29/12587828)) in a database (using [SQLAlchemy](https://www.sqlalchemy.org)) and then iterates through each crawled ranking table and tries to match institutions with their respective GRID counterparts.

To achieve this, several methods are employed using:

- Institution profile URL in each ranking table
- Institution name & country
- Fuzzy matching of institutions
- Manual matching

It should be noted that the metadata from the GRID database is preferred in case of any discrepancy. For example, if a ranking website lists an institution under `Country A`, but the GRID database records it under `Country B`, the latter will be selected.

## TODO

- [ ] Create a web server and an API.
- [ ] Design and develop a dashboard.
- [ ] Finish the documentation.
