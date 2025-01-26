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
    st.write("Wähle ein Frühstück aus, um passende Gerichte für Mittag und Abend anzuzeigen.")

    # Frühstücksauswahl
    search_query = st.text_input("Suche nach Frühstücksoptionen:").strip().lower()
    if search_query:
        filtered_options = data[data['Frühstück'].str.contains(search_query, na=False)]['Frühstück'].unique()
    else:
        filtered_options = data['Frühstück'].unique()

    breakfast_options = sorted(filtered_options)
    if not breakfast_options:
        st.error("Keine passenden Frühstücksoptionen gefunden. Bitte ändern Sie Ihre Suche.")
        return

    selected_breakfast = st.selectbox("Wähle dein Frühstück:", breakfast_options)

    # Filter und passende Mahlzeiten anzeigen
    if selected_breakfast:
        st.write(f"Gewähltes Frühstück: {selected_breakfast}")  # Debugging-Ausgabe
        matching_meals = data[data['Frühstück'] == selected_breakfast]

        if not matching_meals.empty:
            lunch_options = matching_meals['Mittag'].unique()
            dinner_options = matching_meals['Abend'].unique()

            st.write("### Passende Mahlzeiten:")
            st.write("**Mittagsoptionen:**")
            for lunch in lunch_options:
                st.write(f"- {lunch}")

            st.write("**Abendoptionen:**")
            for dinner in dinner_options:
                st.write(f"- {dinner}")
        else:
            st.write("Keine passenden Mahlzeiten gefunden. Bitte überprüfen Sie die Eingabedaten.")

if __name__ == "__main__":
    main()
