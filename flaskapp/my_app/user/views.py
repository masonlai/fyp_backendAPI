from flask import request, jsonify, Blueprint, abort
from flask.views import MethodView
from flask import make_response
from .. import db, app
from .models import User, DeceasedPage
import datetime

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/profile')
def profile():
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[0]

    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        user = User.query.filter_by(id=user_id).first()
        res = {
            'name': user.name,
            'username': user.username,
        }
        return jsonify(res)


class UserView(MethodView):

    def get(self, id=None):
        res = {}
        users = User.query.all()
        res = {}
        for usr in users:
            res[usr.id] = {
                'id': usr.id,
                'name': usr.username,
                'password': usr.password,
            }
        return jsonify(res)

    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        religion = request.form.get('religion')
        exit_user = User.query.filter_by(username=username).first()
        if not exit_user:
            usr = User(username, password, email, religion)
            db.session.add(usr)
            db.session.commit()

            try:
                user = User.query.filter_by(username=username).first()
                access_token = user.generate_token(user.id)
                if access_token:
                    response = {
                        'message': 'You logged in and signed up successfully.',
                        'access_token': access_token.decode(),
                        'username': user.username,
                        'email': usr.email,
                        'religion': usr.religion
                    }
                    return make_response(jsonify(response)), 200

            except Exception as e:
                # Create a response containing an string error message
                response = {
                    'message': str(e) + '1'
                }
                # Return a server error using the HTTP Error Code 500 (Internal Server Error)
                return make_response(jsonify(response)), 500
        else:
            response = {
                'message': 'User already exists. Please login.'
            }

            return jsonify(response)

    def put(self, id):
        # Update the record for the provided id
        # with the details provided.
        return

    def delete(self, id):
        if User.isAdmin(request):
            user = User.query.filter_by(id=id).first()
            if user:
                user.delete()
                return jsonify({'msg': 'user deleted'})
            else:
                return jsonify({'msg': 'user not found'})

        else:
            response = {
                'message': 'you are not allowed to delete user.'
            }

            return jsonify(response)


class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""

    def post(self):
        try:
            # Get the user object using their email (unique to every user)
            user = User.query.filter_by(username=request.form.get('username')).first()
            # Try to authenticate the found user using their password
            if user and user.password == request.form.get('password'):
                # Generate the access token. This will be used as the authorization header
                access_token = user.generate_token(user.id)
                if access_token:
                    response = {
                        'message': 'You logged in successfully.',
                        'access_token': access_token.decode(),
                        'username': user.username
                    }
                    return make_response(jsonify(response)), 200
            else:
                # User does not exist. Therefore, we return an error message
                response = {
                    'message': 'Invalid email or password, Please try again'
                }
                return make_response(jsonify(response)), 401

        except Exception as e:
            # Create a response containing an string error message
            response = {
                'message': str(e) + '1'
            }
            # Return a server error using the HTTP Error Code 500 (Internal Server Error)
            return make_response(jsonify(response)), 500

    def put(self):
        # Update the user password for login user
        # with the details provided.
        auth_header = request.headers.get('Authorization')
        access_token = auth_header

        if access_token:
            user_id = User.decode_token(access_token)
            user = User.query.filter_by(id=user_id).first()
            if user:
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                if password and len(password) >= 5:
                    if password == confirm_password:
                        user.password = password
                        user.save()
                        return jsonify({'msg': 'Password changed successfully'})
                    else:
                        return jsonify({'msg': 'Both password did not matched '})
                else:
                    return jsonify({'msg': 'Minimum length of password should be 5'})
            else:
                return jsonify({'message': 'Please login to reset password.'})
        else:
            return jsonify({'msg': "unauthorized access"})


class CreatingPageView(MethodView):
    def post(self):
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            gender = request.form.get('gender')
            date_of_birth = request.form.get('date_of_birth')
            date_of_death = request.form.get('date_of_death')
            place_of_birth = request.form.get('place_of_birth')
            nationality = request.form.get('nationality')
            life_profile = request.form.get('life_profile')
            portrait = request.files['portrait'].read()
            portrait_position = request.form.get('portrait_position')
            theme = request.files['theme'].read()
            creating_date = datetime.datetime.now()
            a = date_of_birth.split()
            b = date_of_death.split()
            date_of_birth = datetime.datetime.strptime(a[1]+a[2]+a[3], '%b%d%Y')
            date_of_death = datetime.datetime.strptime(b[1]+b[2]+b[3], '%b%d%Y')
            pageInfo = DeceasedPage(first_name, last_name, gender, date_of_birth, date_of_death, \
                                    place_of_birth, nationality, life_profile, portrait, portrait_position,\
                                    theme, creating_date)
            db.session.add(pageInfo)
            db.session.commit()
            db.session.flush()
            db.session.refresh(pageInfo)
            response = {
                'message': 'You created successfully.',
                'id':pageInfo.id,
                'first_name': pageInfo.first_name,
                'last_name': pageInfo.last_name,
                'gender': pageInfo.gender,
                'date_of_birth': pageInfo.date_of_birth,
                'date_of_death': pageInfo.date_of_death,
                'place_of_birth': pageInfo.place_of_birth,
                'nationality': pageInfo.nationality,
                'life_profile': pageInfo.life_profile,
                'portrait_position':pageInfo.portrait_position,
                'creating_date':pageInfo.creating_date

            }
            return make_response(jsonify(response)), 200

        except Exception as e:
            response = {
                'message': str(e) + '1'
            }
            return make_response(jsonify(response)), 500

class TestView(MethodView):
    def post(self):
        try:
            theme = request.files['file'].read()
            print(type(theme))
            response = {
                'message': 'ok'
            }
            return make_response(jsonify(response)), 500
        except Exception as e:
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 500

User_view = UserView.as_view('user_view')
Login_view = LoginView.as_view('login_view')
Creating_page_view = CreatingPageView.as_view('Creating_page_view')
Test_view = TestView.as_view('Test_view')

app.add_url_rule(
    '/registration', view_func=User_view, methods=['POST']
)
app.add_url_rule(
    '/users', view_func=User_view, methods=['GET']
)
app.add_url_rule(
    '/user/<int:id>', view_func=User_view, methods=['GET']
)
app.add_url_rule(
    '/deleteuser/<int:id>', view_func=User_view, methods=['DELETE']
)
app.add_url_rule(
    '/login', view_func=Login_view, methods=['POST']
)
app.add_url_rule(
    '/changePassword', view_func=Login_view, methods=['PUT']
)
app.add_url_rule(
    '/CreatingPage', view_func=Creating_page_view, methods=['POST']
)
app.add_url_rule(
    '/test', view_func=Test_view, methods=['POST']
)
