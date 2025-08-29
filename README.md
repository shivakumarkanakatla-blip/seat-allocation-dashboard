# 🎓 Seat Allocation Dashboard

A Streamlit app for student seat allocation based on **rank, caste, and preferences**.

## 🚀 Features
- Students enter **Unique ID** to check allocation
- Seat allocation logic:
  - Sorted by rank
  - Caste-wise seat availability
  - Preference order checked
- Admins can view full allocation list

## 📂 Files
- `students.csv` → Student details (UniqueID, Name, Gender, Caste, Rank)
- `seat.csv` → College seat availability (category-wise)
- `preference.csv` → Student preferences (CollegeID, PrefNumber, UniqueID)

## 🛠️ Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
