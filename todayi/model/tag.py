import uuid


class InvalidTagError(Exception):
    """
    Error for attempting to provide invalid tags
    """

    pass


class Tag:
    """
    Represents a tag, which can optionally describe a
    `todayi.model.entry.Entry` object.

    :param name: name of the tag
    :type name: str
    :param uuid: unique id for tag
    :type uuid: str
    """

    def __init__(self, name: str, uuid: str = str(uuid.uuid4())):
        contains_space = any([c.isspace() for c in name])
        if contains_space:
            raise InvalidTagError("Tags are not allowed to contain whitespace")
        self.name = name.lower()
        self.uuid = uuid
