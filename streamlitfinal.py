import pymysql
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")
web = option_menu(
    menu_title="Quickride",
    options=["Home", "📍Find Your Way"],
    icons=["house", "info-circle"],
    orientation="horizontal"
)

st.markdown(
    """
    <style>
        /* Custom styling */
        body { background-color: #F0F4F8; font-family: 'Arial', sans-serif; }
        h1 { text-align: center; color: #E92421; font-size: 48px; font-weight: bold; }
        .header-home { font-size: 42px; color: #E92421; font-weight: bold; }
        .header-filter { font-size: 36px; color: #E92421; font-weight: bold; }
        .welcome { text-align: center; font-size: 36px; color: #E92421; font-weight: bold; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True
)

def create_connection():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="PRANITHAA17@",  
            database="REDBUS_DETAILS"
        )
    except pymysql.Error as err:
        st.error(f"Database connection error: {err}")
        return None


# Fetch data from MySQL database based on query


def load_data(query, params=None):
    conn = create_connection()
    if conn:
        print("connection established")
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(rows, columns=columns)
        except pymysql.Error as err:
            st.error(f"Data loading error: {err}")

    return pd.DataFrame()


# Convert times to 24-hour format 
def time_to_24hr(time_input):
    return time_input.strftime('%H:%M') if time_input else None

# Filter data based on user input
def filter_data(state, route, bus_type, price_range, star_rating_range, seat_availability, Start_time=None, End_time=None):
    query = "SELECT * FROM REDBUS_DETAILS WHERE 1=1"
    params = []

    # State filter
    if state:
        query += " AND state = %s"
        params.append(state)

    # Route filter
    if route:
        query += " AND route_name IN (%s)" % ','.join(['%s'] * len(route))
        params.extend(route)
          # Bus type filter
    if bus_type == 'A/C':
        query += " AND bus_type = %s"
        params.append('A/C')
    elif bus_type == 'NON A/C':
        query += " AND bus_type = %s"
        params.append('NON A/C')
    else:
        query += " AND bus_type NOT LIKE %s AND bus_type NOT LIKE %s"
        params.extend(['%Sleeper%', '%Semi-Sleeper%'])

    # Price range filter
    query += " AND price BETWEEN %s AND %s"
    params.extend(price_range)

    # Star rating filter
    if star_rating_range[0] > 0.0 or star_rating_range[1] < 5.0:
        query += " AND star_rating BETWEEN %s AND %s"
        params.extend(star_rating_range)

    # Seat availability filter
    if seat_availability > 0:
        query += " AND seats_available >= %s"
        params.append(seat_availability)

         # Time filters
    if Start_time is not None:
        query += " AND Start_time >= %s"
        params.append(Start_time)
    if End_time is not None:
        query += " AND End_time <= %s"
        params.append(End_time)

    return query, params

# Home Tab
if web == "Home":
    st.title("🚍 Welcome to REDBUS!")
    st.write("""
        RedBus is your go-to platform for booking bus tickets online.
        Explore our user-friendly interface to find, compare, and book buses from various operators.
    """)
    st.header("Key Features")
    st.write("- **Wide Range of Options:** Choose from numerous bus operators and routes.")
    st.write("- **Easy Booking:** Simple and quick booking process.")
    st.write("- **Secure Payments:** Multiple secure payment options for your convenience.")
    st.write("- **Customer Support:** 24/7 support for any queries or issues.")
    # Filtered Data Tab
if web == "📍Find Your Way":
    st.markdown("<h1 style='color: green; font-weight: bold;'>Bus Data</h1>", unsafe_allow_html=True)

    # Sidebar filters
    st.sidebar.header("Find Your Ideal Bus Route!")
    states = load_data("SELECT DISTINCT state FROM REDBUS_DETAILS")
    state_filter = st.sidebar.selectbox("State", states['state'].tolist() if not states.empty else [])

    # Route Name Filter (filtered based on the selected state)
    route_filter = []
    if state_filter:
        routes = load_data("SELECT DISTINCT route_name FROM REDBUS_DETAILS WHERE state = %s", [state_filter])
        route_filter = st.sidebar.multiselect("Route Name", routes['route_name'].tolist() if not routes.empty else [])

    bus_type_filter = st.sidebar.radio("Bus Type", ['A/C', 'NON A/C', 'others'])

    price_data = load_data("SELECT MIN(price), MAX(price) FROM REDBUS_DETAILS WHERE state = %s", [state_filter])
    if not price_data.empty:
       price_min, price_max = price_data.iloc[0]
       price_min = price_min if price_min is not None else 0.0
       price_max = price_max if price_max is not None else 1000.0  # Set a reasonable default max price
    else:
       price_min, price_max = 0.0, 1000.0  # Default range if no data is found

    price_range_filter = st.sidebar.slider("Price Range", float(price_min), float(price_max), (float(price_min), float(price_max)))

    Rating_range_filter = st.sidebar.slider("Ratings Range", 0.0, 5.0, (0.0, 5.0))
    seat_availability_filter = st.sidebar.slider("Minimum Seats Available", 0, 50, 0)
    Start_time_filter = st.sidebar.time_input("Start Time", None)
    End_time_filter = st.sidebar.time_input("End Time", None)

    query, params = filter_data(state_filter, route_filter, bus_type_filter, price_range_filter, Rating_range_filter, seat_availability_filter, time_to_24hr(Start_time_filter), time_to_24hr(End_time_filter))
    filtered_data = load_data(query, params)

    st.write("### Filtered Bus Data")
    if not filtered_data.empty:
        st.dataframe(filtered_data)
    else:
        st.write("No results found for the selected filters.")


