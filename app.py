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

            # Auswahl der Startmahlzeit
            starting_meal = st.radio(f"Mit welcher Mahlzeit möchtest du für {day} beginnen?", ("Frühstück", "Mittag", "Abend"), key=f"starting_meal_{day}")

            # Frühstücksauswahl
            selected_breakfast = None
            selected_lunch = None
            selected_dinner = None

            if starting_meal == "Frühstück":
                selected_breakfast = st.selectbox(f"Wähle ein Frühstück für {day}", data['Frühstück'].unique(), key=f"breakfast_{day}")
                matching_lunch = data[data['Frühstück'] == selected_breakfast]['Mittag'].unique()
                selected_lunch = st.selectbox(f"Mittagessen basierend auf deiner Frühstücksauswahl ({day}):", matching_lunch, key=f"lunch_{day}")
                matching_dinner = data[(data['Frühstück'] == selected_breakfast) & (data['Mittag'] == selected_lunch)]['Abend'].unique()
                selected_dinner = st.selectbox(f"Abendessen basierend auf deiner Frühstücks- und Mittagsauswahl ({day}):", matching_dinner, key=f"dinner_{day}")
            elif starting_meal == "Mittag":
                selected_lunch = st.selectbox(f"Wähle ein Mittagessen für {day}", data['Mittag'].unique(), key=f"lunch_{day}")
                matching_breakfast = data[data['Mittag'] == selected_lunch]['Frühstück'].unique()
                selected_breakfast = st.selectbox(f"Frühstück basierend auf deiner Mittagsauswahl ({day}):", matching_breakfast, key=f"breakfast_{day}")
                matching_dinner = data[(data['Mittag'] == selected_lunch) & (data['Frühstück'] == selected_breakfast)]['Abend'].unique()
                selected_dinner = st.selectbox(f"Abendessen basierend auf deiner Frühstücks- und Mittagsauswahl ({day}):", matching_dinner, key=f"dinner_{day}")
            elif starting_meal == "Abend":
                selected_dinner = st.selectbox(f"Wähle ein Abendessen für {day}", data['Abend'].unique(), key=f"dinner_{day}")
                matching_lunch = data[data['Abend'] == selected_dinner]['Mittag'].unique()
                selected_lunch = st.selectbox(f"Mittagessen basierend auf deiner Abendauswahl ({day}):", matching_lunch, key=f"lunch_{day}")
                matching_breakfast = data[(data['Abend'] == selected_dinner) & (data['Mittag'] == selected_lunch)]['Frühstück'].unique()
                selected_breakfast = st.selectbox(f"Frühstück basierend auf deiner Mittag- und Abendauswahl ({day}):", matching_breakfast, key=f"breakfast_{day}")

            weekly_plan[day] = {
                'Frühstück': selected_breakfast,
                'Mittag': selected_lunch,
                'Abend': selected_dinner
            }

    # Warnung, wenn eine Mahlzeit mehr als 2-mal ausgewählt wurde
    all_selected_meals = [meal for day_meals in weekly_plan.values() for meal in day_meals.values() if meal]
    meal_counts = pd.Series(all_selected_meals).value_counts()
    repeated_meals = meal_counts[meal_counts > 2]
    if not repeated_meals.empty:
        st.warning("Folgende Mahlzeiten wurden mehr als 2-mal in der Woche ausgewählt und sollten reduziert werden:")
        for meal, count in repeated_meals.items():
            st.write(f"- {meal}: {count}x")

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
        shopping_list = meal_counts
        st.write("## Einkaufsliste (Druckversion)")
        st.write("### Benötigte Zutaten:")
        for item, count in shopping_list.items():
            st.write(f"- {item} ({count}x)")

if __name__ == "__main__":
    main()
