
from os import times


file = "new_time.txt"
new_file = str(file.split(".txt")[0]) + "_analyzed.txt"
filter_word = "_simulate"
raw = open(file, "r")
new = open(new_file, "w")
total_time = 0

for line in raw:
    if filter_word in line:
        new.write(line)
        time = line.split(" ")[-2]
        total_time += float(time)

new.write(f"Total time for function {filter_word} is: {total_time}")

raw.close()
new.close()
