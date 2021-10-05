class Error(Exception):
    """Base class for other exceptions"""
    pass

class ArgumentsError(Error):
    """ Raise when not having folder argument """
    pass

class CreatingCopyError(Error):
    """ Raise when not having copy_id """
    pass
