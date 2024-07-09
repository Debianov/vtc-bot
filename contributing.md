# How to contribute
Start by searching in the TODO and Backlog columns from the [project board](). It is imperative that 
you work in your own fork.
When you are done, create new pull request. Keep in the mind that you should mention all the issues that were fixed.
Keep the `Discussion` tab free for any newbie topics.
# Dev dependencies
```sh
poetry install --with dev,docs
```
# Docs generation
If you want a web version of the docs:
```sh
cd docs
make html
```
# Start autotests
Create a secret file with the db name and username:
```sh
POSTGRES_TEST_DBNAME=...
POSTGRES_USER=...
```
And export it:
```sh
export file
```
Then:
```sh
poetry run pytest
```