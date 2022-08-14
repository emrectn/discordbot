
def fix_null_partition(standup):
    for key in standup:
        if standup[key].strip() == "":
            standup[key] = "\n-"
    return standup
