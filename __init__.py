def setup():
    """Initial entrypoint that allows the configuration
    of a Zineb project by populating the application
    with the spiders, models and other items"""
    from zineb.registry import registry
    
    registry.populate()
