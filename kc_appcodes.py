from neoapi import http_error_codes


BAD_FACEBOOK_TOKEN = '4008', 'the facebook token provided was invalid or expired', http_error_codes.BAD_REQUEST
WRONG_USER = '4031', 'you can only perform this action on yourself', http_error_codes.FORBIDDEN
