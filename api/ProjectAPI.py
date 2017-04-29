from flask import abort
from flask_restful import Resource, reqparse
from model.Model import User, Project
from common.Auth import auth_required

projectsParser = reqparse.RequestParser()
projectsParser.add_argument('project_name', type=str)
projectsParser.add_argument('project_speed', type=str)

class ProjectsListAPI(Resource):

    @auth_required
    def get(self, user_id):
        """
        Get the user's projects list
        """
        user = User.objects.filter_by(id=user_id)[0]
        projects = user.req_projs.all()
        if projects is None:
            return abort(400)

        return [proj.to_serializable_dict() for proj in projects]

    @auth_required
    def post(self, user_id):
        """
        Add a project to project list
        """
        args = projectsParser.parse_args()
        project_name = args['project_name']
        project_speed = args['project_speed']

        if project_name is None:
            abort(400)

        user = User.objects.filter_by(id=user_id)[0]

        # add a project to project list
        try:
            user.req_projs.append(Project(name=project_name, speed=project_speed))
        except Exception as e:
            user.session.rollback()
            abort(400)

        return {'status': 'success', 'message':
                'The project has been added to your project list'}

    @auth_required
    def delete(self, user_id):
        """
        Delete a specific project from the project list
        """
        args = projectsParser.parse_args()
        project_name = args['project_name']

        if project_name is None:
            abort(400)

        user = User.objects.filter_by(id=user_id)[0]

        try:
            project_to_remove = user.req_projs.filter_by(name=project_name)[-1]
            project_to_remove.delete()
        except Exception as e:
            {'status': 'error', 'message':
                    'Project name is wrong.'}

        return {'status': 'success', 'message':
                'The project has been delete from your project list'}
