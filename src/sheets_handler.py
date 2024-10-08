import gspread
from oauth2client.service_account import ServiceAccountCredentials
import urllib.request
import json
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#CREDENTIALS = 'Quickstart-f94184934ce3.json'
CREDENTIALS = 'Grap-c4b50445bb91.json'
SHEET_TOKEN_PATH = os.path.join(ROOT_DIR, CREDENTIALS)
#SHEET_ID_WRITE = '1e2b5z2ydOKQBLGvgNfbBUbGv1C09UUG2KQBCiOJUkeo'
#SHEET_ID_READ = '1BsNMbjRzqzWhZ0ODWR0Bw1w46bJgKYPyvfIz2YFB-DM'
SHEET_ID_WRITE = "1ii7xOYtg-7cZftmHJVxD2i0IiVm6w_e3Rvj0jTRtXXQ"
SHEET_ID_READ = "1us5gqUSqjX0ejNtQyVsAbSTLjiBZ8gWm2JnaBWkTwbk"

def get_sheet(id, token_path):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(token_path, scope)
    gc = gspread.authorize(credentials)
    return gc.open_by_key(id).sheet1


def write_sheet(row):
    sheet = get_sheet(SHEET_ID_WRITE, SHEET_TOKEN_PATH)
    sheet.append_row(row)

    #sheet.clear()

    # n_rows = 10
    # n_cols = 3
    # cells = sheet.range(1, 1, n_rows, n_cols)
    # i = 0
    # for i in range(n_rows):
    #     for j in range(n_cols):
    #         cells[i*n_cols + j].value = f"{i}, {j}"

    # sheet.update_cells(cells)


def read_sheet():
    sheet = get_sheet(SHEET_ID_READ, SHEET_TOKEN_PATH)

    return sheet.get_all_records()

