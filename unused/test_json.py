import json

#Given dict name as str, and dictionary, convert dict to JSON then return name of JSON file.
def store(name, dictionary):
	json_filename = name + '.json'
	with open(json_filename, "w") as outfile:
		json.dump(dictionary, outfile)
	return json_filename

#Given filename as str, convert JSON to dict and return dictionary.
def load(json_filename):
	with open(json_filename) as json_file:
		data = json.load(json_file)
	return data

if __name__ == '__main__':

	tester = {'red':  1,
			  'blue': 2}

	filename = store('test', tester)

	data = load(filename)

	print(data)
	print(tester == data)