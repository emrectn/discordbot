from IPython.display import display
import requests
import re

from pandas import DataFrame

from lib.utils.config import settings

base_url = 'https://api.trello.com/1'
key = settings.trello_key
token = settings.trello_token
auth = "key={}&token={}".format(key, token)
boards_url = "/boards/"
member_dict = {}
member_tasks = {}


def get_member_name_by_id(member_id):
    global member_dict, base_url, auth
    if member_id in member_dict:
        return member_dict[member_id]
    else:
        get_member_details_url = base_url+"/members/"+member_id+"?"+auth
        member_details = requests.get(get_member_details_url).json()
        member_name = member_details["fullName"]
        member_dict[member_id] = member_name
    return member_name


def get_boards():
    global base_url, auth
    get_member_boards_url = base_url+"/members/me/boards?fields=name,url&"+auth
    boards = requests.get(get_member_boards_url).json()
    return boards


def get_board_details(board_id):
    global base_url, auth
    get_board_details_url = base_url+"/boards/"+board_id+"/lists?"+auth
    board_details = requests.get(get_board_details_url).json()
    return board_details


def get_list_details(list_id):
    global base_url, auth
    get_list_details_url = base_url+"/lists/"+list_id+"/cards?"+auth
    list_details = requests.get(get_list_details_url).json()
    return list_details


def get_card_details(board_id, card_id):
    global base_url, auth

    get_card_details_url = base_url+"/boards/"+board_id+"/cards/"+card_id+"?"+auth
    card_details = requests.get(get_card_details_url).json()

    card_name = card_details["name"]
    card_id_members = card_details["idMembers"]

    id_checklists = card_details["idChecklists"]
    card_last_activity = card_details["dateLastActivity"]

    # if len(id_checklists) > 0:
    #     print("card has checklist")  # TODO: implement checklist control

    # get members of card
    member_list = []
    for member_id in card_id_members:
        member_list.append(get_member_name_by_id(member_id))
    return card_name, card_last_activity, member_list


def get_data_from_trello():
    member_tasks = {}
    boards = get_boards()#  get all boards
    keywords = ['todo', 'to do', 'progress', 'yapılacak', 'yapılıyor']
    for index, board in enumerate(boards):
        # print("\n\n************")

        board_id = board["id"]
        board_name = board["name"]

        print("*" + board_id, board_name, f'({index+1}/{len(boards)})')  
        board_lists = get_board_details(board_id)  # get board details
        for board_list in board_lists:
            if not any(x in re.sub('-', '', board_list["name"]).lower() for x in keywords):
                continue
            list_id = board_list["id"]
            list_name = board_list["name"]
                

            print("**" + list_id, list_name)
            list_details = get_list_details(list_id)  # get lists of board
            for card_detail in list_details:
                card_id = card_detail["id"]
                card_name = card_detail["name"]
                # print("***" + card_id, card_name)

                card_name, card_last_activity, member_list = get_card_details(
                    board_id, card_id)

                for member in member_list:
                    if member not in member_tasks:
                        member_tasks[member] = {}
                    if board_name not in member_tasks[member]:
                        member_tasks[member][board_name] = {}
                    if list_name not in member_tasks[member][board_name]:
                        member_tasks[member][board_name][list_name] = []
                    member_tasks[member][board_name][list_name].append(card_name)
                    
    return member_tasks


def list_members():
    global member_tasks
    members = []
    for el in member_tasks.keys():
        # print(el)
        members.append(el)
    return members


def get_task_counts_per_member():
    global member_tasks
    task_counts = {}
    for el in member_tasks.keys():
        task_counts[el] = len(member_tasks[el])
    return sorted(task_counts.items(), key=lambda x: x[1])


def show_tasks_for_member(member_name):
    global member_tasks
    print("*"*5+member_name+"*"*5)
    try:
        mt = member_tasks[member_name]
    except:
        return
    df = DataFrame(mt, columns=['Board', 'List', 'Card', 'LastActivity'])
    display(df)


def retrieve_tasks_for_member(member_name):
    global member_tasks
    print("*"*5+member_name+"*"*5)
    try:
        mt = member_tasks[member_name]
    except:
        return
    df = DataFrame(mt, columns=['Board', 'List', 'Card', 'LastActivity'])
    return df.to_html()
