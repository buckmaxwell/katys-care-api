from neoapi import SerializableStructuredNode, SerializableStructuredRel, ZeroOrMore
from neoapi import StringProperty, AliasProperty, ZeroOrOne, DoesNotExist, application_codes
from neomodel import RelationshipTo, RelationshipFrom
import hashlib
import accesstoken
from uuid import uuid4
from constants import UserRoles
import treatment_plan
import farm
from neoapi import FunctionProperty


class UserV1(SerializableStructuredNode):
    """This is the User entity"""

    __type__ = 'users'

    # INFO
    version = '1.0.0'
    secret = ['password']
    hashed = ['password']

    # ATTRIBUTES
    type = StringProperty(default='users')
    id = StringProperty(unique_index=True, required=True)
    email = AliasProperty(to='id')
    role = StringProperty(default=UserRoles.USER)
    password = StringProperty()
    #farm_ids = FunctionProperty(default='[x.id for x in self.works_for.all()]')


    # RELATIONSHIPS
    token = RelationshipTo(
        'accesstoken.AccessTokenV1', 'HAS_TOKEN', cardinality=ZeroOrOne, model=SerializableStructuredRel
    )
    treatment_plans = RelationshipFrom(
        'treatment_plan.TreatmentPlanV1', 'HAS_VET', cardinality=ZeroOrMore, model=SerializableStructuredRel
    )
    vet_for = RelationshipFrom(
        'farm.FarmV1', 'HAS_VETS', cardinality=ZeroOrMore, model=SerializableStructuredRel
    )
    works_for = RelationshipTo(
        'farm.FarmV1', 'HAS_STAFF', cardinality=ZeroOrMore, model=SerializableStructuredRel
    )


def token_representation(user_id):
    """returns a json object that represents a token to be created"""
    new_token_string = str(uuid4())
    new_token = dict(
        data=dict(
            type='access_tokens',
            id=str(uuid4()),
            attributes=dict(
                id=new_token_string
            ),
            relationships=dict(
                user=dict(
                    data=dict(
                        type='users',
                        id=user_id
                    )
                )
            )
        )
    )
    return new_token


def login(request_form, request_args):
    try:
        email = request_form['email'].lower()
        password = request_form['password']
        password = hashlib.sha256(password).hexdigest()
        u = UserV1.nodes.get(email=email, password=password)  # get user from id and password
        new_token = token_representation(u.id)

        if u.token:
            accesstoken.AccessTokenV1.update_resource(new_token, u.token.single().id)
            r = accesstoken.AccessTokenV1.get_resource(request_args, u.token.single().id)
        else:
            r = accesstoken.AccessTokenV1.create_resource(new_token)  # create the new token then connect it

    except DoesNotExist:
        r = application_codes.error_response([application_codes.RESOURCE_NOT_FOUND])
    except KeyError:
        r = application_codes.error_response([application_codes.BAD_FORMAT_VIOLATION])
    return r
