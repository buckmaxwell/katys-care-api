from neoapi import SerializableStructuredNode, SerializableStructuredRel
from neoapi import StringProperty, ZeroOrOne, ZeroOrMore
from neomodel import JSONProperty
from neomodel import RelationshipTo, RelationshipFrom
from katysutils import id_generator


class TreatmentPlanV1(SerializableStructuredNode):
    """This is the Treatment Plan entity"""

    __type__ = 'treatment_plans'

    # INFO
    version = '1.0.0'

    # ATTRIBUTES
    type = StringProperty(default='treatment_plans')
    id = StringProperty(default=id_generator, unique_index=True)
    title = StringProperty()
    body = JSONProperty()

    # RELATIONSHIPS
    veterinarian = RelationshipTo(
        'user.UserV1', 'HAS_VET', cardinality=ZeroOrOne, model=SerializableStructuredRel
    )
    calves = RelationshipFrom(
        'calf.CalfV1', 'HAS_TREATMENT_PLAN', cardinality=ZeroOrMore, model=SerializableStructuredRel
    )
