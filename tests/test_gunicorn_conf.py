from kookaburra import gunicorn_conf


def test_gunicorn_config() -> None:
    assert gunicorn_conf.worker_class == "uvicorn.workers.UvicornWorker"
    assert gunicorn_conf.workers == 5
    assert gunicorn_conf.threads == 1
    assert gunicorn_conf.timeout == 60
    assert gunicorn_conf.port == 8000
    assert gunicorn_conf.bind == ":8000"
