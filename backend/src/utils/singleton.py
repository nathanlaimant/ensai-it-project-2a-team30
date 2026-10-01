class Singleton(type):
    """Métaclasse garantissant qu'une classe n'a qu'une seule instance,
    tout en fournissant un point d'accès global à cette instance.

    Voir : https://refactoring.guru/fr/design-patterns/singleton
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Retourne l'instance unique de la classe, en la créant si nécessaire.

        Parameters
        ----------
        *args
            Arguments positionnels transmis au constructeur de la classe,
            utilisés uniquement lors de la première instanciation.
        **kwargs
            Arguments nommés transmis au constructeur de la classe,
            utilisés uniquement lors de la première instanciation.

        Returns
        -------
        object
            L'instance unique de la classe.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
