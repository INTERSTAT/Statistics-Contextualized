"""
Technical configuration for the S4Y pipeline.
"""

conf = {
    "flags": {
        "prefect": {
            "pushToCloudDashboard": False,
            "displayGraphviz": False
        },
        "flow": {
            "testing": False
        }
    },
    "env": {
        "workingDirectory": ""
    },
    "students_datasets": [
        {
            "id": "fr-en-ecoles-effectifs-nb_classes",
            "csv_url": "https://data.education.gouv.fr/explore/dataset/fr-en-ecoles-effectifs-nb_classes/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B",
            "types": {"Numéro de l'école": str, "Rentrée scolaire": str,
                      "Nombre d'élèves en pré-élémentaire hors ULIS": int,
                      "Nombre d'élèves en CP hors ULIS": int, "Nombre d'élèves en CE1 hors ULIS": int,
                      "Nombre d'élèves en CE2 hors ULIS": int, "Nombre d'élèves en CM1 hors ULIS": int,
                      "Nombre d'élèves en CM2 hors ULIS": int},
            "mapping_course_year": {"0": ["Nombre d'élèves en pré-élémentaire hors ULIS"],
                                    "1": ["Nombre d'élèves en CP hors ULIS"],
                                    "2": ["Nombre d'élèves en CE1 hors ULIS"],
                                    "3": ["Nombre d'élèves en CE2 hors ULIS"],
                                    "4": ["Nombre d'élèves en CM1 hors ULIS"],
                                    "5": ["Nombre d'élèves en CM2 hors ULIS"]}
        },
        {
            "id": "fr-en-college-effectifs-niveau-sexe-lv",
            "csv_url": "https://data.education.gouv.fr/explore/dataset/fr-en-college-effectifs-niveau-sexe"
                       "-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true"
                       "&csv_separator=%3B",
            "types": {"Numéro du collège": str, "Rentrée scolaire": str, "Nombre total de 6èmes": int,
                      "Nombre total de 5èmes": int, "Nombre total de 4èmes": int,
                      "Nombre total de 3èmes": int},
            "mapping_course_year": {"6": ["Nombre total de 6èmes"], "7": ["Nombre total de 5èmes"],
                                    "8": ["Nombre total de 4èmes"], "9": ["Nombre total de 3èmes"]}
        },
        {
            "id": "fr-en-lycee_gt-effectifs-niveau-sexe-lv",
            "csv_url": "https://data.education.gouv.fr/explore/dataset/fr-en-lycee_gt-effectifs-niveau"
                       "-sexe-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header"
                       "=true&csv_separator=%3B",
            "types": {"Numéro du lycée": str, "Rentrée scolaire": str, "2ndes GT": int,
                      "2ndes STHR": int, "2ndes TMD": int, "2ndes BT": int, "1ères G": int,
                      "1ères STI2D": int, "1ères STL": int, "1ères STMG": int, "1ères ST2S": int,
                      "1ères STD2A": int, "1ères STHR": int, "1ères TMD": int, "1ères BT": int,
                      "Terminales G": int, "Terminales STI2D": int, "Terminales STL": int,
                      "Terminales STMG": int, "Terminales ST2S": int, "Terminales STD2A": int,
                      "Terminales STHR": int, "Terminales TMD": int, "Terminales BT": int},
            "mapping_course_year": {"10": ["2ndes GT", "2ndes STHR", "2ndes TMD", "2ndes BT"],
                                    "11": ["1ères G", "1ères STI2D", "1ères STL", "1ères STMG", "1ères ST2S",
                                           "1ères STD2A", "1ères STHR", "1ères TMD", "1ères BT"],
                                    "12": ["Terminales G", "Terminales STI2D", "Terminales STL",
                                           "Terminales STMG", "Terminales ST2S", "Terminales STD2A",
                                           "Terminales STHR", "Terminales TMD", "Terminales BT"]}
        },
        {
            "id": "fr-en-lycee_pro-effectifs-niveau-sexe-lv",
            "csv_url": "https://data.education.gouv.fr/explore/dataset/fr-en-lycee_pro-effectifs-niveau-sexe-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B",
            "types": {"Numéro du lycée": str, "Rentrée scolaire": str, "2ndes PRO": int, "CAP 1ère année": int, "CAP en 1 an": int, "BMA 1ère année": int, "BMA en 1 an": int, "CAP 2nde année": int, "1ères PRO": int, "Terminales PRO": int, "MC": int},
            "mapping_course_year": {"10": ["2ndes PRO", "CAP 1ère année", "CAP en 1 an", "BMA 1ère année", "BMA en 1 an"],
                                    "11": ["CAP 2nde année", "1ères PRO"],
                                    "12": ["Terminales PRO"]}
        }
    ]
}
'''
        {
            "id": "fr-en-ecoles-effectifs-nb_classes",
            "csv_url": "https://data.education.gouv.fr/explore/dataset/fr-en-ecoles-effectifs-nb_classes/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B",
            "types": {"numero_ecole": str, "rentree_scolaire": str,
                      "nombre_eleves_preelementaire_hors_ulis": int,
                      "nombre_eleves_cp_hors_ulis": int, "nombre_eleves_ce1_hors_ulis": int,
                      "nombre_eleves_ce2_hors_ulis": int, "nombre_eleves_cm1_hors_ulis": int,
                      "nombre_eleves_cm2_hors_ulis": int},
            "mapping_course_year": {"0": ["nombre_eleves_preelementaire_hors_ulis"],
                                    "1": ["nombre_eleves_cp_hors_ulis"],
                                    "2": ["nombre_eleves_ce1_hors_ulis"],
                                    "3": ["nombre_eleves_ce2_hors_ulis"],
                                    "4": ["nombre_eleves_cm1_hors_ulis"],
                                    "5": ["nombre_eleves_cm2_hors_ulis"]}
        },
        {
            "id": "fr-en-college-effectifs-niveau-sexe-lv",
            "csv_url": "https://data.education.gouv.fr/explore/dataset/fr-en-college-effectifs-niveau-sexe"
                       "-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true"
                       "&csv_separator=%3B",
            "types": {"numero_college": str, "rentree_scolaire": str, "6eme_total": int},
            "mapping_course_year": {"6": ["6eme_total"], "7": ["5eme_total"],
                        "8": ["4eme_total"], "9": ["3eme_total"]}
        },
        {
            "id": "fr-en-lycee_gt-effectifs-niveau-sexe-lv",
            "csv_url": "https://data.education.gouv.fr/explore/dataset/fr-en-lycee_gt-effectifs-niveau"
                       "-sexe-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header"
                       "=true&csv_separator=%3B",
            "types": {"numero_lycee": str, "rentree_scolaire": str, "2ndes_gt": int,
             "2ndes_sthr": int, "2ndes_tmd": int, "2ndes_bt": int, "1eres_g": int,
             "1eres_sti2d": int, "1eres_stl": int, "1eres_stmg": int, "1eres_st2s": int,
             "1eres_std2a": int, "1eres_sthr": int, "1eres_tmd": int, "1eres_bt": int,
             "terminales_g": int, "terminales_sti2d": int, "terminales_stl": int,
             "terminales_stmg": int, "terminales_st2s": int, "terminales_std2A": int,
             "terminales_sthr": int, "terminales_tmd": int, "terminales_bt": int},
            "mapping_course_year": {"10": ["2ndes_gt", "2ndes_sthr", "2ndes_tmd", "2ndes_bt"],
                        "11": ["1eres_g", "1eres_sti2d", "1eres_stl", "1eres_stmg", "1eres_st2s",
                               "1eres_std2a", "1eres_sthr", "1eres_tmd", "1eres_bt"],
                        "12": ["terminales_g", "terminales_sti2d", "terminales_stl",
                               "terminales_stmg", "terminales_st2s", "terminales_std2A",
                               "terminales_sthr", "terminales_tmd", "terminales_bt"]}
        },
        {
            "id": "fr-en-lycee_pro-effectifs-niveau-sexe-lv",
            "csv_url": "https://data.education.gouv.fr/explore/dataset/fr-en-lycee_pro-effectifs-niveau-sexe-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B",
            "types": {"numero_lycee": str, "rentree_scolaire": str, "2ndes_pro": int, "cap_1ere_annee": int, "cap_en_1_an": int, "bma_1ere_annee": int, "bma_en_1_an": int, "cap_2nde_annee": int, "1eres_pro": int, "terminales_pro": int, "mc": int},
            "mapping_course_year": {"10": ["2ndes_pro", "cap_1ere_annee", "cap_en_1_an", "bma_1ere_annee", "bma_en_1_an"],
                        "11": ["cap_2nde_annee", "1eres_pro"],
                        "12": ["terminales_pro"]}
        }
'''

