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

# Fonction pour charger le fichier XLSX contenant les catégories
def load_categories(file_path):
    df = pd.read_excel(file_path, usecols="A:C")
    return df

# Fonction pour trouver la correspondance exacte dans la colonne C et afficher la valeur de la colonne A
def find_category_value(df, category):
    match = df[df['C'] == category]
    if not match.empty:
        return match['A'].values[0]
    else:
        return None

st.title('Audit de Listing Shopping')

# Charger le fichier de catégories
uploaded_file = st.file_uploader("Importer le fichier de catégories XLSX", type=["xlsx"])

if uploaded_file:
    try:
        categories_df = load_categories(uploaded_file)
        st.write("Fichier de catégories chargé avec succès.")
    except Exception as e:
        st.error(f"Erreur lors de l'importation du fichier de catégories: {e}")

# Ajouter une URL contenant un fichier XML
url = st.text_input("Entrer l'URL du fichier XML")

if url and uploaded_file:
    try:
        xml_root = import_xml(url)
        df_xml = parse_xml(xml_root)

        # Compter le nombre d'items dans le flux XML
        item_count = len(xml_root.findall('.//item'))
        st.write(f"Nombre d'items dans le flux XML: {item_count}")

        st.write("Aperçu des données XML importées:")
        st.write(df_xml.head())

        # Afficher le nombre d'items dans les différentes catégories
        category_counts = df_xml['g:google_product_category'].value_counts()
        st.write("Nombre d'items par catégorie:")

        for category, count in category_counts.items():
            category_value = find_category_value(categories_df, category)
            if category_value:
                st.write(f"{category_value}: {count}")
            else:
                st.write(f"{category}: {count} (Catégorie non trouvée dans le fichier XLSX)")

    except Exception as e:
        st.error(f"Erreur lors de l'importation du fichier XML: {e}")