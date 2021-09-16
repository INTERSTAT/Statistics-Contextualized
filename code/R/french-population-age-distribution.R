#' French population age distribution, using Insee census data.
library(httr)
library(dplyr)
library(readr)

# Constants ----
ZIP_URL <- "https://www.insee.fr/fr/statistiques/fichier/5395878/BTT_TD_POP1B_2018.zip"
ZIP_FILE_NAME <- "POP1B.zip"

REF_CLASSES_URL <- "https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/age-groups.csv"
REF_CLASSES_FILE_NAME <- "ref_classes.csv"

REF_NUTS3_URL <- "https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/nuts3.csv"
REF_NUTS3_FILE_NAME <- "nuts3.csv"

# Grabbing source data
resp <- httr::GET(ZIP_URL)
writeBin(resp$content, ZIP_FILE_NAME)

# Getting age classes reference file
resp_classes <- httr::GET(REF_CLASSES_URL)

# FIXME a direct read of the content should be possible
writeBin(resp_classes$content, REF_CLASSES_FILE_NAME) 

df_ref_classes <- readr::read_csv(REF_CLASSES_FILE_NAME)

# Nuts 3 for France
resp_nuts <- httr::GET(REF_NUTS3_URL)
writeBin(resp_nuts$content, REF_NUTS3_FILE_NAME)

df_ref_nuts3 <- readr::read_csv(REF_NUTS3_FILE_NAME)

# Handling data ----
df_pop1b <- readr::read_csv2(
  ZIP_FILE_NAME, 
  col_types = cols(
    NIVGEO = col_character(),
    CODGEO = col_character(),
    LIBGEO = col_character(),
    SEXE = col_factor(),
    AGED100 = col_double(),
    # FIXME for now we are handling the numeric transformation later
    NB = col_character() 
  )
)

# Grouping by age classes - except for the 100+
df_pop1b_classe_age <- df_pop1b %>%
  select(-c(NIVGEO, LIBGEO)) %>% 
  mutate(NB = as.numeric(NB)) %>% 
  mutate(
    CLASSE_AGE = cut(
      AGED100,
      breaks = 20,
      right = F,
      labels = df_ref_classes$group[1:20] # excluding 100+, specifically managed later
    )
  )

df_pop1b_somme <- df_pop1b_classe_age %>% 
  group_by(CODGEO, SEXE, CLASSE_AGE) %>% 
  summarise(SOMME = sum(NB))

# Managing 100+
df_pop1b_100 <- df_pop1b %>% 
  filter(AGED100 == "100") %>% 
  mutate(NB = as.numeric(NB)) %>% 
  mutate(CLASSE_AGE = df_ref_classes$group[21]) %>% 
  rename(SOMME = NB) %>% 
  select(CODGEO, SEXE, CLASSE_AGE, SOMME)

# All age classes dataset
df_pop1b_final <- df_pop1b_somme %>% 
  bind_rows(df_pop1b_100) %>% 
  arrange(CODGEO, SEXE)

# Adding NUTS
df_nuts <- df_pop1b_final %>% 
  mutate(
    CODGEO_COURT = case_when(
      # Oversea territories code have three caracters
      substr(CODGEO, 1, 2) == "97" ~ substr(CODGEO, 1, 3),
      TRUE ~ substr(CODGEO, 1, 2)
    )
  ) %>% 
  left_join(df_ref_nuts3, by = c("CODGEO_COURT" = "departement")) %>% 
  select(-CODGEO_COURT) %>% 
  rename(
    NUTS3 = nuts3, 
    LABEL = label
  )

# Writing results ---
readr::write_csv2(df_nuts, "pop1b_somme_classe_age.csv")
