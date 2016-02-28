import random
import string
import accesstoken


def id_generator(size=5, chars=string.ascii_lowercase + string.digits):
    """
    Generate an string to use as an id

    Note: While unlikely, it is possible that this method could return a duplicate
    the likelihood decreases as the size of the id increases
    """
    return ''.join(random.choice(chars) for _ in range(size))


def user_from_token(token):
    token = accesstoken.AccessTokenV1.nodes.get(id=token)
    return token.user.single().id

