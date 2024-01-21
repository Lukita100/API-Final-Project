import streamlit as st
import requests



if 'headers' not in st.session_state:
    st.session_state.headers = {}
if 'state_button' not in st.session_state:
    st.session_state.state_button=False
if 'submitted_button' not in st.session_state:
    st.session_state.submitted_button=False
if 'update_button' not in st.session_state:
    st.session_state.update_button=False
if 'submit' not in st.session_state:
    st.session_state.submit=False    
    

# Streamlit Interface
st.title('Tennis Grand Slams Champions')

# Function to handle user signup
def signup(username, password):
    try:
        response = requests.post("http://127.0.0.1:5000/signup", json={"username": username, "password": password})
        response.raise_for_status()  # Raise an HTTPError for bad responses
        st.success('Signup successful! You can now login.')
    except requests.exceptions.RequestException as e:
        st.warning(f"Error during signup: {e}")

# Function to handle user login and retrieve authentication token
def login(username, password):
    try:
        response = requests.post("http://127.0.0.1:5000/login", json={"username": username, "password": password})
        response.raise_for_status()  # Raise an HTTPError for bad responses
        token = response.json().get('access_token')
        #print(token)
        st.session_state.headers ={"Authorization": f"Bearer {token}"} 
        #print (st.session_state.headers)
        return st.session_state.headers
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error during login: {e}")
        return None
        
# Signup and Login sections side by side
col1, col2 = st.columns(2)
    
# Signup section
with col1:
    st.header('Signup')
    username_signup = st.text_input('Username/Email')
    password_signup = st.text_input('Password', type='password')
    signup_button = st.button('Signup')

    if signup_button:
        signup(username_signup, password_signup)

# Login section
with col2:
    st.header('Login')
    username = st.text_input(' Username/ Email')
    password = st.text_input(' Password', type='password')
    login_button = st.button('Login')

    if login_button:
        headers = login(username, password)
        if headers:
            st.success('Login successful!')
        else:
            st.warning('Invalid credentials. Please try again.')

# Function to check if the user is logged in
def is_logged_in():
    return st.session_state.headers is not None and 'Authorization' in st.session_state.headers          

# Display the sections only if the user is logged in
if is_logged_in():
    # Function to retrieve titles from the Flask API
    def get_titles(headers):
        response = requests.get('http://127.0.0.1:5000/titles',headers=headers)
        data = response.json()
        return data

    # Function to retrieve the number of titles per player from the Flask API
    def get_titles_by_player(player_name,headers):
        response = requests.get(f'http://127.0.0.1:5000/titles/{player_name}',headers=headers)
        data = response.json()
        return data

    # Function to retrieve champions from the Flask API
    def get_champions(headers):
        response = requests.get("http://localhost:5000/champions", headers=headers)
        data = response.json()
        return data

    # Function to retrieve champions by year from the Flask API
    def get_champions_by_year(year,headers):
        response = requests.get(f'http://127.0.0.1:5000/champions/{year}',headers=headers)
        data = response.json()
        return data

    # Function to add a new champion using the Flask API
    def add_champion(year, australian_open, roland_garros, wimbledon, us_open, headers):
        data = {
            "Year": year,
            "Australian_Open": australian_open,
            "Roland_Garros": roland_garros,
            "Wimbledon": wimbledon,
            "US_Open": us_open
        }
        response = requests.post("http://127.0.0.1:5000/champions", json=data, headers=headers)
        return response.json()

    # Function to update a champion using the Flask API
    def update_champion(year, update_data, headers):
        response = requests.put(f'http://127.0.0.1:5000/champions/{year}', json=update_data, headers=headers)
        return response.json()

    # Function to delete a champion using the Flask API
    def delete_champion(year, headers):
        response = requests.delete(f'http://127.0.0.1:5000/champions/{year}', headers=headers)
        return response.json()


    # Checkbox to toggle visibility of the list
    show_titles = st.checkbox('Display all Titles')
    show_champions = st.checkbox('Display Champions by Year')  # Add a checkbox for champions

    if show_titles:
        st.header('All Titles')
        titles = get_titles(st.session_state.headers)
        st.write(titles)

    if show_champions:  # Display champions if the checkbox is selected
        st.header('All Champions')
        champions = get_champions(st.session_state.headers)
        st.write(champions)
        

    #Section to retrieve the number of titles per player
    st.header('Player Career Titles:')
    player_name = st.text_input('Player Name:')
    if player_name:
        result = get_titles_by_player(player_name,st.session_state.headers)
        if len(result) == 3:
            st.write(f"Number of Grand Slam Titles for {result['database_player']}: {result['number_of_titles']}")
        else:
            st.write("Player does not exist! Please enter a valid name.")    
                
    # Section to retrieve champions by year
    st.header('Champions by Year:')
    champion_year = st.text_input('Enter Year:')
    if champion_year:
        champion_result = get_champions_by_year(int(champion_year),st.session_state.headers)
        print(champion_result)
        #if 'Champion' in champion_result:
        st.write(f"Champions for {champion_result['Year']}:")
        for key, value in champion_result.items():
            if key != 'Year':
                st.write(f"{key}: {value.strip()}")  # Use strip() to remove leading and trailing whitespaces
        
            

    # Section to predict champions (POST method)
    st.header('Predict Champions:')
    champion_year_post = st.text_input('Enter Year for Prediction:')
    if not st.session_state.state_button:
        st.session_state.state_button=st.button("Predict Champions:")
    #print("state_button: ",st.session_state.state_button)
    if st.session_state.state_button:
        #Input fields:
        australian_open = st.text_input('Australian Open:')
        roland_garros = st.text_input('Roland Garros:')
        wimbledon = st.text_input('Wimbledon:')
        us_open = st.text_input('US Open:')
        
        if champion_year_post and australian_open and roland_garros and wimbledon and us_open:
            result = add_champion(int(champion_year_post), (australian_open), (roland_garros), (wimbledon), (us_open), st.session_state.headers)
            st.write(result)
            st.session_state.submitted_button=True
        else:
            st.warning('Please fill in all the details.')
        if st.session_state.submitted_button:
            st.session_state.state_button=False
            st.session_state.submitted_button=False  
    #print("submitted_button:",st.session_state.submitted_button)


    # Section to update champion information (PUT method)
    st.header('Update Champion Information:')
    champion_year_put = st.text_input('Enter Year for Update:')

    #print(st.session_state.update_button)
    if not st.session_state.update_button:
        st.session_state.update_button=st.button('Update Champion Information')
        

    if st.session_state.update_button:
        #Input fields.
        update_data = {
            "Australian_Open": st.text_input('Australian Open:'),
            "Roland_Garros": st.text_input('Roland Garros:'),
            "Wimbledon": st.text_input('Wimbledon:'),
            "US_Open": st.text_input('US Open:')
            }

        if champion_year_put and all(update_data.values()):
            result = update_champion(int(champion_year_put), update_data, st.session_state.headers)
            st.write(result)
            st.session_state.submit=True
            
        else:
            st.warning('Please fill in at least one field for update.')
        if st.session_state.submit:
            st.session_state.update_button=False
            st.session_state.submit=False
            
    # Section to delete champion information (DELETE method)
    st.header('Delete Champion:')
    champion_year_delete = st.text_input('Enter Year for Delete:')
    if st.button('Delete Champion'):
        if champion_year_delete:
            result = delete_champion(int(champion_year_delete), st.session_state.headers)
            st.write(result)
        else:
            st.warning('Please enter the year for the champion you want to delete.')
    
else:
    st.warning('Please log in to access the endpoints.')