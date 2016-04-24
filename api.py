__author__ = 'Max Buck'
__email__ = 'maxbuckdeveloper@gmail.com'
__version__ = '1.0.0'


import os
from flask import Flask, request
from neoapi import application_codes
import user as user_module
from neomodel import DoesNotExist
from constants import UserRoles, AuthenticationLevels
import json
import kc_appcodes
import accesstoken
import katyscareerror
from user import UserV1 as User
from farm import FarmV1 as Farm
from calf import CalfV1 as Calf
from treatment_plan import TreatmentPlanV1 as TreatmentPlan
from katysutils import user_from_token

# Please set Debug Mode to False for production
debug_mode = False


app = Flask(__name__)
url = os.environ.get("NEO4J_REST_URL")


# API CHECK#############################################################################################################
@app.route('/', methods=['GET'])
@app.route('/v1', methods=['GET'])
def index():
    """ Call this method for basic version info or to ensure the api is running. """
    return 'Your api is up and running!'


# AUTHENTICATION########################################################################################################
def authenticate(level=AuthenticationLevels.ANY, user_id=None):
    def authenticate_decorator(func):
        def func_wrapper(*args, **kwargs):
            if debug_mode:
                response = func(*args, **kwargs)
            else:
                response = None
                with app.app_context():  # change the context in order to allow for use of request
                    try:  # fetch the user by id
                        token = request.headers['Authorization']
                        the_user = accesstoken.AccessTokenV1.nodes.get(id=token).user.single()  # fetch the user by id
                        if level == AuthenticationLevels.ANY:
                            pass
                        if level == AuthenticationLevels.USER and the_user.id != user_id and the_user.role != UserRoles.SYS_ADMIN:
                            raise katyscareerror.WrongUserError()
                        if level == AuthenticationLevels.ADMIN and the_user.role != UserRoles.SYS_ADMIN:
                            raise katyscareerror.Forbidden()
                        response = func(*args, **kwargs)

                    except DoesNotExist:  # return an error message if token is bad
                        response = application_codes.error_response([application_codes.BAD_AUTHENTICATION])
                    except KeyError:  # return an error message if authentication not provided
                        response = application_codes.error_response([application_codes.NO_AUTHENTICATION])
                    except katyscareerror.WrongUserError:
                        response = application_codes.error_response([kc_appcodes.WRONG_USER])
                    except katyscareerror.Forbidden:
                        response = application_codes.error_response([application_codes.FORBIDDEN_VIOLATION])

            return response

        return func_wrapper
    return authenticate_decorator


# LOGIN METHODS#########################################################################################################
@app.route('/v1/token', methods=['POST'])  # this might be a patch method
def get_token():
    request_json = json.loads(request.data)
    try:
        response = user_module.login(request_json, request.args)

    except KeyError:
        response = application_codes.error_response([application_codes.BAD_FORMAT_VIOLATION])

    return response


# USER METHODS##########################################################################################################
@app.route('/v1/users/<id>', methods=['GET', 'PATCH', 'DELETE'])
@app.route('/v1/users', defaults={'id': None}, methods=['POST', 'GET'])
def user_wrapper(id):
    """Methods related to the user resource"""

    response = None
    if id:
        id = id.lower()

    req_data = None
    try:
        if request.data:
            req_data = json.loads(request.data)
            if "email" in req_data["data"]["attributes"]:
                    req_data["data"]["attributes"]["email"] = req_data["data"]["attributes"]["email"].lower()  # emails should be lower case
            if "id" in req_data["data"]["attributes"]:
                req_data["data"]["attributes"]["id"] = req_data["data"]["attributes"]["id"].lower()
    except KeyError:
        return application_codes.error_response([application_codes.BAD_FORMAT_VIOLATION])

    def post_user():
        return User.create_resource(req_data)

    @authenticate(AuthenticationLevels.USER, id)
    def patch_user():
        return User.update_resource(req_data, id)

    @authenticate(AuthenticationLevels.USER, id)
    def delete_user():
        return User.deactivate_resource(id)

    @authenticate(AuthenticationLevels.USER, id)
    def get_user():
        return User.get_resource(request.args, id)

    @authenticate(AuthenticationLevels.ADMIN)
    def get_user_collection():
        return User.get_collection(request.args)

    # pick method to execute
    if request.method == 'POST':  # no auth required
        response = post_user()
    elif request.method == 'PATCH':  # must be user
        response = patch_user()
    elif request.method == 'DELETE':  # must be user
        response = delete_user()
    elif request.method == 'GET' and id:  # must be user
        response = get_user()
    elif request.method == 'GET':  # must be administrator
        response = get_user_collection()
    return response


# FARM METHODS##########################################################################################################
@app.route('/v1/farms', defaults={'farm_id': None},  methods=['GET', 'POST'])
@app.route('/v1/farms/<farm_id>', methods=['GET', 'PATCH'])
def farm_wrapper(farm_id):
    response = None
    farm_id = farm_id.lower() if farm_id else farm_id
    req_data = json.loads(request.data) if request.data else dict()

    @authenticate(AuthenticationLevels.ANY)
    def public_calls():
        if request.method == 'POST':
            return Farm.create_resource(req_data)
        elif request.method == 'GET' and farm_id:
            return Farm.get_resource(request.args, farm_id)
        elif request.method == 'GET':
            return Farm.get_collection(request.args)

    @authenticate(AuthenticationLevels.USER)
    def private_calls():
        if request.method == 'PATCH':
            return Farm.update_resource(req_data, farm_id)
        elif request.method == 'DELETE':
            return Farm.deactivate_resource(farm_id)

    if request.method in ['POST', 'GET']:
        response = public_calls()
    elif request.method in ['PATCH', 'DELETE']:
        response = private_calls()

    return response


# TREATMENT PLAN METHODS################################################################################################
@app.route('/v1/treatment_plans', defaults={'tp_id': None},  methods=['GET', 'POST'])
@app.route('/v1/treatment_plans/<tp_id>', methods=['GET', 'PATCH', 'DELETE'])
def treatment_plan_wrapper(tp_id):
    response = None
    tp_id = tp_id.lower() if tp_id else tp_id
    req_data = json.loads(request.data) if request.data else dict()
    tp_owner_id = None

    try:  # Attempt to find user associated with treatment plan
        if tp_id:
            tp = TreatmentPlan.nodes.get(id=tp_id)
            tp_owner = tp.veterinarian.single()
            if tp_owner:
                tp_owner_id = tp_owner.id
    except DoesNotExist:
        return application_codes.error_response([application_codes.RESOURCE_NOT_FOUND])

    @authenticate(AuthenticationLevels.ANY)
    def public_calls():
        if request.method == 'POST':
            user_id = user_from_token(request.headers['Authorization'])
            if 'relationships' not in req_data['data']:
                req_data['data']['relationships'] = dict()
            req_data['data']['relationships']['veterinarian'] = dict()
            req_data['data']['relationships']['veterinarian']['data'] = {'type': 'users', 'id': user_id}
            return TreatmentPlan.create_resource(req_data)
        elif request.method == 'GET' and tp_id:
            return TreatmentPlan.get_resource(request.args, tp_id)
        elif request.method == 'GET':
            return TreatmentPlan.get_collection(request.args)

    @authenticate(AuthenticationLevels.USER, user_id=tp_owner_id)
    def private_calls():
        if request.method == 'PATCH':
            return TreatmentPlan.update_resource(req_data, tp_id)
        elif request.method == 'DELETE':
            return TreatmentPlan.deactivate_resource(tp_id)

    if request.method in ['POST', 'GET']:
        response = public_calls()
    elif request.method in ['PATCH', 'DELETE']:
        response = private_calls()

    return response


# CALF METHODS##########################################################################################################
@app.route('/v1/calves', defaults={'calf_id': None},  methods=['GET', 'POST'])
@app.route('/v1/calves/<calf_id>', methods=['GET', 'PATCH'])
def calf_wrapper(calf_id):
    """
    NOTE: cid is case sensitive and determined by the user who creates the calf

    The id is made up of the cid and farm id. {farmid}_{cid}
    """
    response = None
    req_data = json.loads(request.data) if request.data else dict()

    try:  # Authorize here (not ideal, but this type of auth not supported by def at top of page)
        if calf_id:
            token = request.headers['Authorization']
            the_user = accesstoken.AccessTokenV1.nodes.get(id=token).user.single()
            calf = Calf.nodes.get(id=calf_id)
            permitted_users = calf.farm.single().staff.all()
            if the_user in permitted_users:
                pass
            else:
                raise katyscareerror.KatysCareError
    except DoesNotExist:
        return application_codes.error_response([application_codes.BAD_AUTHENTICATION])
    except katyscareerror.KatysCareError:
        return application_codes.error_response([application_codes.FORBIDDEN_VIOLATION])
    except KeyError:
        return application_codes.error_response([application_codes.NO_AUTHENTICATION])

    @authenticate(AuthenticationLevels.ANY)
    def public_calls():
        if request.method == 'POST':
            try:
                farm_id = req_data["data"]["relationships"]["farm"]["data"]["id"]
                cid = req_data["data"]["attributes"]["cid"]
                req_data["data"]["attributes"]["id"] = "{fid}_{cid}".format(fid=farm_id, cid=cid)
                return Calf.create_resource(req_data)
            except KeyError:
                return application_codes.error_response([application_codes.BAD_FORMAT_VIOLATION])
        elif request.method == 'GET' and calf_id:
            return Calf.get_resource(request.args, calf_id)
        elif request.method == 'GET':
            return Calf.get_collection(request.args)

    @authenticate(AuthenticationLevels.USER)
    def private_calls():
        if request.method == 'PATCH':
            return Calf.update_resource(req_data, calf_id)
        elif request.method == 'DELETE':
            return Calf.deactivate_resource(calf_id)

    if request.method in ['POST', 'GET']:
        response = public_calls()
    elif request.method in ['PATCH', 'DELETE']:
        response = private_calls()

    return response


# ERROR HANDLERS########################################################################################################
@app.errorhandler(404)
def not_found(error):
    return application_codes.error_response([application_codes.RESOURCE_NOT_FOUND])


@app.errorhandler(405)
def method_not_allowed(error):
    return application_codes.error_response([application_codes.METHOD_NOT_ALLOWED])


# FLASK INFO############################################################################################################
"""if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10200, debug=True)
"""