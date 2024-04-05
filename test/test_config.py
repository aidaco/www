from datetime import timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile


from server import config, auth_base


def test_create_config():
    with NamedTemporaryFile("r+", suffix=".toml") as tmpfile:
        tmpfile.file.close()
        p = Path(tmpfile.name)
        p.write_text(
            config.dumps_toml(
                config.create("TEST USERNAME", "TEST PASSWORD", "TEST JWT SECRET")
            )
        )
        c = config.read(p)
        assert c.admin.username == "TEST USERNAME"
        assert auth_base.check_password("TEST PASSWORD", c.admin.password_hash) is None
        assert c.jwt.secret == "TEST JWT SECRET"
        assert isinstance(c.jwt.access_ttl, timedelta)


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
        assert c.rebuild
        assert c.rebuild.secret == "TEST REBUILD SECRET"
        assert c.rebuild.branch is None
