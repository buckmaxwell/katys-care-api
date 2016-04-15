from neoapi import SerializableStructuredNode, SerializableStructuredRel, FunctionProperty
from neoapi import StringProperty, ZeroOrOne, BooleanProperty, DateTimeProperty, ZeroOrMore, AliasProperty
from neomodel import RelationshipTo, RelationshipFrom
from katysutils import id_generator


class FarmV1(SerializableStructuredNode):
    """This is the Farm entity"""

    __type__ = 'farms'

    # INFO
    version = '1.0.0'

    # ATTRIBUTES
    type = StringProperty(default='farms')
    id = StringProperty(default=id_generator, unique_index=True)
    name = StringProperty(required=True)
    #default_treatment_plan = FunctionProperty(default="[x for x in self.veternarian.single()]")

    # RELATIONSHIPS
    calves = RelationshipFrom('calf.CalfV1', 'HAS_FARM', cardinality=ZeroOrMore, model=SerializableStructuredRel)

    veterinarian = RelationshipTo(
        'user.UserV1', 'HAS_VETS', cardinality=ZeroOrOne, model=SerializableStructuredRel
    )
    staff = RelationshipFrom(
        'user.UserV1', 'HAS_STAFF', cardinality=ZeroOrMore, model=SerializableStructuredRel
    )
