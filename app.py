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
    st.title("Mahlzeit-Empfehlungen")
    st.write("Wähle ein Frühstück, Mittag oder Abend aus, um die fehlenden Mahlzeiten anzuzeigen.")

    # Auswahloptionen
    search_category = st.radio("Wähle die Kategorie für die Suche:", ("Frühstück", "Mittag", "Abend"))
    search_query = st.text_input(f"Suche nach {search_category}-Optionen:").strip().lower()

    if search_category == "Frühstück":
        filtered_options = data[data['Frühstück'].str.contains(search_query, na=False)]['Frühstück'].unique() if search_query else data['Frühstück'].unique()
    elif search_category == "Mittag":
        filtered_options = data[data['Mittag'].str.contains(search_query, na=False)]['Mittag'].unique() if search_query else data['Mittag'].unique()
    elif search_category == "Abend":
        filtered_options = data[data['Abend'].str.contains(search_query, na=False)]['Abend'].unique() if search_query else data['Abend'].unique()

    options = sorted(filtered_options)
    if not options:
        st.error(f"Keine passenden {search_category}-Optionen gefunden. Bitte ändern Sie Ihre Suche.")
        return

    selected_option = st.selectbox(f"Wähle dein {search_category}:", options)

    # Filter und fehlende Mahlzeiten anzeigen
    if selected_option:
        st.write(f"Gewähltes {search_category}: {selected_option}")  # Debugging-Ausgabe

        if search_category == "Frühstück":
            matching_meals = data[data['Frühstück'] == selected_option]
        elif search_category == "Mittag":
            matching_meals = data[data['Mittag'] == selected_option]
        elif search_category == "Abend":
            matching_meals = data[data['Abend'] == selected_option]

        if not matching_meals.empty:
            breakfast_options = matching_meals['Frühstück'].unique()
            lunch_options = matching_meals['Mittag'].unique()
            dinner_options = matching_meals['Abend'].unique()

            st.write("### Passende Mahlzeiten:")
            if search_category != "Frühstück":
                st.write("**Frühstücksoptionen:**")
                for breakfast in breakfast_options:
                    st.write(f"- {breakfast}")

            if search_category != "Mittag":
                st.write("**Mittagsoptionen:**")
                for lunch in lunch_options:
                    st.write(f"- {lunch}")

            if search_category != "Abend":
                st.write("**Abendoptionen:**")
                for dinner in dinner_options:
                    st.write(f"- {dinner}")
        else:
            st.write("Keine passenden Mahlzeiten gefunden. Bitte überprüfen Sie die Eingabedaten.")

if __name__ == "__main__":
    main()

