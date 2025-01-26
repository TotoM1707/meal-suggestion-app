import streamlit as st
import pandas as pd
import os

# Load the data
file_path = 'C:/Mira/LEMME_Chat_Translated_Manual_DE.xlsx'
if not os.path.exists(file_path):
    st.error("Die Datei wurde nicht gefunden. Bitte stellen Sie sicher, dass sich die Datei unter 'C:/Mira/LEMME_Chat_Translated_Manual_DE.xlsx' befindet.")
    st.stop()

try:
    data = pd.read_excel(file_path, sheet_name='Sheet1')
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
    breakfast_options = sorted(data['Frühstück'].unique())
    if not breakfast_options:
        st.error("Keine Frühstücksoptionen gefunden. Bitte überprüfen Sie die Daten im Excel-Dokument.")
        st.stop()

    selected_breakfast = st.selectbox("Wähle dein Frühstück:", breakfast_options)

    # Filter und passende Mahlzeiten anzeigen
    if selected_breakfast:
        st.write(f"Gewähltes Frühstück: {selected_breakfast}")  # Debugging-Ausgabe
        matching_meals = data[data['Frühstück'] == selected_breakfast]

        if not matching_meals.empty:
            lunch = matching_meals['Mittag'].values[0]
            dinner = matching_meals['Abend'].values[0]

            st.write("### Passende Mahlzeiten:")
            st.write(f"**Mittag:** {lunch}")
            st.write(f"**Abend:** {dinner}")
        else:
            st.write("Keine passenden Mahlzeiten gefunden. Bitte überprüfen Sie die Eingabedaten.")

if __name__ == "__main__":
    main()
