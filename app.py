# Save this as construction_schedule_app.py and run with: streamlit run construction_schedule_app.py

import streamlit as st
import google.generativeai as genai
from datetime import datetime
import math

# Configure Gemini API with your provided key
genai.configure(api_key="AIzaSyDHYnt70EfiQ1uKWxW-oSKk92xLG7UsQgI")

# Function to list available models
def list_available_models():
    try:
        models = genai.list_models()
        supported = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                supported.append(model.name)
        return supported
    except Exception as e:
        return f"Error listing models: {str(e)}"

# Function to convert date to Excel-style serial date
def date_to_serial(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        base_date = datetime(1899, 12, 30)  # Excel serial date base
        serial_date = (date_obj - base_date).days
        return serial_date
    except ValueError:
        return None

# List available models early to select a valid one
available_models = list_available_models()
st.sidebar.write("Available Models:")
st.sidebar.write(available_models)

# Select a model from available ones (default to first supported if possible)
if available_models:
    model_name = st.selectbox("Select Model", available_models, index=0)
    try:
        model = genai.GenerativeModel(model_name)
    except Exception:
        model = None
        st.error(f"Selected model '{model_name}' not usable.")
else:
    model = None
    st.error("No supported models available. Check API key, enable Generative Language API, or region restrictions.")

# Example schedule as a string (from the provided document)
example_schedule = """Column Names:
Phase, Level, Activity / Component, Start Date, End Date, Duration, Key Notes

Row 1:
Phase: 1. Site Preparation
Level: —
Activity / Component: Clearing, survey, layout, temporary utilities
Start Date: {start_date_str}
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Includes barricading, soil testing

Row 2:
Phase: Plinth
Level: —
Activity / Component: Heavy and stable base for Building
Start Date: end date of Site Preparation
End Date: Write the end date Depending on Activity / Component column
Duration: —
Key Notes: —

Row 3:
Phase: 2. Excavation & Raft
Level: B1 Basement
Activity / Component: Deep excavation, retaining walls, raft PCC & waterproofing
Start Date: end date of Site Preparation
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: 1-level excavation with dewatering

Row 4:
Phase: 3. RCC Superstructure
Level: B1 Basement
Activity / Component: Raft → slab
Start Date: end date of Site Preparation
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Raft PCC, waterproofing and B1 slab (overlaps excavation)

Row 5:
Phase: 3. RCC Superstructure
Level: Keep on increasing basement based on {num_basements}
Activity / Component: Columns → slab
Start Date: end date of RCC Superstructure
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: —

Row 6:
Phase: 3. RCC Superstructure
Level: Ground Floor
Activity / Component: Columns → slab
Start Date: end date of RCC Superstructure
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Podium + entry level

Row 7:
Phase: 3. RCC Superstructure
Level: 1st Floor
Activity / Component: Columns → slab
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Begin MEP embedments

Row 8:
Phase: 3. RCC Superstructure
Level: Keep on increasing floors based on num_floors_above based on {num_basements}
Activity / Component: Columns → slab
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Structural cycle stabilized

Row 9:
Phase: 3. RCC Superstructure
Level: Terrace / Roof Slab
Activity / Component: Roof slab & parapet
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: End of structural cycle

Row 10:
Phase: 4. Masonry & Plastering
Level: B1, GF – max floor
Activity / Component: Blockwork, lintels, internal & external plaster
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Start two floors below RCC front

Row 11:
Phase: 5. Basement Services
Level: B1 Basement
Activity / Component: Waterproofing, ramps, driveways, STP, sump
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Coordinate with RCC progress

Row 12:
Phase: 6. Electrical / Plumbing (1st Fix)
Level: All Levels
Activity / Component: Concealed conduits, sleeves, piping
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Parallel with masonry

Row 13:
Phase: 7. Flooring & Tiling
Level: GF – max floor
Activity / Component: Screed, tiles, skirting, toilets
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Start after plastering floor-wise

Row 14:
Phase: 8. Waterproofing (Terrace & Wet Areas)
Level: Roof + B1 + Wet areas
Activity / Component: APP membrane, toilets, balconies
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Critical quality stage

Row 15:
Phase: 9. Painting & Finishes
Level: B1, GF – max floor
Activity / Component: Putty, primer, internal/external paint
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Interior & façade

Row 16:
Phase: 10. Fixtures & Fit-outs
Level: All Levels
Activity / Component: Doors, windows, sanitary, lighting
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Overlap with painting

Row 17:
Phase: 11. External Development
Level: Site / Podium
Activity / Component: Compound wall, paving, drainage, landscaping
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Coordinate with façade

Row 18:
Phase: 12. Testing & Handover
Level: Entire Project
Activity / Component: Lift, fire, STP, electrical, final cleaning
Start Date: Based on progreess of prior construction
End Date: Write the end date Depending on Activity / Component column
Duration: Calculate total days rquired to fininsh this phase based on Start date and End date
Key Notes: Occupancy & completion certificate
"""

# System prompt for Gemini
system_prompt_template = """
You are an expert in generating construction schedules for buildings. Use the following example schedule as a template to create a new one. Adjust the number of basements, floors, durations, and other details based on the inputs provided. Assume the builtup area per floor is the same for basements and above-ground floors. Calculate the number of above-ground floors as (total_builtup_area / builtup_area_per_floor) - number_of_basements, assuming integer values.

Structure the output as a markdown table with columns: Phase, Level, Activity / Component, Start Date, End Date, Duration, Key Notes.
Make sure the schedule is realistic, with overlapping phases where appropriate, similar to the example.
Use data data type for Start Date and End Date, starting from the provided project start date {start_date_serial} (equivalent to {start_date_str} in YYYY-MM-DD format).
Add a summary section at the end, including total project duration, key milestones, and any assumptions made.

Refer to Example Schedule just as an exaple for structure make sure to allocate time to each step based on the total area and number of floors and number of basements and other factors.:
{example_schedule}

Now, generate a schedule for:
- Total Builtup Area: {total_area} sqft
- Number of Basements: {num_basements}
- Builtup Area per Floor: {area_per_floor} sqft
- Calculated Total Levels: {total_levels}
- Calculated Above-Ground Floors: {num_floors_above} (including ground floor)
- Project Start Date: {start_date_str} (serial date: {start_date_serial})
"""

# Streamlit app
st.title("Construction Schedule Generator")

total_area = st.number_input("Total Builtup Area (sqft)", min_value=0.0, value=10000.0)
num_basements = st.number_input("Number of Basements", min_value=0, value=2, step=1)
area_per_floor = st.number_input("Builtup Area per Floor (sqft)", min_value=0.0, value=2000.0)
start_date = st.date_input("Project Start Date", value=datetime(2025, 1, 1))

if area_per_floor > 0 and total_area > 0:
    leveltotal = total_area / area_per_floor
    total_levels = math.floor(leveltotal)
    num_floors_above = total_levels - num_basements
    st.write(f"Calculated Total Levels: {total_levels}")
    st.write(f"Calculated Above-Ground Floors: {num_floors_above} (including ground floor)")
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    start_date_serial = date_to_serial(start_date_str)
    
    if start_date_serial is None:
        st.error("Invalid start date format. Please use YYYY-MM-DD.")
    elif total_levels != int(total_levels) or num_floors_above != int(num_floors_above):
        st.error("Total area must be divisible by area per floor to get integer levels.")
    elif model is None:
        st.error("Cannot generate schedule: No valid model available. See available models in sidebar.")
    else:
        if st.button("Generate Construction Schedule"):
            prompt = system_prompt_template.format(
                example_schedule=example_schedule,
                total_area=total_area,
                num_basements=num_basements,
                area_per_floor=area_per_floor,
                total_levels=int(total_levels),
                num_floors_above=int(num_floors_above),
                start_date_str=start_date_str,
                start_date_serial=start_date_serial
            )
            try:
                response = model.generate_content(prompt)
                st.markdown("### Generated Construction Schedule")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating schedule: {str(e)}")
                st.write("Try a different model from the sidebar or check your API setup.")
else:
    st.warning("Please enter valid positive values for all inputs.")