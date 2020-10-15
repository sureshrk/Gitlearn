import csv,json

csvFilepath  ="Data/Spots.csv"
jsonFilepath ="Data/Spots.json"
recordList = []

with open(csvFilepath) as csvFile:
    csvReader = csv.DictReader(csvFile)
    print(csvReader)
    for rows in csvReader:
        print(rows)
        recordList.append(rows)
    print(recordList)

with open(jsonFilepath,'w') as jsonFile:
    jsonFile.write(json.dumps(recordList,indent=4))

