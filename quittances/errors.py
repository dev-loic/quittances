class Error(Exception):
    """Base class for other exceptions"""
    pass

class CreatingCopyError(Error):
    """ Raise when not having copy_id """
    pass
