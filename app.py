import streamlit as st
import pandas as pd
import os
import random

# Load the data
file_path = 'LEMME_Chat_Translated_Manual_DE.xlsx'
if not os.path.exists(file_path):
    st.error("Die Datei wurde nicht gefunden. Bitte stellen Sie sicher, dass sich die Datei unter 'LEMME_Chat_Translated_Manual_DE.xlsx' befindet.")
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

# Memory for previously used meals
used_meals = set()

# Streamlit App
def main():
    st.markdown("<h2 style='font-size: 20px;'>Mahlzeit-Empfehlungen mit Wochenplan und Einkaufsliste</h2>", unsafe_allow_html=True)

    # Seiten-Navigation
    page = st.sidebar.radio("Navigation", ["Startseite", "Wochenplan", "Monatsplan", "Einkaufsliste"])

    if page == "Startseite":
        display_start_page()
    elif page == "Wochenplan":
        display_weekly_plan()
    elif page == "Monatsplan":
        display_monthly_plan()
    elif page == "Einkaufsliste":
        display_shopping_list()


def display_start_page():
    st.write("## Willkommen zur Mahlzeitenplanung")
    st.write("Nutzen Sie das Menü auf der linken Seite, um zwischen Wochen-, Monatsplänen und der Einkaufsliste zu wechseln.")

    # Suchfunktion hinzufügen
    st.write("### Mahlzeit suchen")
    meal_type = st.selectbox("Wähle die Mahlzeit aus", ["Frühstück", "Mittag", "Abend"], key="meal_type_search")
    if meal_type == "Frühstück":
        search_results = data['Frühstück'].unique()
        selected_meal = st.selectbox("Verfügbare Frühstücke", search_results, key="selected_breakfast_search")
        matching_lunch = data[data['Frühstück'] == selected_meal]['Mittag'].unique()
        matching_dinner = data[data['Frühstück'] == selected_meal]['Abend'].unique()

        st.selectbox("Passende Mittagessen", matching_lunch, key="matching_lunch_search")
        st.selectbox("Passende Abendessen", matching_dinner, key="matching_dinner_search")

    elif meal_type == "Mittag":
        search_results = data['Mittag'].unique()
        selected_meal = st.selectbox("Verfügbare Mittagessen", search_results, key="selected_lunch_search")
        matching_breakfast = data[data['Mittag'] == selected_meal]['Frühstück'].unique()
        matching_dinner = data[data['Mittag'] == selected_meal]['Abend'].unique()

        st.selectbox("Passende Frühstücke", matching_breakfast, key="matching_breakfast_search")
        st.selectbox("Passende Abendessen", matching_dinner, key="matching_dinner_search")

    elif meal_type == "Abend":
        search_results = data['Abend'].unique()
        selected_meal = st.selectbox("Verfügbare Abendessen", search_results, key="selected_dinner_search")
        matching_breakfast = data[data['Abend'] == selected_meal]['Frühstück'].unique()
        matching_lunch = data[data['Abend'] == selected_meal]['Mittag'].unique()

        st.selectbox("Passende Frühstücke", matching_breakfast, key="matching_breakfast_search")
        st.selectbox("Passende Mittagessen", matching_lunch, key="matching_lunch_search")


def display_weekly_plan():
    days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
    auto_plan = {}
    available_meals = data.copy()

    st.write("## Automatischen Wochenplan erstellen")
    for day in days:
        day_plan = {}
        for meal_type in ['Frühstück', 'Mittag', 'Abend']:
            remaining_meals = available_meals[meal_type][~available_meals[meal_type].isin(used_meals)].unique()
            if len(remaining_meals) == 0:
                st.error(f"Nicht genügend verfügbare {meal_type} Optionen für {day}.")
                return

            selected_meal = random.choice(remaining_meals)
            day_plan[meal_type] = selected_meal

            # Mahlzeit als verwendet markieren
            used_meals.add(selected_meal)

            # Sicherstellen, dass maximal 2 Tage hintereinander gleiche Mahlzeiten gewählt werden
            if len(used_meals) > 7:
                used_meals.pop()

        auto_plan[day] = day_plan

    st.write("## Automatisch erstellter Wochenplan")
    for day, meals in auto_plan.items():
        st.write(f"### {day}")
        st.write(f"- **Frühstück:** {meals['Frühstück']}")
        st.write(f"- **Mittag:** {meals['Mittag']}")
        st.write(f"- **Abend:** {meals['Abend']}")

    # Save the weekly plan for the shopping list
    st.session_state['weekly_plan'] = auto_plan


def display_monthly_plan():
    days_in_month = 30
    auto_month_plan = {}
    available_meals = data.copy()

    st.write("## Automatischen Monatsplan erstellen")
    for day in range(1, days_in_month + 1):
        day_plan = {}
        for meal_type in ['Frühstück', 'Mittag', 'Abend']:
            remaining_meals = available_meals[meal_type][~available_meals[meal_type].isin(used_meals)].unique()
            if len(remaining_meals) == 0:
                st.error(f"Nicht genügend verfügbare {meal_type} Optionen für Tag {day}.")
                return

            selected_meal = random.choice(remaining_meals)
            day_plan[meal_type] = selected_meal

            # Mahlzeit als verwendet markieren
            used_meals.add(selected_meal)

            # Sicherstellen, dass maximal 2 Tage hintereinander gleiche Mahlzeiten gewählt werden
            if len(used_meals) > 7:
                used_meals.pop()

        auto_month_plan[f"Tag {day}"] = day_plan

    st.write("## Automatisch erstellter Monatsplan")
    for day, meals in auto_month_plan.items():
        st.write(f"### {day}")
        st.write(f"- **Frühstück:** {meals['Frühstück']}")
        st.write(f"- **Mittag:** {meals['Mittag']}")
        st.write(f"- **Abend:** {meals['Abend']}")

    # Save the monthly plan for the shopping list
    st.session_state['monthly_plan'] = auto_month_plan


def display_shopping_list():
    st.write("## Einkaufsliste")

    # Collect all meals from weekly and monthly plans
    weekly_plan = st.session_state.get('weekly_plan', {})
    monthly_plan = st.session_state.get('monthly_plan', {})

    all_meals = []
    for plan in [weekly_plan, monthly_plan]:
        for day, meals in plan.items():
            all_meals.extend(meals.values())

    if not all_meals:
        st.write("Es wurden noch keine Pläne erstellt. Bitte erstellen Sie zuerst einen Wochen- oder Monatsplan.")
        return

    shopping_list = pd.Series(all_meals).value_counts()

    st.write("### Benötigte Zutaten:")
    for item, count in shopping_list.items():
        st.write(f"- {item} ({count}x)")

if __name__ == "__main__":
    main()
