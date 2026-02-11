from typing import Annotated
from pydantic import BaseModel, Field, AfterValidator, ValidationError
from datetime import date
import json
import os


def validate_user_birth(birth):
    lowerBound = date(1920, 1, 1)
    upperBound = date.today()
    if lowerBound <= birth <= upperBound:
        return birth

    raise ValueError("Invalid birth date")


class UserProfile(BaseModel):

    name: str = Field(min_length=2, max_length=30)

    birth: Annotated[date, AfterValidator(validate_user_birth)]


users = [
    {"name": "super", "birth": "2002-04-07"},
    {"name": "marc", "birth": "1900-04-07"},
    {"name": "John", "birth": "3900-04-07"},
    {"name": "Doe", "birth": "2000-04-07"},
    {"name": "Baraa", "birth": "2003-04-07"},
    {"name": "su", "birth": "1900-04-07"},
    {"birth": "1900-04-07"},
    {"name": "super", "birth": "daawdaw"},
    {"nam": "super", "bih": "1900-04-07"},
]

validUsers = []

if not os.path.isdir("output"):
    os.mkdir("output")

errorsLog = open("output/errors.log", "w+")

for index, user in enumerate(users):
    try:
        validUser = UserProfile.model_validate(user)
        validUsers.append(validUser.model_dump(mode="json"))
    except ValidationError as e:
        for err in e.errors():
            loc = ">".join([str(loc) for loc in err["loc"]])
            msg = err["msg"]
            errorsLog.write(f'Index: {index}: [{loc}]  ":"  {msg}')
        errorsLog.write("\n")


with open("output/valid_users.json", "w+") as validUsersFile:
    json.dump(validUsers, validUsersFile, indent=2)
