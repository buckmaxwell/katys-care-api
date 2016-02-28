## Create a user

```http
POST http://localhost:10200/v1/users
```
## Login

```http
POST http://localhost:10200/v1/token?include=user
```

## Retrieve Individual User

```http
GET http://localhost:10200/v1/users/{id}
```

## Retrieve Group of Users

```http
GET http://localhost:10200/v1/users
```

## Deactivate a User

```http
DELETE http://localhost:10200/v1/users/{id}
```

## Update a User

```http
PATCH http://localhost:10200/v1/users/{id}
```

