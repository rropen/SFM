import pytest
from sfm.config import generate_db_string


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
        == "mssql+pyodbc:///?autocommit=true&odbc_connect=Driver%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BServer%3Dtcp%3Aone%2C1433%3BDatabase%3Dtwo%3B%0A++++++++Uid%3Dthree%3BPwd%3Dfour%3BEncrypt%3Dyes%3BTrustServerCertificate%3Dno%3BConnection+Timeout%3D30%3B"
    )

    # prod with db params
    env = "production"
    assert (
        generate_db_string(env, dbhost, dbname, dbuser, dbpass)
        == "mssql+pyodbc:///?autocommit=true&odbc_connect=Driver%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BServer%3Dtcp%3Aone%2C1433%3BDatabase%3Dtwo%3B%0A++++++++Uid%3Dthree%3BPwd%3Dfour%3BEncrypt%3Dyes%3BTrustServerCertificate%3Dno%3BConnection+Timeout%3D30%3B"
    )
