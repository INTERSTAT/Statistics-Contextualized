'MIUR_Schools: add school codes'
import csv
import re
from dis import code_info

import requests
import os
import urllib.parse


def add_school_code():

    input_file_withCodes = csv.reader(open(os.getcwd() + '\\resources\\MIUR Schools.csv', 'r'), delimiter=",")
    output_file = open(os.getcwd() + '\\resources\\MIUR_Schools_with_coordinates_addedSchoolCodes.csv', 'w')
    dict = {}

    output_file.write('AnnoScolastico,CodiceComune,DescrizioneComune,SiglaProvincia,TipologiaIndirizzo,'
                      'DenominazioneIndirizzo,NumeroCivico,CAP,Latitude,Longitude,ExactLocation,CodiceScuola\n')

    next(input_file_withCodes)
    for fields in input_file_withCodes:
        l = fields[0] + "\t" + fields[3] + "\t" + fields[4] + "\t" + fields[5] + "\t" + fields[6] + \
            "\t" + fields[7] + "\t" + fields[8] + "\t" + fields[9]
        if not fields[1] in dict:
            list = [l]
            dict[fields[1]] = list
        else:
            dict[fields[1]].append(l)

    print(len(dict))

    with open(os.getcwd() + '\\resources\\MIUR Schools.tsv') as input_file_tsv, \
            open(os.getcwd() + '\\resources\\MIUR_Schools_with_coordinates.csv') as input_file_withCoordinates:
        line = input_file_tsv.readline()
        line2 = input_file_withCoordinates.readline()
        while line and line2:
            line = input_file_tsv.readline().rstrip('\n').replace('"','')
            line2 = input_file_withCoordinates.readline().rstrip('\n')
            codScuola = [k for (k, v) in dict.items() if line in v]
            if(len(codScuola)>0):
                for code in codScuola:
                    output_file.write(line2 + ',' + code + '\n')

    output_file.close();





