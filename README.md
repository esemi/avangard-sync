[Avangard bank](https://www.avangard.ru/rus/) and [moy sklad](https://www.moysklad.ru/) sync tool
---
todo badges

todo description

### Pre-requirements
- [redis server up and running](https://redis.io/docs/getting-started/installation/)
- [python 3.10+](https://www.python.org/downloads/)

### Local setup
```shell
$ git clone git@github.com:esemi/avangard-sync.git
$ cd avangard-sync
$ python3.10 -m venv venv
$ source venv/bin/activate
$ pip install -U poetry pip setuptools
$ poetry config virtualenvs.create false --local
$ poetry install
```

Create env file to override default config
```bash
cat > .env << EOF
throttling_time=30.0
debug=true
EOF
```

### Run tests
```shell
$ pytest --cov=app
```

### Run linters
```
$ poetry run mypy app/
$ poetry run flake8 app/
```

### Run background task
```
python -m app.sync_tool
```


### Links
todo description
