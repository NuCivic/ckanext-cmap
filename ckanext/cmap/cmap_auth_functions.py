import ckan.plugins as plugins
import ckan.authz

def group_create(context, data_dict=None):
    # Only authorize sysadmins to create groups (organizations):
    user = context['user']
    return {'success': ckan.authz.Authorizer.is_sysadmin(user)}

class CMAPAuthFunctions(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthFunctions, inherit=True)

    def get_auth_functions(self):
        return {
                'group_create': group_create,
                }
