# from zineb.registry import registry_completed


def setup():
    """Initial entrypoint that allows the configuration
    of a Zineb project by populating the application
    with the spiders, models and other items"""
    from zineb.registry import registry

    registry.populate()


# def test_function(**kwargs):
#     print(kwargs)
#     return True


# registry_completed.connect(test_function)
