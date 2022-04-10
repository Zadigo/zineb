def setup():
    """Initial entrypoint that allows the configuration
    of for a Zineb project by populating the application
    with the spiders, models and other required items
    for a project to run"""
    from zineb.registry import registry
    
    registry.populate()
