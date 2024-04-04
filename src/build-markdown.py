import json
import os
import uuid

FILENAME = os.environ.get("CHANGES_JSON_FILE", "")

status_table = {"CREATE_COMPLETE": ":green_circle:"}

action_table = {
    "Add": ":sparkle:",  # ❇️
    "Modify": ":twisted_rightwards_arrows:",  # 🔀
    "Remove": ":x:",  # ❌
    "Dynamic": ":grey_question:",  # ❔
}

CHANGE_LINE_TEMPLATE = "{action} | `{id}` | {type} | {replacement} | {details}\n"


def get_details(details):
    out = []
    for d in details:
        if d["Target"]["Attribute"] != "Properties":
            continue
        out.append(f"<li>{d['Target']['Name']}</li> <!-- markdownlint-disable-line MD033 -->")
    return f"<ul>{''.join(out)}</ul>"


def get_replace(resource_change):
    if resource_change["Action"] != "Modify":
        return "NA"
    replace = resource_change.get("Replacement", "Unknown")
    if replace == "True":
        return f":recycle:{replace}"
    return replace


def get_action(action):
    return f"{action_table[action]} {action}"


def main():
    try:
        with open(FILENAME, "r") as f:
            changeset = json.load(f)
    except FileNotFoundError:
        changeset = json.loads(os.environ["RAW_CHANGES"])
    # Output main header
    out = f"# Changeset for {changeset['StackName']}\n\n"

    # Output status header
    out += f"## Status: {status_table[changeset['Status']]} `{changeset['Status']}`\n\n"

    if not changeset["Changes"]:
        out += "No changes\n"
        return out

    # Output table header and dashes.
    out += "Action | ID | Resource Type | Replacement | Changed Properties\n"
    out += "------ | -- | ------------- | ----------- | ------------------\n"

    # Output each change
    for x in changeset["Changes"]:
        out += CHANGE_LINE_TEMPLATE.format(
            action=get_action(x["ResourceChange"]["Action"]),
            id=x["ResourceChange"]["LogicalResourceId"],
            type=x["ResourceChange"]["ResourceType"],
            replacement=get_replace(x["ResourceChange"]),
            details=get_details(x["ResourceChange"]["Details"]),
        )

    # Put the ChangeSetID in the output as a comment
    out += f"\n<!-- ChangesetID: {changeset['ChangeSetId']} -->\n"

    # Docs: https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#multiline-strings
    # Example from here: https://github.com/orgs/community/discussions/28146#discussioncomment-5638023
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        delimiter = uuid.uuid1()
        f.write(f"comment<<{delimiter}\n")
        f.write(out)
        f.write("\n")
        f.write(str(delimiter))

    return out


if __name__ == "__main__":
    comment = main()
    print(comment)
