from datetime import timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile


from server import config
from server.auth_backends import hasher


def test_create_config():
    with NamedTemporaryFile("r+", suffix=".toml") as tmpfile:
        tmpfile.file.close()
        p = Path(tmpfile.name)
        config.create("TEST USERNAME", "TEST PASSWORD", "TEST JWT SECRET", p)
        c = config.read(p)
        assert c.admin.username == "TEST USERNAME"
        assert hasher().check("TEST PASSWORD", c.admin.password_hash)
        assert c.jwt.secret == "TEST JWT SECRET"
        assert c.jwt.ttl == timedelta(days=30)
        assert c.locations.static == Path("dist")


def test_read_config_with_rebuild():
    toml = """
[admin]
username = "TEST USERNAME"
password_hash = "TEST PASSWORD HASH"

[jwt]
secret = "TEST JWT SECRET"

[locations]
static = "dist"
database = "aidan.software.sqlite3"

[rebuild]
secret = "TEST REBUILD SECRET"
"""
    with NamedTemporaryFile("r+", suffix=".toml") as tmpfile:
        tmpfile.file.write(toml)
        tmpfile.file.close()
        c = config.read(Path(tmpfile.name))
        assert c.admin.username == "TEST USERNAME"
        assert c.admin.password_hash == "TEST PASSWORD HASH"
        assert c.jwt.secret == "TEST JWT SECRET"
        assert c.jwt.ttl == timedelta(days=30)
        assert c.locations.static == Path("dist")
        assert c.rebuild.secret == "TEST REBUILD SECRET"
        assert c.rebuild.branch is None
