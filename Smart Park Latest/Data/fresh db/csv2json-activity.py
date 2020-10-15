import csv,json

csvFilepath  ="Data/Activity.csv"
jsonFilepath ="Data/Activity.json"
recordDist = {}

with open(csvFilepath) as csvFile:
    csvReader = csv.DictReader(csvFile)
    print(csvReader)
    for rows in csvReader:
        id = rows['License']
        if id in recordDist:
            lst = recordDist[id]
        else:
            lst = []
            recordDist[id] = lst
        lst.append(rows)
    print(recordDist)
        

with open(jsonFilepath,'w') as jsonFile:
    jsonFile.write(json.dumps(recordDist,indent=4))


