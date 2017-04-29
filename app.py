from flask import Flask
from flask_restful import Api
from flask_restful.utils import cors
from flask_mail import Mail
from common import redis_store
from api.UserAPI import RegisterAPI, LoginAPI, ActivateAPI
from api.UserAPI import ChangePasswordAPI, ForgetPasswordAPI
from api.ProjectAPI import ProjectsListAPI
# from api.profileAPI import ProfileAPI, ProfileIconAPI, SearchProfileAPI
# from api.friendsAPI import FriendsListAPI, FriendsRequestAPI
# from api.passwordAPI import ChangePasswordAPI, ForgetPasswordAPI
# from api.postAPI import PostAPI

# load configuration and bootstrap flask
app = Flask(__name__)
app.config.from_object('config')

redis_store.init_app(app)
mail = Mail(app)

api = Api(app)
api.decorators = [cors.crossdomain(origin='*',
                                   headers='my-header, accept, content-type, token')]

# add endpoints to flask restful api
api.add_resource(RegisterAPI, '/create_user')
api.add_resource(LoginAPI, '/login')
api.add_resource(ActivateAPI, '/activate_account')

api.add_resource(ChangePasswordAPI, '/change_password')
api.add_resource(ForgetPasswordAPI, '/forget_password')
#
# api.add_resource(ProfileAPI, '/profile')
# api.add_resource(ProfileIconAPI, '/upload_profile_icon')
# api.add_resource(SearchProfileAPI, '/search_profile')
#
api.add_resource(ProjectsListAPI, '/projects_list')
# api.add_resource(FriendsRequestAPI, '/friends_request')
#
# api.add_resource(PostAPI, '/post')

if __name__ == '__main__':
    app.run(debug=True)
