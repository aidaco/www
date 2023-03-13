import sys

import argon2


def main():
    cmd = sys.argv[1]
    ph = argon2.PasswordHasher()
    if cmd == "hash":
        print(ph.hash(sys.argv[2]))
    elif cmd == "check":
        try:
            ph.verify(sys.argv[2], sys.argv[3])
            print("Success")
        except argon2.exceptions.VerificationError:
            print("Failed")


if __name__ == "__main__":
    main()
