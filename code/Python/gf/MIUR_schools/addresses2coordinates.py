'MIUR_Schools: from addresses to coordinates'
import csv
import re
import requests
import os
import urllib.parse


def addresses2coordinates():
    input_file = csv.reader(open(os.getcwd() + '\\resources\\MIUR Schools.tsv', 'r'), delimiter="\t")
    output_file = open(os.getcwd() + '\\resources\\MIUR_Schools_with_coordinates.csv', 'w')
    print("Raw input file obtained successfully. Please wait...")

    next(input_file)
    output_file.write('AnnoScolastico,CodiceComune,DescrizioneComune,SiglaProvincia,TipologiaIndirizzo,'
                      'DenominazioneIndirizzo,NumeroCivico,CAP,Latitude,Longitude,ExactLocation\n')
    for fields in input_file:
        # N.B. The following elaborations have been made only because the addresses were not written correctly
        # in the starting dataset, otherwise they will not be necessary.

        #Deleting special characters from addresses, except the apostrophe and the point
        TipologiaIndirizzo = re.sub(r"[^a-zA-Z0-9 `']+", '', fields[4])
        DenominazioneIndirizzo = re.sub(r"[^a-zA-Z0-9 `'.]+", '', fields[5]).replace(",", "")
        DescrizioneComune = re.sub(r"[^a-zA-Z0-9 `']+", '', fields[2])
        NumeroCivico = fields[6]

        #Incomplete names are not found by the server (for example "via G. SIANI" or "via G.Leopardi")
        #so only the surname is taken (for example "via SIANI" or "via Leopardi)
        if ("." in DenominazioneIndirizzo) and (" " in DenominazioneIndirizzo):
            splitted = DenominazioneIndirizzo.split(" ")
        else:
            splitted = DenominazioneIndirizzo.split(".")
        DenominazioneIndirizzo = splitted[len(splitted) - 1]

        #If a comma is present, only the first part of the address or house number is considered
        if "," in DenominazioneIndirizzo: DenominazioneIndirizzo = DenominazioneIndirizzo.split(",")[0]
        if "," in NumeroCivico: NumeroCivico = NumeroCivico.split(",")[0]

        apiService = "https://nominatim.openstreetmap.org/search?street="
        url = urllib.parse.quote(TipologiaIndirizzo.encode('utf-8')) + "%20" + \
              urllib.parse.quote(DenominazioneIndirizzo.encode('utf-8')) + "+&city=" + urllib.parse.quote(
            DescrizioneComune.encode('utf-8')) + \
              "&format=json&limit=1"

        newRow = fields[0] + "," + fields[1] + "," + DescrizioneComune + "," + fields[
            3] + "," + TipologiaIndirizzo + "," + \
                 DenominazioneIndirizzo + "," + NumeroCivico + "," + fields[7] + ","

        NumeroCivico_is_a_digit = False
        address_found = False
        #It checks whether the house number is a numerical value
        if (bool(re.search(re.compile("^\d+$"), NumeroCivico))):
            NumeroCivico_is_a_digit = True
            api = apiService + urllib.parse.quote(NumeroCivico.encode('utf-8')) + "+" + url
        else:
            api = apiService + url

        r = requests.get(api)
        data = r.json()
        print(api)
        if (len(data) > 0): address_found = True

        if NumeroCivico_is_a_digit and address_found:
            output_file.write(newRow + data[0]['lat'] + "," + data[0]['lon'] + "," + 'true\n')
        elif (NumeroCivico_is_a_digit is False) and address_found:
            output_file.write(newRow + data[0]['lat'] + "," + data[0]['lon'] + "," + 'false\n')
        else:
            output_file.write(newRow + ',' + ',false\n')

    output_file.close();
