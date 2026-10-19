from solution import make_job


def test_default_retries():
    job = make_job("backup")
    assert (job.name, job.retries) == ("backup", 3)
