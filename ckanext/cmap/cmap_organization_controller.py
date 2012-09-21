import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit
import ckan.logic.action as action
import pylons.config as config
import ckan.lib.mailer as mailer
import ckan.logic as logic
import ckan.logic.schema as schema
import ckan.lib.navl.dictization_functions
import ckan.lib.dictization.model_save as model_save

class CMAPOrganizationController(base.BaseController):

    def _send_application( self, group, reason  ):
        from genshi.template.text import NewTextTemplate

        if not reason:
            base.h.flash_error(toolkit._("There was a problem with your "
                "submission, please correct it and try again"))
            errors = {"reason": ["No reason was supplied"]}
            return self.apply(group.id, errors=errors,
                              error_summary=action.error_summary(errors))

        admins = group.members_of_type(base.model.User, 'admin' ).all()
        recipients = [(u.fullname,u.email) for u in admins] if admins else [
                     (config.get('ckan.admin.name', "CKAN Administrator"),
                       config.get('ckan.admin.email', None), )]

        if not recipients:
            base.h.flash_error(toolkit._("There is a problem with the system "
                "configuration"))
            errors = {"reason": ["No group administrator exists"]}
            return self.apply(group.id, errors=errors,
                              error_summary=action.error_summary(errors))

        extra_vars = {
            'group'    : group,
            'requester': base.c.userobj,
            'reason'   : reason
        }
        email_msg = base.render("email/join_publisher_request.txt",
                extra_vars=extra_vars, loader_class=NewTextTemplate)

        try:
            for (name,recipient) in recipients:
                mailer.mail_recipient(name,
                               recipient,
                               "Publisher request",
                               email_msg)
        except:
            base.h.flash_error(toolkit._("There is a problem with the system "
                "configuration"))
            errors = {"reason": ["No mail server was found"]}
            return self.apply(group.id, errors=errors,
                              error_summary=action.error_summary(errors))

        base.h.flash_success(toolkit._("Your application has been submitted"))
        base.h.redirect_to('publisher_read', id=group.name)

    def _add_publisher_list(self):
        base.c.possible_parents = base.model.Session.query(base.model.Group).\
               filter(base.model.Group.state == 'active').\
               filter(base.model.Group.type == 'organization').\
               order_by(base.model.Group.title).all()

    def apply(self, id=None, data=None, errors=None, error_summary=None):
        '''Send a membership application email to an organization's admins.'''

        # Add the dict of the group we're applying to to the template context.
        # This enables the group's website_url to be shown in the site header.
        if id:
            try:
                group = base.model.Group.get(id)
                if not group:
                    base.abort(404, toolkit._('Group not found'))
                context = {'model': base.model,
                           'session': base.model.Session,
                           'user': base.c.user or base.c.author,
                           'for_view': True,
                           'extras_as_string': True}
                base.c.group_dict = toolkit.get_action('group_show')(context,
                        {'id': id})
            except logic.NotFound:
                base.abort(404, toolkit._('Group not found'))
            except logic.NotAuthorized:
                base.abort(401, toolkit._(
                    'Unauthorized to read group %s') % id)

        if 'parent' in base.request.params and not id:
            id = base.request.params['parent']

        if id:
            base.c.group = base.model.Group.get(id)
            if 'save' in base.request.params and not errors:
                return self._send_application(base.c.group,
                        base.request.params.get('reason', None))

        self._add_publisher_list()
        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}

        data.update(base.request.params)

        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}
        base.c.form = base.render('organization_apply_form.html',
                extra_vars=vars)
        return base.render('organization_apply.html')

    def _add_users( self, group, parameters  ):
        if not group:
            base.h.flash_error(toolkit._(
                "There was a problem with your submission, "
                "please correct it and try again"))
            errors = {"reason": ["No reason was supplied"]}
            return self.apply(group.id, errors=errors,
                              error_summary=action.error_summary(errors))

        data_dict = logic.clean_dict(
                ckan.lib.navl.dictization_functions.unflatten(
                    logic.tuplize_dict(logic.parse_params(
                        base.request.params))))
        data_dict['id'] = group.id

        # Temporary fix for strange caching during dev
        l = data_dict['users']
        for d in l:
            d['capacity'] = d.get('capacity','editor')

        context = {
            "group" : group,
            "schema": schema.default_group_schema(),
            "model": base.model,
            "session": base.model.Session
        }

        # Temporary cleanup of a capacity being sent without a name
        users = [d for d in data_dict['users'] if len(d) == 2]
        data_dict['users'] = users

        base.model.repo.new_revision()
        model_save.group_member_save(context, data_dict, 'users')
        base.model.Session.commit()

        base.h.redirect_to( controller='group', action='edit', id=group.name)


    def users(self, id, data=None, errors=None, error_summary=None):
        base.c.group = base.model.Group.get(id)

        if not base.c.group:
            base.abort(404, toolkit._('Group not found'))

        context = {
                   'model': base.model,
                   'session': base.model.Session,
                   'user': base.c.user or base.c.author,
                   'group': base.c.group }

        try:
            logic.check_access('group_update',context)
        except logic.NotAuthorized, e:
            base.abort(401, toolkit._(
                'User %r not authorized to edit %s') % (base.c.user, id))

        if 'save' in base.request.params and not errors:
            return self._add_users(base.c.group, base.request.params)

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}

        data['users'] = []
        data['users'].extend( { "name": user.name,
                                "capacity": "admin" }
                                for user in base.c.group.members_of_type(
                                    base.model.User, "admin").all())
        data['users'].extend( { "name": user.name,
                                "capacity": "editor" }
                                for user in base.c.group.members_of_type(
                                    base.model.User, 'editor' ).all())

        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}
        base.c.form = base.render('organization_users_form.html',
                extra_vars=vars)

        return base.render('organization_users.html')
