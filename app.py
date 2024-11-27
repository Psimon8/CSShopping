import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# Configuration de la page Streamlit
st.set_page_config(
    layout="wide",
    page_title="CSS Flux Audit",
    page_icon="🍧"
)

# URL du fichier XLSX dans le dépôt GitHub
xlsx_url = "https://raw.githubusercontent.com/Psimon8/CSShopping/main/CSS_CAT_FR_US.xlsx"

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
            # Remplacer les deux-points dans les noms de balises par des underscores
            tag = child.tag.replace('{http://base.google.com/ns/1.0}', 'g:')
            item_data[tag] = child.text
        data.append(item_data)
    return pd.DataFrame(data)

# Fonction pour charger le fichier XLSX contenant les catégories
def load_categories(url):
    df = pd.read_excel(url, usecols="A:C")
    df.columns = ['Category_Name', 'B', 'ID_CAT']  # Renommer les colonnes pour correspondre aux libellés
    return df

# Fonction pour trouver la correspondance exacte dans la colonne ID_CAT et afficher la valeur de la colonne Category_Name
def find_category_value(df, category):
    match = df[df['ID_CAT'].astype(str) == str(category)]
    if not match.empty:
        return match['Category_Name'].values[0]
    else:
        return None

st.title('Audit de Listing Shopping')

# Charger le fichier de catégories depuis GitHub
try:
    categories_df = load_categories(xlsx_url)
    st.write("Fichier de catégories chargé avec succès.")
except Exception as e:
    st.error(f"Erreur lors de l'importation du fichier de catégories: {e}")

# Ajouter une URL contenant un fichier XML
url = st.text_input("Entrer l'URL du fichier XML")

if url:
    try:
        xml_root = import_xml(url)
        df_xml = parse_xml(xml_root)

        # Compter le nombre d'items dans le flux XML
        item_count = len(xml_root.findall('.//item'))
        st.write(f"Nombre d'items dans le flux XML: {item_count}")

        # Afficher le nombre d'items dans les différentes catégories
        category_counts = df_xml['g:google_product_category'].value_counts()

        # Diviser l'affichage en deux colonnes
        col1, col2 = st.columns(2)

        with col1:
            st.write("Nombre d'items par catégorie:")
            for category, count in category_counts.items():
                category_value = find_category_value(categories_df, category)
                if category_value:
                    st.write(f"{category}: {count} items - {category_value}")
                else:
                    st.write(f"{category}: {count} items (Catégorie non trouvée dans le fichier XLSX)")

        with col2:
            st.write("Diagramme des catégories:")
            chart_data = pd.DataFrame({
                'Catégorie': category_counts.index,
                'Nombre d items': category_counts.values
            })
            st.bar_chart(chart_data.set_index('Catégorie'))

        st.write("Aperçu des données XML importées:")
        st.write(df_xml.head())

    except Exception as e:
        st.error(f"Erreur lors de l'importation du fichier XML: {e}")