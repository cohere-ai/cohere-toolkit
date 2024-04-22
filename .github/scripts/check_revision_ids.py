import glob


def main():
    files = glob.glob("src/backend/alembic/versions/*.py")
    revision_ids = [file.split("_")[0] for file in files]

    if len(revision_ids) != len(set(revision_ids)):
        raise Exception("Duplicate revision ID found")

    print("All revision IDs are unique")


if __name__ == "__main__":
    main()
