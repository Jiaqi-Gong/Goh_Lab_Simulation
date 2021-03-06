"""
This file:
- Generates the graph of "Number of stuck bacteria at certain time VS Total number of bacteria"
- Gets several dynamic result files with same time step and combines them

* "Time" is an independent variable
* "Stuck bacteria number over time" is a dependent variable
"""

"""
Procedure for using this:
1. Put all dynamic results you want to combine in a folder called DynamicResult, 
2. Make sure this folder is under same root as this file,
3. Run this file to output your combined results in the folder DynamicResult.
"""

import os
from openpyxl import load_workbook, Workbook

folder_path = "../DynamicResult"

file_list = os.listdir(folder_path)
file_list.sort()

result = []

# init a new workbook
wb = Workbook()
ws1 = wb.create_sheet("Combine", 0)
timeStep = None

for file in file_list:
    if "trail" in file:
        filepath = "{}/{}".format(folder_path, file)
        workbook = load_workbook(filename=filepath)
        sheet = workbook["Results"]

        # get total time step
        if timeStep is None:
            timeStep = sheet["L"]
            result.append(timeStep)

        total_bact_col_name = "I"
        stuck_bact_col_name = "N"
        stuck_per_col_name = "Q"

        # get column for total bacteria, stuck bacteria and stuck percentage
        total_bact_col = sheet[total_bact_col_name]
        stuck_bact_col = sheet[stuck_bact_col_name]
        stuck_per_col = sheet[stuck_per_col_name]

        # Record result
        result.append(total_bact_col)
        result.append(stuck_bact_col)
        result.append(stuck_per_col)


# write result into ws
# generate rwo list, read every part in
for row_num in range(len(timeStep)):
    rowList = []
    for col in result:
        rowList.append(col[row_num].value)
    ws1.append(rowList)


# save result
name = "Dynamic_combine.xlsx"

file_path = "{}/{}".format(folder_path, name)

wb.save(file_path)




