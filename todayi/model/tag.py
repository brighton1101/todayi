import uuid


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
        self.name = name.lower()
        self.uuid = uuid
