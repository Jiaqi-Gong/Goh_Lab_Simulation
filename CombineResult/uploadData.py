import os.path
from typing import List

import pandas as pd

# key is trail number, value is equilibrium value
result_data = {}

# key is column number, value is equilibrium value
write_data = {}


def main(source_folder: str, target_file: str, target_col_name: str):
    directory = os.fsencode(source_folder)

    # get data
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".xlsx"):
            file_path = "{}/{}".format(source_folder, filename)

            data = pd.read_excel(file_path)
            trail = data["Trail"][0]
            eq_result = data["equilibrium bacteria stuck"][0]

            result_data[trail] = eq_result

    # print(result_data)

    # open target file
    target = pd.read_excel(target_file)
    trails = pd.read_excel(target_file, usecols=[0]).values.tolist()

    for count, value in enumerate(trails):
        val = value[0]
        if val in result_data:
            write_data[count] = result_data[val]

    # print(write_data)

    # print(target)
    # write data
    for key in write_data.keys():
        target.at[int(key), target_col_name] = write_data[key]

    # print(target)

    target.to_excel("Result_Combined.xlsx", index=False)


if __name__ == '__main__':
    source_folder = "Result/ResultDynamic"
    target_file = "(Bacteria #) Dynamic Trials 2.xlsx"
    target_col_name = "Equilibrium"
    main(source_folder, target_file, target_col_name)
