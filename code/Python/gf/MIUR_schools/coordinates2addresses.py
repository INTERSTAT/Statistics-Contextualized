'France Air Quality Data: from coordinates to addresses'
import csv
import requests
import os


def coordinates2addresses():
    input_file = csv.reader(open(os.getcwd() + '\\resources\\data_PM10_France-csv.csv', 'r'), delimiter=",")
    output_file = open(os.getcwd() + '\\resources\\data_PM10_France-csv-Municipality.csv', 'w')
    print("Raw input file obtained successfully. Please wait...")

    next(input_file)
    output_file.write('CountryOrTerritory,ReportingYear,UpdateTime,StationLocalId,SamplingPointLocalId,SamplingPoint_Latitude,SamplingPoint_Longitude,Municipality,'
                      'Pollutant,AggregationType,Namespace,Unit,BeginPosition,EndPosition,Validity,Verification,DataCoverage,DataCapture,TimeCoverage,AQValue\n')
    for fields in input_file:
        lat = fields[5]
        lon = fields[6]
        api = "https://nominatim.openstreetmap.org/reverse?format=json&"
        info = "lat="+lat+"&lon="+lon+"&zoom=18&addressdetails=1"

        r = requests.get(api + info)
        data = r.json()
        print(api + info)

        data_dict = data['address']
        if "city_district" in data_dict:
            municipality = data_dict["city_district"]
        elif "municipality" in data_dict:
            municipality = data_dict["municipality"]
        else:
            municipality = data_dict["city"]

        newRow = fields[0]+","+fields[1]+","+fields[2]+","+ fields[3]+","+fields[4]+","+fields[5]+","+fields[6]+","+\
                 municipality+","+fields[7]+","+fields[8]+","+fields[9]+","+ fields[10]+","+fields[11]+","+fields[12]+","+fields[13]+","+\
                 fields[14]+","+fields[15]+","+fields[16]+","+ fields[17]+","+fields[18]

        output_file.write(newRow+'\n')

    output_file.close();
