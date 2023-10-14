import json

def write_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)
    
    print('Done writing to file', filename)
