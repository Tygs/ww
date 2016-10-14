def test_import():
    import ww  # noqa

    from ww import g

    g('test')
