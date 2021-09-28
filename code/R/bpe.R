library(httr)
library(dplyr)
library(readr)

target_url <- "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_sport_Loisir_xy_csv.zip"

resp <- httr::GET(target_url)

writeBin(resp$content, "bpe.zip")

df_bpe <- readr::read_csv2("bpe.zip")

df_bpe_select <- df_bpe %>%
  select(AN, COUVERT, DEPCOM, ECLAIRE, LAMBERT_X, LAMBERT_Y, NBSALLES, QUALITE_XY, TYPEQU)

readr::write_csv2(df_bpe_select, "bpe_select.csv")
