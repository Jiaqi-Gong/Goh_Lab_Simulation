"""
This file:
- Sorts the total number of bacteria and number of stuck bacteria based on timestep

"""
"""
Procedure:
1. If you haven't done so already, either create a new excel file or run the combineExcel file 
    - If you didn't run the combineExcel file, you will need to make a folder called DynamicResult, and a excel file called Dynamic_combine
        - Make sure the excel file is in .xlsx format in order for it to properly work
    - If you ran the combineExcel file, everything should be set
2. Make sure the first sheet on the Dynamic_combine file is the combined data 
3. Change the timestep variable to the necessary timestep 
4. You can also change if you want to see the index on the excel file or not

"""
import pandas as pd
import os
from openpyxl import load_workbook, Workbook
import re


# create a function which outputs excel file for different timesteps
def _sortTimestep(timestep: int, show_index: bool):
    """
    This function sorts out the Dynamic_combine into timestep inputted by the user
    """

    # import excel file
    folder_path = "../DynamicResult"
    file = "Dynamic_combine.xlsx"
    path = f'{folder_path}/{file}'

    # read the first sheet
    master_sheet = pd.read_excel(path, sheet_name=0, index_col=None)

    # determine the row of that timestep
    row = master_sheet[master_sheet["Time step"] == timestep]

    # make this into a dictionary, and initialize another dictionary
    row = row.to_dict()
    nrow = {}

    # find all the keys of the dictionary
    list_header = list(row.keys())
    for ind in range(len(list_header)):
        key = list_header[ind]

        # if the key is a duplicate, we will add it to an existing key
        if any(map(str.isdigit, key)):
            # determine the actual key
            digit = re.findall('[0-9]+', key)[0]
            digit_index = key.find(digit)
            fix_key = key[:digit_index - 1]

            # append it to the existing key
            nrow[fix_key].append(row[key][timestep])

        # if the key is not a duplicate, make it a new key
        else:
            nrow[key] = [row[key][timestep]]

    # remove the timestep key from the dictionary
    nrow.pop("Time step")

    # create a new dataframe
    timestep_sheet = pd.DataFrame(nrow)

    # write the new sheet onto the existing excel file
    with pd.ExcelWriter(path, mode='a') as writer:
        timestep_sheet.to_excel(writer, sheet_name=f"Timestep = {timestep}", engine='openpyxl', index=show_index)


# input timestep you want to determine
timestep = 200
show_index = False

if __name__ == '__main__':
    _sortTimestep(timestep, show_index)