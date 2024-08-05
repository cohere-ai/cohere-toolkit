import json
from collections import defaultdict
from typing import Dict

from backend.tools.google_drive.constants import GoogleDriveActions
from backend.tools.google_drive.sync.utils import extract_file_ids_from_target


def consolidate(activities: Dict[str, str]):
    """
    Notes

    - GDrive actions come in chronological order
    - Purposefully have Create and Edit actions check if a file exists, helps with
    move + create/edit combos. Without it there is no great way to async execute them.
    - Create action also pulls latest permissions and name, thus making create a superset of permissions_change and rename
    - Edit action also pulls latest permissions and name, thus making edit a superset of permissions_change and rename
    """
    file_id_actions = defaultdict(list)
    for activity in activities:
        file_ids = extract_file_ids_from_target(activity=activity)
        for file_id in file_ids:
            file_id_actions[file_id].append(activity)

    consolidated_file_id_actions = defaultdict(list)
    for file_id, activities in file_id_actions.items():
        actions = [list(x["primaryActionDetail"].keys())[0] for x in activities]
        # NOTE Debugs below help with understanding the consolidation logic
        print(file_id)
        print("Before")
        print(actions)

        if GoogleDriveActions.MOVE.value in actions:
            found_index = actions.index(GoogleDriveActions.MOVE.value)
            consolidated_file_id_actions[file_id].append(activities[found_index])

        for action in actions:
            consolidated_file_id_actions[file_id].append(activities[0])
            if action in [
                GoogleDriveActions.DELETE.value,
                GoogleDriveActions.RESTORE.value,
                GoogleDriveActions.CREATE.value,
                GoogleDriveActions.EDIT.value,
            ]:
                break

        # NOTE Debugs below help with understanding the consolidation logic
        after_actions = [
            list(x["primaryActionDetail"].keys())[0]
            for x in consolidated_file_id_actions[file_id]
        ]
        print("After")
        print(after_actions)
        print("\n")

    # print(json.dumps(consolidated_file_id_actions, indent=2))


if __name__ == "__main__":
    # Opening JSON file
    f = open("/Users/giannis/Desktop/test.json")

    # returns JSON object as
    # a dictionary
    activities = json.load(f)
    consolidate(activities=activities)
