import streamlit as st
import pandas as pd
import requests
from io import StringIO

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

# Fonction pour calculer le taux de complétion des attributs
def calculate_completion_rate(df, attributes):
    return df[attributes].notna().mean() * 100

st.title('Audit de Listing Shopping')

# Charger le fichier des catégories FR/US depuis GitHub
category_url = "https://github.com/Psimon8/CSShopping/category_mapping.csv"

try:
    category_file = requests.get(category_url).content
    category_df = pd.read_csv(StringIO(category_file.decode('utf-8')))
    category_mapping = dict(zip(category_df['FR'], category_df['US']))
    st.success("Le fichier de correspondance des catégories a été chargé avec succès.")
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier de correspondance des catégories : {e}")
    category_mapping = {}

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

        if category_fr and category_mapping:
            category_us = category_mapping[category_fr]
            required = required_attributes.get(category_us, [])
            recommended = recommended_attributes.get(category_us, [])
            
            st.write(f"Attributs obligatoires pour {category_fr} ({category_us}): {required}")
            st.write(f"Attributs recommandés pour {category_fr} ({category_us}): {recommended}")

            # Calculer le taux de complétion
            if required:
                required_completion_rate = calculate_completion_rate(df, required)
                st.write("Taux de complétion des attributs obligatoires:")
                st.write(required_completion_rate)
                st.write("Progression des attributs obligatoires:")
                for attr, rate in zip(required, required_completion_rate):
                    st.progress(int(rate))

            if recommended:
                recommended_completion_rate = calculate_completion_rate(df, recommended)
                st.write("Taux de complétion des attributs recommandés:")
                st.write(recommended_completion_rate)
                st.write("Progression des attributs recommandés:")
                for attr, rate in zip(recommended, recommended_completion_rate):
                    st.progress(int(rate))
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier de listing : {e}")
