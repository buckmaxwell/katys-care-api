__author__ = 'max'

FB_GRAPH_ME = 'https://graph.facebook.com/v2.4/me?access_token={accesstoken}&fields=email,first_name,last_name,gender,\
birthday,location'


class UserRoles(object):
    SYS_ADMIN = 'sysadmin'
    USER = 'user'
    VETERINARIAN = 'veterinarian'


class SignUpMethods(object):
    NATIVE_SIGNUP = 'NATIVE'
    FACEBOOK_SIGNUP = 'FACEBOOK'
    TWITTER_SIGNUP = 'TWITTER'


class AuthenticationLevels(object):
    ANY = 'ANY'
    USER = 'USER'
    ADMIN = 'ADMIN'


class ArtistRoles(object):
    HEADLINER = 'HEADLINER'
    OPENER = 'OPENER'
    ANY = 'ANY'
