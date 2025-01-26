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

    # Buttons für Wochenplan und Einkaufsliste oben anzeigen
    col1, col2 = st.columns(2)
    with col1:
        show_plan = st.button("Wochenplan anzeigen")
    with col2:
        show_list = st.button("Einkaufsliste anzeigen")

    tabs = st.tabs(days)

    # Mahlzeitzählung für Warnungen
    all_selected_meals = []

    for day, tab in zip(days, tabs):
        with tab:
            st.write(f"### {day}")

            # Auswahl für Frühstück
            breakfast = st.selectbox(f"Frühstück für {day}", data['Frühstück'].unique(), key=f"breakfast_{day}")
            matching_lunch = data[data['Frühstück'] == breakfast]['Mittag'].unique()
            matching_dinner = data[data['Frühstück'] == breakfast]['Abend'].unique()

            # Auswahl für Mittagessen
            lunch = st.selectbox(f"Mittagessen für {day}", matching_lunch, key=f"lunch_{day}")
            matching_dinner = data[(data['Frühstück'] == breakfast) & (data['Mittag'] == lunch)]['Abend'].unique()

            # Auswahl für Abendessen
            dinner = st.selectbox(f"Abendessen für {day}", matching_dinner, key=f"dinner_{day}")

            weekly_plan[day] = {
                'Frühstück': breakfast,
                'Mittag': lunch,
                'Abend': dinner
            }

            # Sammeln der Mahlzeiten für Warnungen
            all_selected_meals.extend([breakfast, lunch, dinner])

            # Warnung, wenn eine Mahlzeit mehr als 2-mal ausgewählt wurde
            meal_counts = pd.Series(all_selected_meals).value_counts()
            repeated_meals = meal_counts[meal_counts > 2]
            if not repeated_meals.empty:
                st.warning("Folgende Mahlzeiten wurden mehr als 2-mal ausgewählt:")
                for meal, count in repeated_meals.items():
                    st.write(f"- {meal}: {count}x")

    if show_plan:
        st.write("## Dein Wochenplan (Druckversion)")
        for day, meals in weekly_plan.items():
            st.write(f"### {day}")
            st.write(f"- **Frühstück:** {meals['Frühstück']}")
            st.write(f"- **Mittag:** {meals['Mittag']}")
            st.write(f"- **Abend:** {meals['Abend']}")

    if show_list:
        st.write("## Einkaufsliste (Druckversion)")
        shopping_list = pd.Series(all_selected_meals).value_counts()
        st.write("### Benötigte Zutaten:")
        for item, count in shopping_list.items():
            st.write(f"- {item} ({count}x)")

if __name__ == "__main__":
    main()
