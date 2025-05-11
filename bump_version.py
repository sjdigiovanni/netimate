import toml
import semver
import sys

PYPROJECT_PATH = "pyproject.toml"
VERSION_FILE = "VERSION"

ALLOWED_BUMPS = {"major", "minor", "patch"}


def read_version():
    pyproject = toml.load(PYPROJECT_PATH)
    return pyproject["project"]["version"]


def write_version(new_version):
    pyproject = toml.load(PYPROJECT_PATH)
    pyproject["project"]["version"] = new_version
    with open(PYPROJECT_PATH, "w") as f:
        toml.dump(pyproject, f)
    with open(VERSION_FILE, "w") as f:
        f.write(new_version)


def bump_version(bump_type):
    current = read_version()
    parsed = semver.VersionInfo.parse(current)

    if bump_type == "major":
        new = parsed.bump_major()
    elif bump_type == "minor":
        new = parsed.bump_minor()
    elif bump_type == "patch":
        new = parsed.bump_patch()
    else:
        raise ValueError(f"Unsupported bump type: {bump_type}")

    write_version(str(new))
    print(str(new))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ALLOWED_BUMPS:
        print(f"Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)

    bump_version(sys.argv[1])
