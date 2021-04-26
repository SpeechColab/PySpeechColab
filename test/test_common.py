def test_always_pass():
    assert True


def test_imports():
    import speechcolab
    assert speechcolab

    from speechcolab import datasets
    assert datasets

    from speechcolab.datasets import gigaspeech
    assert gigaspeech
