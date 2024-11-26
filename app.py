import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# Fonction pour importer ou ajouter une URL contenant un fichier XML
def import_xml(url):
    response = requests.get(url)
    if response.status_code == 200:
        return ET.fromstring(response.content)
    else:
        raise Exception("Erreur lors de l'importation du fichier XML")

# Fonction pour charger et analyser le fichier XML
def parse_xml(xml_root):
    data = []
    for item in xml_root.findall('.//item'):
        item_data = {}
        for child in item:
            item_data[child.tag] = child.text
        data.append(item_data)
    return pd.DataFrame(data)

st.title('Audit de Listing Shopping')

# Ajouter une URL contenant un fichier XML
url = st.text_input("Entrer l'URL du fichier XML")

if url:
    try:
        xml_root = import_xml(url)
        df_xml = parse_xml(xml_root)
        st.write("Aperçu des données XML importées:")
        st.write(df_xml.head())

        # Compter le nombre d'items dans le flux XML
        item_count = len(xml_root.findall('.//item'))
        st.write(f"Nombre d'items dans le flux XML: {item_count}")

    except Exception as e:
        st.error(f"Erreur lors de l'importation du fichier XML: {e}")