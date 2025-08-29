import streamlit as st
import pandas as pd

# ==========================
# Streamlit Page Config
# ==========================
st.set_page_config(page_title="Seat Allocation Dashboard", page_icon="🎓", layout="centered")

# ==========================
# Load Data
# ==========================
@st.cache_data
def load_data():
    try:
        students_df = pd.read_csv("students.csv")
        seats_df = pd.read_csv("seat.csv")
        preferences_df = pd.read_csv("preference.csv")
        return students_df, seats_df, preferences_df
    except FileNotFoundError as e:
        st.error(f"Error: {e}. Make sure the required CSV files (students.csv, seat.csv, preference.csv) are in the same directory.")
        return None, None, None

students_df, seats_df, preferences_df = load_data()

# ==========================
# Seat Allocation Function
# ==========================
def allocate_seats():
    # Ensure dataframes are loaded before proceeding
    if students_df is None or seats_df is None or preferences_df is None:
        return pd.DataFrame() # Return empty dataframe if data loading failed

    students_sorted = students_df.sort_values(by="Rank")
    seat_columns = ["SC", "SC-CC", "ST", "BC", "Minority", "OC"]

    seats_availability = {}
    for _, row in seats_df.iterrows():
        college_id = row["CollegeID"]
        seats_availability[college_id] = {caste: row[caste] for caste in seat_columns}

    allocation_results = []
    for _, student in students_sorted.iterrows():
        student_id = student["UniqueID"]
        caste = student["Caste"]
        gender = student["Gender"]
        name = student["Name"]
        rank = student["Rank"]

        student_prefs = preferences_df[preferences_df["UniqueID"] == student_id].sort_values(by="PrefNumber")
        allotted = False

        for _, pref in student_prefs.iterrows():
            college_id = pref["CollegeID"]

            # Check if the caste column exists in seats_availability for the college
            if college_id in seats_availability and caste in seats_availability[college_id] and seats_availability[college_id][caste] > 0:
                seats_availability[college_id][caste] -= 1
                college_name = seats_df.loc[seats_df["CollegeID"] == college_id, "Institution"].values[0]
                allocation_results.append([student_id, name, gender, caste, rank, college_id, college_name, pref["PrefNumber"]])
                allotted = True
                break
            # Fallback to OC category if specific caste seat is not available
            elif college_id in seats_availability and seats_availability[college_id]["OC"] > 0:
                 seats_availability[college_id]["OC"] -= 1
                 college_name = seats_df.loc[seats_df["CollegeID"] == college_id, "Institution"].values[0]
                 allocation_results.append([student_id, name, gender, caste, rank, college_id, f"{college_name} (OC)", pref["PrefNumber"]])
                 allotted = True
                 break


        if not allotted:
            allocation_results.append([student_id, name, gender, caste, rank, "No College Available", "-", None])

    return pd.DataFrame(allocation_results,
                        columns=["UniqueID", "Name", "Gender", "Caste", "Rank", "CollegeID", "Institution", "PrefNumber"])

allocation_df = allocate_seats()

# ==========================
# Streamlit UI
# ==========================
st.markdown(
    """
    <style>
    /* General body styling */
    body {
        background-color: #f0f2f6;
    }
    /* Header styling */
    .header {
        text-align: center;
        background-color: #FFA500; /* New dark blue background color */
        color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-family: 'Arial', sans-serif;
    }
    /* Custom button style */
    div.stButton > button:first-child {
        background-color: #007BFF; /* New professional blue color */
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 12px 30px;
        border-radius: 10px;
        border: none;
        transition: 0.3s ease-in-out;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    div.stButton > button:first-child:hover {
        background-color: #0056b3; /* Darker blue on hover */
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    /* Input box styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #ced4da;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown("<h1 class='header'>🎓 Seat Allocation Result!</h1>", unsafe_allow_html=True)


st.write("") # Adding some space
st.info("Enter your **Unique ID** below to check your college allotment.")

unique_id_input = st.text_input("🔑 **Enter your Unique ID**", placeholder="e.g., 1115619330")

# Initialize variables to hold the result outside the button's scope
result_to_display = None
error_message = None

# === Center the button ===
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Get Result", key="get_result"):
        # Only proceed if data is loaded
        if allocation_df.empty and students_df is None:
            st.stop()

        if not unique_id_input.strip():
            st.warning("⚠️ Please enter a valid Unique ID.")
        else:
            try:
                # Ensure input is treated as a number for matching
                search_id = int(unique_id_input.strip())
                result = allocation_df[allocation_df["UniqueID"] == search_id]
                if result.empty:
                    error_message = "❌ No record found for this Unique ID. Please check and try again."
                else:
                    result_to_display = result
            except ValueError:
                st.error("❌ Invalid Unique ID. Please enter a numeric ID.")

# === Display the result or error message outside the columns to allow for wider display ===
if error_message:
    st.error(error_message)

if result_to_display is not None:
    st.success("✅ **Result Found!**")
    st.dataframe(result_to_display.style.set_properties(**{'text-align': 'left'}).set_table_styles(
        [dict(selector='th', props=[('text-align', 'left')])]
    ), use_container_width=True)




