import pytest
from sfm.database import generate_db_string


def test_generate_db_string():
    """Test the generate_db_string function in config.py."""

    env = "test"
    dbhost = "unset"
    dbname = "unset"
    dbuser = "unset"
    dbpass = "unset"

    # test env
    assert generate_db_string(env, dbhost, dbname, dbuser, dbpass) == "sqlite://"

    # local env
    env = "local"
    assert (
        generate_db_string(env, dbhost, dbname, dbuser, dbpass)
        == "sqlite:///./issues.db"
    )

    # dev without db params
    env = "development"
    with pytest.raises(ValueError):
        conn_str = generate_db_string(env, dbhost, dbname, dbuser, dbpass)
        print("Connection String: {}".format(conn_str))

    # dev with db params
    env = "development"
    dbhost = "one"
    dbname = "two"
    dbuser = "three"
    dbpass = "four"
    assert (
        generate_db_string(env, dbhost, dbname, dbuser, dbpass)
        == "postgresql+psycopg2://three:four@one/two"
    )

    # prod with db params
    env = "production"
    assert (
        generate_db_string(env, dbhost, dbname, dbuser, dbpass)
        == "postgresql+psycopg2://three:four@one/two"
    )
