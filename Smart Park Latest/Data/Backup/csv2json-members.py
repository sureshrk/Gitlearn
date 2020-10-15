import csv,json

csvFilepath  ="data/Members.csv"
jsonFilepath ="data/Members.json"
recordDist = {}

with open(csvFilepath) as csvFile:
    csvReader = csv.DictReader(csvFile)
    print(csvReader)
    for rows in csvReader:
        id = rows['License']
        recordDist[id] = rows

with open(jsonFilepath,'w') as jsonFile:
    jsonFile.write(json.dumps(recordDist,indent=4))


