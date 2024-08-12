import glob


def main():
    files = glob.glob("src/backend/alembic/versions/*.py")

    if len(files) != len(set(files)):
        raise Exception("Duplicate file name found")

    print("All revision IDs are unique")


if __name__ == "__main__":
    main()
