from flask import Flask, jsonify, request, redirect
from flask_mysqldb import MySQL
from flask_smorest import abort
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_restx import Api, Resource, fields, Namespace

app = Flask(__name__)
CORS(app)
bcrypt=Bcrypt(app)
api = Api(app, version='1.0', title='Tennis API', description='Tennis Grand Slams Champions', default='Endpoints',doc='/')


#Configure the Flask app for JWT
app.config['SECRET_KEY'] = '123'  #Change this to a secure secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
jwt = JWTManager(app)

#DataBase Connection
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'grand_slams'
mysql = MySQL(app)

#Define a bearer token:
token_parser = api.parser()
token_parser.add_argument('Authorization', location='headers', required=True, help='Bearer token')

# Define a model for the request payload in the signup endpoint
signup_model = api.model('Signup', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

# Define a model for the request payload in the login endpoint
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

# Define a model for the response in the get_titles endpoint
title_model = api.model('Title', {
    'Number_of_Titles': fields.Integer(description='Number of Titles'),
    'Player': fields.String(description='Player'),
    'Amateur_Era': fields.String(description='Amateur Era Titles'),
    'Open_Era': fields.String(description='Open Era Titles'),
    'Australian_Open': fields.String(description='Australian Open Titles'),
    'Roland_Garros': fields.String(description='Roland Garros Titles'),
    'Wimbledon': fields.String(description='Wimbledon Titles'),
    'US_Open': fields.String(description='US Open Titles'),
    'Years': fields.String(description='Years')
})
titles_list_model = api.model('Titles List', {
    'Career_Titles': fields.List(fields.Nested(title_model), description='List of career titles')})

player_title_model = api.model('Titles by Player', {
    'database_player': fields.String(description='Player in the database'),
    'argument_player': fields.String(description='Player from the request argument'),
    'number_of_titles': fields.Integer(description='Number of Titles')
})

# Define a model for the response in the get_champions endpoint.
champions_model = api.model('Champions:', {
    'Year': fields.String(description='Year'),
    'Australian_Open': fields.String(description='Australian Open Champion'),
    'Roland_Garros': fields.String(description='Roland Garros Champion'),
    'Wimbledon': fields.String(description='Wimbledon Champion'),
    'US_Open': fields.String(description='US Open Champion')
})
champions_list_model = api.model('Champions List', {
    'Champions': fields.List(fields.Nested(champions_model), description='List of Champions')})

# Define a model for the response in the get_champions_by_year endpoint
champion_by_year_model = api.model('Champions by Year', {
    'Year': fields.Integer(description='Year'),
    'Australian_Open': fields.String(description='Australian Open Champion'),
    'Roland_Garros': fields.String(description='Roland Garros Champion'),
    'Wimbledon': fields.String(description='Wimbledon Champion'),
    'US_Open': fields.String(description='US Open Champion')
})

champions_prediction_model = api.model('Champions Prediction', {
    'Year': fields.Integer(required=True, description='Year to predict'),
    'Australian_Open': fields.String(required=True, description='Predicted Australian Open Champion'),
    'Roland_Garros': fields.String(required=True, description='Predicted Roland Garros Champion'),
    'Wimbledon': fields.String(required=True, description='Predicted Wimbledon Champion'),
    'US_Open': fields.String(required=True, description='Predicted US Open Champion')
})

# Define a model for the request payload in the update_champion endpoint
champions_update_model = api.model('Champions Update', {
    'Australian_Open': fields.String(description='Updated Australian Open Champion'),
    'Roland_Garros': fields.String(description='Updated Roland Garros Champion'),
    'Wimbledon': fields.String(description='Updated Wimbledon Champion'),
    'US_Open': fields.String(description='Updated US Open Champion')
})


#SIGN-UP
@api.route('/signup')
class Signup(Resource):
    @api.expect(signup_model)  # Expecting the request payload to match the defined model
    def post(self):
        try:
            data = request.get_json()
            
            #Ensure all required data is present in the request
            required_fields = ['username', 'password']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Incomplete data'}), 400

            #Extract data from the request
            username = data['username']
            password = data['password']

            #Hash the password before storing it in the database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            #Add the new user to the 'users' table
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'message': 'User registered successfully'})
        
        except Exception as e:
            # Print the exception to the console for debugging purposes
            print(f"Error in signup route: {str(e)}")

            # Return a meaningful error response to the client
            return jsonify({'error': 'Internal Server Error'})


#LOG-IN
@api.route('/login')
class Login(Resource):
    @api.expect(login_model)  # Expecting the request payload to match the defined model
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            entered_password = data.get('password')
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            username = cursor.fetchone()
            
            if username:
                #Extract the hashed password from the database
                hashed_password = username[1]
                bpw=bcrypt.check_password_hash(hashed_password, entered_password)
                #Check if the entered password matches the stored hash
                if bpw:
                    #Passwords match, authentication successful
                    access_token = create_access_token(identity=username)
                    return jsonify(access_token=access_token)
                else:
                    #Passwords don't match
                    return jsonify({"message": "wrong username or password"})
            else:
                # User not found
                return jsonify({"message": "wrong username or password"})

        except Exception as e:
            print(f"Error in login route: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e)}, 500


#GET Titles.
@api.route('/titles')
class Titles(Resource):
    @api.doc(parser=token_parser)
    @api.header('Authorization', 'Bearer token')
    @api.marshal_list_with(titles_list_model)  # Marshall the response using the defined model
    @api.doc(description='Get a list of all titles')  # Description for the Swagger documentation
    def get(self):
        """
        List of Players with 3 titles or more.
        """
        try:        
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM titles")
            data = cursor.fetchall()
            cursor.close()
            titles_list = []
            
            for title in data:
                title_dict = {
                    'Number_of_Titles': title[0],
                    'Player': title[1],
                    'Amateur_Era': title[2],
                    'Open_Era': title[3],
                    'Australian_Open': title[4],
                    'Roland_Garros': title[5],
                    'Wimbledon': title[6],
                    'US_Open':title[7],
                    'Years':title[8]            
            }
                titles_list.append(title_dict)
            
            return {'Career_Titles':titles_list}
        except Exception as e:
            print(f"Error in get_titles route: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

#GET Titles by Player:
@api.route('/titles/<string:player_name>')
class TitlesByPlayer(Resource):
    @api.doc(parser=token_parser)
    @api.header('Authorization', 'Bearer token')
    @api.marshal_with(player_title_model)  # Marshal the response using the defined model
    @api.doc(params={'player_name': 'Player name to filter titles'})  # Description for the Swagger documentation
    def get(self, player_name):
        """
        Total Grand Slams Titles for each player.
        """
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT Player, Titles FROM titles WHERE Player LIKE %s", ('%' + player_name + '%',))
            result = cursor.fetchone()
            cursor.close()
            if result:
                database_player, count = result
                return {'database_player': database_player, 'argument_player': player_name,'number_of_titles': count}
            else:
                return {'player': player_name, 'number_of_titles': 0}
        except Exception as e:
            print(f"Error in get_titles_by_player route: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e)}, 500
        
        
#GET Champions.  
@api.route('/champions')
class Champions(Resource):
    @api.doc(parser=token_parser)
    @api.header('Authorization', 'Bearer token')
    @api.marshal_list_with(champions_list_model)  # Marshal the response using the defined model
    @api.doc(description='Get a list of all champions')  # Description for the Swagger documentation
    def get(self):
        """
        Get Champions List.
        """
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM champions")
            data = cursor.fetchall()
            cursor.close()
            
            champions_list = []
            for champion in data:
                champion_dict = {
                    'Year': champion[0],
                    'Australian_Open': champion[1],
                    'Roland_Garros': champion[2],
                    'Wimbledon': champion[3],
                    'US_Open': champion[4],
            }
                champions_list.append(champion_dict)

            return {'Champions': champions_list}
        except Exception as e:
            print(f"Error in get_champions route: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

#Get Champions by Year.   
@api.route('/champions/<int:year>')
class ChampionsByYear(Resource):
    @api.doc(parser=token_parser)
    @api.header('Authorization', 'Bearer token')
    @api.marshal_with(champion_by_year_model)  # Marshal the response using the defined model
    @api.doc(params={'year': 'Year to filter champions'})  # Description for the Swagger documentation
    def get(self, year):
        """
        Get champions by chosen year.
        """
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM champions WHERE Year = %s", (year,))
            data = cursor.fetchone()
            cursor.close()

            if data:
                champion_dict = {
                    'Year': data[0],
                    'Australian_Open': data[1],
                    'Roland_Garros': data[2],
                    'Wimbledon': data[3],
                    'US_Open': data[4]  
                }
                return champion_dict
            else:
                return {'message': f'No champion found for the year {year}'}, 404

        except Exception as e:
            print(f"Error in get_champions_by_year route: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e)}, 500
        
#Predict Champions for next years.
@api.route('/champions')
class ChampionsPrediction(Resource):
    @api.expect(champions_prediction_model)  # Expecting the request payload to match the defined model
    @api.doc(parser=token_parser)
    @api.header('Authorization', 'Bearer token')
    @api.doc(description='Predict champions for the next years')  # Description for the Swagger documentation
    def post(self):
        try:
            data = request.json
            # Ensure all required data is present in the request
            required_fields = ['Year', 'Australian_Open', 'Roland_Garros', 'Wimbledon', 'US_Open']
            if not all(field in data for field in required_fields):
                return {'error': 'Incomplete data'}, 400
            # Extract data from the request
            year = data['Year']
            australian_open = data['Australian_Open']
            roland_garros = data['Roland_Garros']
            wimbledon = data['Wimbledon']
            us_open = data['US_Open']
            # Add the predicted champion to the database for the given year
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO champions (Year, Australian_Open, Roland_Garros, Wimbledon, US_Open) VALUES (%s, %s, %s, %s, %s)",
                (year, australian_open, roland_garros, wimbledon, us_open))
            mysql.connection.commit()
            cursor.close()

            return {'message': 'Champion prediction added successfully for the year'}

        except Exception as e:
            print(f"Error in post_champion_prediction route: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

# Update champion information for a specific year
@api.route('/champions/<int:year>')
class UpdateChampion(Resource):
    #@api.doc(parser=token_parser)
    @api.header('Authorization', 'Bearer token')
    @api.expect(champions_update_model)  # Expecting the request payload to match the defined model
    @api.doc(params={'year': 'Year to update champion information'}, parser=token_parser)  # Description for the Swagger documentation
    def put(self, year):
        try:
            data = request.json

            # Ensure at least one field is provided for updating
            if not any(field in data for field in ['Australian_Open', 'Roland_Garros', 'Wimbledon', 'US_Open']):
                return {'error': 'No fields provided for update'}, 400

            cursor = mysql.connection.cursor()

            # Build the update query dynamically based on the provided fields
            update_query = "UPDATE champions SET "
            update_values = []

            for field, value in data.items():
                if field in ['Australian_Open', 'Roland_Garros', 'Wimbledon', 'US_Open']:
                    update_query += f"{field} = %s, "
                    update_values.append(value)

            # Remove the trailing comma and add the WHERE clause
            update_query = update_query.rstrip(', ') + " WHERE Year = %s"
            update_values.append(year)

            # Execute the update query
            cursor.execute(update_query, tuple(update_values))
            mysql.connection.commit()
            cursor.close()

            return {'message': f'Champion information updated for the year {year}'}, 200

        except Exception as e:
            print(f"Error in update_champion route: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e)}, 500    


#DELETE Champions
@api.route('/champions/<int:year>')
class DeleteChampion(Resource):
    @api.doc(parser=token_parser)
    @api.header('Authorization', 'Bearer token')
    @api.doc(params={'year': 'Year to delete champion'})  # Description for the Swagger documentation
    def delete(self, year):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM champions WHERE Year = %s", (year,))
            mysql.connection.commit()
            cursor.close()

            return {'message': f'Champion for the year {year} deleted successfully'}, 200

        except Exception as e:
            print(f"Error in delete_champion route: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e)}, 500    

#Add a route to serve the Streamlit interface
@app.route('/streamlit_interface', methods=['GET'])
@jwt_required()
def serve_streamlit_interface():
    # Add your Streamlit interface URL here
    return redirect("http://localhost:8501/")  # Update with your Streamlit interface URL
        
if __name__ == '__main__':
    app.run(debug=True)
    
