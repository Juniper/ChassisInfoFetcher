import json
import re

with open("commands/MX_12.txt", "r") as data_file:
    commandSettings = json.load(data_file)
for item in commandSettings["commandList"]:
	print re.sub('[|]', '"|"', item)