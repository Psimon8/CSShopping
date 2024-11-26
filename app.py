import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

# Définir les attributs obligatoires et recommandés par catégorie de produit US
required_attributes = {
    "Apparel & Accessories": ["id", "title", "description", "link", "image_link", "availability", "price", "gtin", "brand", "condition", "age_group", "color", "size", "item_group_id", "google_product_category", "gender"],
    "Books": ["id", "title", "description", "link", "image_link", "availability", "price", "gtin", "brand", "condition", "author", "publisher", "google_product_category"],
    "Media": ["id", "title", "description", "link", "image_link", "availability", "price", "condition", "gtin", "google_product_category"],
    "Electronics": ["id", "title", "description", "link", "image_link", "availability", "price", "condition", "gtin", "brand", "mpn", "google_product_category"],
    "Furniture": ["id", "title", "description", "link", "image_link", "availability", "price", "condition", "gtin", "brand", "mpn", "google_product_category"],
    "Food & Beverages": ["id", "title", "description", "link", "image_link", "availability", "price", "condition", "gtin", "brand", "google_product_category"],
    "Health & Beauty": ["id", "title", "description", "link", "image_link", "availability", "price", "condition", "gtin", "brand", "google_product_category"],
}

recommended_attributes = {
    "Apparel & Accessories": ["sale_price", "sale_price_effective_date", "shipping", "tax", "material", "pattern", "size_type", "size_system"],
    "Books": ["mpn", "language", "publication_date", "format", "pages", "isbn"],
    "Media": ["author", "publisher", "release_date", "format"],
    "Electronics": ["identifier_exists", "color", "size", "material", "pattern", "energy_efficiency_class", "age_group", "gender"],
    "Furniture": ["size", "item_group_id", "material", "pattern", "color"],
    "Food & Beverages": ["mpn", "product_highlight", "product_detail", "expiration_date", "energy_efficiency_class", "servings_per_container", "serving_size"],
    "Health & Beauty": ["mpn", "size", "color", "material", "pattern"],
}

# Correspondances des catégories FR -> US
category_mapping = {
    "Vêtements & Accessoires": "Apparel & Accessories",
    "Livres": "Books",
    "Médias": "Media",
    "Appareils Électroniques": "Electronics",
    "Mobilier": "Furniture",
    "Alimentation & Boissons": "Food & Beverages",
    "Santé & Beauté": "Health & Beauty",
}

# Fonction pour calculer le taux de complétion des attributs
def calculate_completion_rate(df, attributes):
    if attributes:
        return (df[attributes].notna().mean() * 100).tolist()
    return []

# Fonction pour générer le code HTML du graphique ApexCharts
def st_apex_charts(chart_data):
    chart_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    </head>
    <body>
        <div id="chart"></div>
        <script>
            var options = {chart_data};
            var chart = new ApexCharts(document.querySelector("#chart"), options);
            chart.render();
        </script>
    </body>
    </html>
    """
    st.components.v1.html(chart_html, height=600)

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

# Fonction pour vérifier la conformité du flux XML
def check_compliance(df, categories):
    compliance_report = {}
    for category in categories.keys():
        compliance_report[category] = df['category'].str.contains(category).sum()
    return compliance_report

# Fonction pour proposer des améliorations
def suggest_improvements(compliance_report):
    improvements = {}
    for category, count in compliance_report.items():
        if count == 0:
            improvements[category] = "Ajouter des éléments dans la catégorie " + category
    return improvements

st.title('Audit de Listing Shopping')

# Charger le fichier de listing
uploaded_file = st.file_uploader("Importer un fichier de listing CSV ou XLSX", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Lire le fichier en fonction de son type
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write("Aperçu des données importées:")
        st.write(df.head())

        # Sélectionner la catégorie de produit FR pour l'audit
        category_fr = st.selectbox("Sélectionner la catégorie de produit (FR)", list(category_mapping.keys()))

        if category_fr:
            category_us = category_mapping[category_fr]
            required = required_attributes.get(category_us, [])
            recommended = recommended_attributes.get(category_us, [])
            
            st.write(f"Attributs obligatoires pour {category_fr} ({category_us}): {required}")
            st.write(f"Attributs recommandés pour {category_fr} ({category_us}): {recommended}")

            # Calculer le taux de complétion
            required_completion_rate = calculate_completion_rate(df, required)
            recommended_completion_rate = calculate_completion_rate(df, recommended)

            # Préparer les données pour ApexCharts
            chart_data = {
                "chart": {
                    "type": "bar"
                },
                "series": [
                    {
                        "name": "Obligatoires",
                        "data": required_completion_rate
                    },
                    {
                        "name": "Recommandés",
                        "data": recommended_completion_rate
                    }
                ],
                "xaxis": {
                    "categories": required + recommended
                }
            }
            
            # Afficher le graphique avec ApexCharts
            st_apex_charts(chart_data)
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier de listing : {e}")

# Ajouter une URL contenant un fichier XML
url = st.text_input("Entrer l'URL du fichier XML")

if url:
    try:
        xml_root = import_xml(url)
        df_xml = parse_xml(xml_root)
        st.write("Aperçu des données XML importées:")
        st.write(df_xml.head())

        compliance_report = check_compliance(df_xml, category_mapping)
        improvements = suggest_improvements(compliance_report)

        st.write("Rapport de conformité:", compliance_report)
        st.write("Propositions d'améliorations:", improvements)

    except Exception as e:
        st.error(f"Erreur lors de l'importation du fichier XML: {e}")
