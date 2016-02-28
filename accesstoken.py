from neomodel import (StringProperty, AliasProperty, RelationshipFrom, ZeroOrOne)
from neoapi import SerializableStructuredNode, SerializableStructuredRel
import user


class AccessTokenV1(SerializableStructuredNode):
    """
    The access token for a user
    """

    __type__ = 'access_tokens'  # => __type__ must be specified and the same as the default for type

    # INFO
    version = '1.0.0'  # => A version is not required but is a good idea

    # ATTRIBUTES -- NOTE: 'type' and 'id' are required for json api specification compliance
    type = StringProperty(default='access_tokens')  # => required, unique name for model
    id = StringProperty(unique_index=True, required=True)  # => required
    token = AliasProperty(to='id')

    # RELATIONSHIPS
    user = RelationshipFrom('user.UserV1', 'HAS_TOKEN', cardinality=ZeroOrOne, model=SerializableStructuredRel)
