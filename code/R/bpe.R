library(httr)
library(dplyr)
library(readr)

# This script extracts a list of columns from the CSV file containing the data from the 2020 Permanent database of facilities
# (BPE in French) published by Insee.
# See https://www.insee.fr/en/metadonnees/source/serie/s1161 for more information on the BPE.
# The main landing page for data access is https://www.insee.fr/fr/statistiques/3568638?sommaire=3568656.
# The extraction here operates on the geocoded "sport & leisure" BPE data.

# URL of the archive, and name of the data file inside the archive
target_url <- "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_sport_Loisir_xy_csv.zip"
file_name <- "bpe20_sport_loisir_xy.csv"

# Get the archive and save it locally
resp <- httr::GET(target_url)
writeBin(resp$content, "bpe.zip")

# Read the data file from the locally saved archive
df_bpe <- readr::read_csv2(unz("bpe.zip", file_name))

# Select the desired colums
df_bpe_select <- df_bpe %>%
  select(AN, COUVERT, DEPCOM, ECLAIRE, LAMBERT_X, LAMBERT_Y, NBSALLES, QUALITE_XY, TYPEQU)

# Write the extract in a local CSV file
readr::write_csv2(df_bpe_select, "bpe_select.csv")
