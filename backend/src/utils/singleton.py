class Singleton(type):
    """
    A singleton class has only one instance, while providing a global access point to this instance.
    https://refactoring.guru/fr/design-patterns/singleton
    A copy of teacher's code.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
