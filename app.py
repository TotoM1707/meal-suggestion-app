import streamlit as st
import pandas as pd
import os

# Load the data
file_path = 'LEMME_Chat_Translated_Manual_DE.xlsx'
if not os.path.exists(file_path):
    st.error("Die Datei wurde nicht gefunden. Bitte stellen Sie sicher, dass sich die Datei unter 'C:/Mira/LEMME_Chat_Translated_Manual_DE.xlsx' befindet.")
    st.stop()

try:
    # Ensure openpyxl is available
    import openpyxl
    data = pd.read_excel(file_path, sheet_name='Sheet1')
except ImportError:
    st.error("Fehlende Abhängigkeit: 'openpyxl'. Installieren Sie es mit 'pip install openpyxl'.")
    st.stop()
except Exception as e:
    st.error(f"Fehler beim Laden der Datei: {e}")
    st.stop()

# Clean the data to remove unnecessary rows (e.g., headers within the data)
data = data.dropna(subset=['Frühstück', 'Mittag', 'Abend'])
if data.empty:
    st.error("Die Daten sind leer oder ungültig. Bitte überprüfen Sie die Quelle.")
    st.stop()

# Normalize data to avoid filtering issues
data['Frühstück'] = data['Frühstück'].astype(str).str.strip().str.lower()
data['Mittag'] = data['Mittag'].astype(str).str.strip()
data['Abend'] = data['Abend'].astype(str).str.strip()

# Streamlit App
def main():
    st.title("Mahlzeit-Empfehlungen mit Wochenplan und Einkaufsliste")

    # Wochenplan erstellen mit Tabs
    st.write("## Wochenplan erstellen")
    days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
    weekly_plan = {}

    tabs = st.tabs(days)

    for day, tab in zip(days, tabs):
        with tab:
            st.write(f"### {day}")

            # Kategorieauswahl und Suche
            search_category = st.radio(f"Welche Kategorie möchtest du durchsuchen? ({day})", ("Frühstück", "Mittag", "Abend"), key=f"search_category_{day}")
            search_query = st.text_input(f"Gib einen Suchbegriff für {search_category} ein ({day}):", key=f"search_query_{day}").strip().lower()

            if search_query:
                if search_category == "Frühstück":
                    search_results = data[data['Frühstück'].str.contains(search_query, na=False)]
                elif search_category == "Mittag":
                    search_results = data[data['Mittag'].str.contains(search_query, na=False)]
                elif search_category == "Abend":
                    search_results = data[data['Abend'].str.contains(search_query, na=False)]

                if not search_results.empty:
                    st.write("### Suchergebnisse:")
                    matching_items = search_results[search_category].unique()
                    selected_item = st.selectbox(f"Wähle ein {search_category} aus den Suchergebnissen ({day}):", matching_items, key=f"selected_{search_category}_{day}")

                    if search_category == "Frühstück":
                        st.write("### Passende Mittags- und Abendessen:")
                        matching_lunch = search_results[search_results['Frühstück'] == selected_item]['Mittag'].unique()
                        matching_dinner = search_results[search_results['Frühstück'] == selected_item]['Abend'].unique()

                        selected_lunch = st.selectbox(f"Mittagessen basierend auf deiner Frühstücksauswahl ({day}):", matching_lunch, key=f"lunch_from_search_{day}")
                        selected_dinner = st.selectbox(f"Abendessen basierend auf deiner Frühstücksauswahl ({day}):", matching_dinner, key=f"dinner_from_search_{day}")
                else:
                    st.warning(f"Keine Ergebnisse gefunden für {day}.")

            weekly_plan[day] = {
                'Frühstück': st.session_state.get(f"selected_Frühstück_{day}", None),
                'Mittag': st.session_state.get(f"lunch_from_search_{day}", None),
                'Abend': st.session_state.get(f"dinner_from_search_{day}", None)
            }

    # Wochenplan anzeigen
    if st.button("Wochenplan anzeigen"):
        st.write("## Dein Wochenplan (Druckversion)")
        for day, meals in weekly_plan.items():
            st.write(f"### {day}")
            st.write(f"- **Frühstück:** {meals['Frühstück']}")
            st.write(f"- **Mittag:** {meals['Mittag']}")
            st.write(f"- **Abend:** {meals['Abend']}")

    # Einkaufsliste generieren
    if st.button("Einkaufsliste anzeigen"):
        all_meals = [meal for day_meals in weekly_plan.values() for meal in day_meals.values() if meal]
        shopping_list = pd.Series(all_meals).value_counts()

        st.write("## Einkaufsliste (Druckversion)")
        st.write("### Benötigte Zutaten:")
        for item, count in shopping_list.items():
            st.write(f"- {item} ({count}x)")

if __name__ == "__main__":
    main()
