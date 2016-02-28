from neoapi import SerializableStructuredNode, SerializableStructuredRel
from neoapi import StringProperty,ZeroOrOne, BooleanProperty, DateTimeProperty
from neomodel import RelationshipTo


class CalfV1(SerializableStructuredNode):
    """This is the Calf entity"""

    __type__ = 'calves'

    # INFO
    version = '1.0.0'

    # ATTRIBUTES
    type = StringProperty(default='calves')
    id = StringProperty(unique_index=True, required=True)
    cid = StringProperty(required=True)
    name = StringProperty()
    treatment_plan_position = StringProperty()
    waiting = BooleanProperty(default=False)
    wait_expires = DateTimeProperty()

    # RELATIONSHIPS
    farm = RelationshipTo('farm.FarmV1', 'HAS_FARM', cardinality=ZeroOrOne, model=SerializableStructuredRel)
    treatment_plan = RelationshipTo(
        'treatment_plan.TreatmentPlanV1', 'HAS_TREATMENT_PLAN', cardinality=ZeroOrOne, model=SerializableStructuredRel
    )
