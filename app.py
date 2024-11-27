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

# Fonction pour importer et analyser le sitemap product XML
def import_sitemap(url):
    response = requests.get(url)
    if response.status_code == 200:
        return ET.fromstring(response.content)
    else:
        raise Exception("Erreur lors de l'importation du sitemap XML")

# Fonction pour compter le nombre de produits dans le sitemap XML
def count_sitemap_products(xml_root):
    return len(xml_root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'))

# Fonction pour extraire les URLs des produits du sitemap XML
def extract_sitemap_urls(xml_root):
    return [loc.text for loc in xml_root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]

# Fonction pour importer ou ajouter une URL contenant un fichier XML flux shopping
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

# Diviser l'affichage en deux colonnes
col1, col2 = st.columns(2)

with col1:
    sitemap_url = st.text_input("Entrer l'URL du sitemap produit")
    if sitemap_url:
        try:
            sitemap_root = import_sitemap(sitemap_url)
            product_count = count_sitemap_products(sitemap_root)
            st.write(f"Nombre de produits dans le sitemap: {product_count}")
        except Exception as e:
            st.error(f"Erreur lors de l'importation du sitemap produit: {e}")

    url = st.text_input("Entrer l'URL du fichier XML")
    if url:
        try:
            xml_root = import_xml(url)
            df_xml = parse_xml(xml_root)

            # Compter le nombre d'items dans le flux XML
            item_count = len(xml_root.findall('.//item'))
            st.write(f"Nombre d'items dans le flux XML: {item_count}")

        except Exception as e:
            st.error(f"Erreur lors de l'importation du fichier XML: {e}")

with col2:
    if url:
        try:
            # Vérifier si la colonne 'g:google_product_category' existe dans le DataFrame
            if 'g:google_product_category' in df_xml.columns:
                # Afficher le nombre d'items dans les différentes catégories
                category_counts = df_xml['g:google_product_category'].value_counts()
                st.write("Nombre d'items par catégorie:")
                for category, count in category_counts.items():
                    category_value = find_category_value(categories_df, category)
                    if category_value:
                        st.write(f"{category}: {count} items - {category_value}")
                    else:
                        st.write(f"{category}: {count} items (Catégorie non trouvée dans le fichier XLSX)")
            else:
                st.write("La colonne 'g:google_product_category' n'existe pas dans le fichier XML importé.")
        except Exception as e:
            st.error(f"Erreur lors de l'analyse des catégories: {e}")

st.write("Aperçu des données XML importées:")
st.write(df_xml.head(20))

# Extraire les URLs des produits du sitemap XML
if sitemap_url and url:
    try:
        sitemap_urls = extract_sitemap_urls(sitemap_root)
        xml_urls = df_xml['g:link'].tolist()  # Assurez-vous que la colonne 'g:link' contient les URLs des produits dans le flux XML

        # Trouver les URLs des produits qui ne sont pas disponibles dans le flux XML
        missing_urls = [url for url in sitemap_urls if url not in xml_urls]

        st.write("URLs des produits non disponibles dans le flux XML:")
        st.write(pd.DataFrame(missing_urls, columns=["URL"]))

    except Exception as e:
        st.error(f"Erreur lors de l'extraction des URLs des produits: {e}")