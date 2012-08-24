import os
import nose

# TODO: It may be possible to fix something in CKAN to make some of these tests
# pass, e.g. when the only error is a validation error due to __junk.
skip_methods = {
    'ckan.tests.functional.api.model.test_package.TestPackagesUnversioned':
        ['test_entity_get_then_post',
         'test_entity_get_then_post_new',
         'test_entity_update_ok_by_name',
         'test_entity_update_ok_by_name_by_put',
         'test_entity_update_readd_tag',
         'test_package_update_delete_last_extra',
         'test_package_update_delete_resource',
         'test_package_update_do_not_delete_last_extra',
         'test_package_update_ok_by_id',
         'test_package_update_ok_by_id_by_put',
         'test_register_post_bad_content_type',
         'test_register_post_indexerror',
         'test_register_post_json',
         'test_register_post_ok',
         'test_register_post_with_group',
         'test_register_post_with_group_sysadmin',
         'test_register_post_readonly_fields',
         'test_register_post_tag_too_long',
         ],
    'ckan.tests.functional.api.model.test_package.TestPackagesVersion1':
        ['test_06_create_pkg_using_download_url',
         'test_10_edit_pkg_with_download_url',
         'test_entity_get_then_post',
         'test_entity_get_then_post_new',
         'test_entity_update_ok_by_name',
         'test_entity_update_ok_by_name_by_put',
         'test_entity_update_readd_tag',
         'test_package_update_delete_last_extra',
         'test_package_update_delete_resource',
         'test_package_update_do_not_delete_last_extra',
         'test_package_update_ok_by_id',
         'test_package_update_ok_by_id_by_put',
         'test_register_post_bad_content_type',
         'test_register_post_indexerror',
         'test_register_post_json',
         'test_register_post_ok',
         'test_register_post_with_group',
         'test_register_post_with_group_sysadmin',
         'test_register_post_readonly_fields',
         'test_register_post_tag_too_long',
        ],
    'ckan.tests.functional.api.model.test_package.TestPackagesVersion2':
        ['test_entity_get_then_post',
         'test_entity_get_then_post_new',
         'test_entity_update_ok_by_name',
         'test_entity_update_ok_by_name_by_put',
         'test_entity_update_readd_tag',
         'test_package_update_delete_last_extra',
         'test_package_update_delete_resource',
         'test_package_update_do_not_delete_last_extra',
         'test_package_update_ok_by_id',
         'test_package_update_ok_by_id_by_put',
         'test_register_post_bad_content_type',
         'test_register_post_indexerror',
         'test_register_post_json',
         'test_register_post_ok',
         'test_register_post_with_group',
         'test_register_post_with_group_sysadmin',
         'test_register_post_readonly_fields',
         'test_register_post_tag_too_long',
        ],
    'ckan.tests.functional.test_user.TestUserController':
        ['test_user_read', # assert 'about' in main_res, main_res
        ],
    'ckan.tests.functional.test_search.TestNonActivePackages':
        ['test_search', # AssertionError: No field by the name 'q' found (fields: None, 'sort')
        ],
    'ckan.tests.functional.test_search.TestSearch2':
        ['test_search', # AssertionError: No field by the name 'q' found (fields: None, 'sort')
         'test_search_foreign_chars', # AssertionError: No field by the name 'q' found (fields: None, 'sort')
        ],
    'ckan.tests.functional.test_pagination.TestPaginationPackage':
        ['test_group_datasets_read_p1', # Pagination links missing from group read page?
         'test_group_datasets_read_p2', # Pagination links missing from group read page?
         'test_package_search_p1', # Pagination links missing from package search page?
         'test_package_search_p2', # Pagination links missing from package search page?

        ],
    'ckan.tests.functional.test_pagination.TestPaginationGroup':
        ['test_group_index', # Pagination links missing from group index page?
        ],
    'ckan.tests.functional.api.model.test_vocabulary.TestVocabulary':
        ['test_add_vocab_tag_to_dataset',
         'test_add_vocab_tag_to_dataset',
         'test_delete_free_tag',
         'test_delete_tag_from_vocab',
        ],
    # TODO: Besides authorization and missing organization from package dict
    # errors, there are lots of other validation errors in these skipped tests,
    # suggests possible schema problems, try to get rid of them.
    'ckan.tests.functional.api.test_activity.TestActivity':
        ['test_01_delete_resources', # The input field __junk was not expected.
         'test_01_remove_tag', # Need to give organisation in package dict
         'test_01_update_extras', # KeyError: extras
         'test_01_update_package', # Need to give organisation in package dict
         'test_01_update_resource', # ValidationError: {u'URL': u'Missing value'}
         'test_01_update_resource_not_logged_in', # Authorization
         'test_add_extras', # Need to give organisation
         'test_add_resources', # Need to give organisation
         'test_add_tag', # Need to give organisation
         'test_create_package', # Need to give organisation
         'test_delete_extras', # KeyError: 'extras'
         'test_create_group', # cmap_auth_functions
         'test_01_delete_resources', # cmap_auth_functions
        ],
    'ckan.tests.functional.test_activity.TestActivity':
        ['test_user_activity',
        ],
    'ckan.tests.functional.api.test_util.TestUtil':
        ['test_status',
        ],
    'ckan.tests.functional.test_admin.TestAdminTrashController':
        ['test_purge_youngest_revision', # TODO: Why does this fail?
        ],
    'ckan.tests.functional.test_authz.TestLockedDownViaRoles':
        ['test_home', # User not authorized to read group. TODO: Why not?
        ],
    'ckan.tests.functional.test_authz.TestSiteRead':
        ['test_pkggroupadmin_read', # User not authorized to read group
         'test_site_reader', # User not authorized to read group
         'test_sysadmin_can_edit_anything', # No orgin package, also name missing
        ],
    'ckan.tests.functional.test_authz.TestUsage':
        ['test_01_visitor_reads', # Not authorized to read group.
         'test_03_user_reads', # Not authorized to read group.
         'test_04_user_edits', # No org in package, name also missing
         'test_admin_edit_deleted', # No org in package, name also missing
         'test_search_deleted', # User not authorized to read group
         'test_sysadmin_can_create_anything', # No org in package
         'test_sysadmin_can_edit_anything', # No org in package, also name missing
         'test_user_creates', # No org in package
         'test_05_author_is_new_package_admin', # TODO: Weird, looks like test data not loaded
        ],
    'ckan.tests.functional.test_group.TestGroup':
        ['test_index', # CMAP template lacks <h1>Groups
         'test_read_plugin_hook', # Lackng support for group read plugin hook?
         'test_new_page', # CMAP template lacks 'Add A Group'
         'test_mainmenu', # Something missing from template
        ],
    'ckan.tests.functional.test_group.TestNew':
        ['test_3_new_duplicate_group', # CMAP template lacks 'Add A Group'
         'test_2_new', # CMAP template lacks 'Add A Group'
         'test_new_bad_param', # cmap_auth_functions
         'test_new_plugin_hook', # cmap_auth_functions
        ],
    'ckan.tests.functional.test_home.TestDatabaseNotInitialised':
        ['test_home_page', # relation 'user' does not exist? Weird
        ],
    'ckan.tests.functional.test_home.TestHomeController':
        ['test_update_profile_notice', # Update profile flash message missing from CMAP templates?
         'test_home_page', # In CMAP templates 'Add a Dataset' appears even if you can't.
        ],
    'ckan.tests.functional.test_package.TestEdit':
        ['test_edit', # Saving a package doesn't redirect?
         'test_edit_2_tags_and_groups', # Saving a package doesn't redirect?
         'test_edit_700_groups_add', # 'groups_0_id' key missing, validation?
         'test_edit_700_groups_remove', # 'groups_0_id' key missing, validation?
         'test_edit_all_fields', # extras_0_key missing, validation?
         'test_edit_basic', # Saving a package doesn't redirect?
         'test_edit_basic_pkg_by_id', # Saving a package doesn't redirect?
         'test_edit_indexerror', # Submitting to a bad solr url succeeds??
         'test_edit_plugin_hook', # CMAP's controller doesn't call package edit plugin hoook
         'test_missing_fields', # A 200 OK that should be a 400
         'test_redirect_after_edit_using_config', # 200 should be 302
         'test_redirect_after_edit_using_param', # 200 should be 302
         ],
    'ckan.tests.functional.test_package.TestNew':
        ['test_missing_fields', # 200 should be 400
         'test_new_all_fields', # No field by the name 'extras__0__key' found
         'test_new_bad_param', # 200 should be 400
         'test_new_existing_name', # Error message missing from template?
         'test_new_indexerror', # 200 should be 500
         'test_new_plugin_hook', # CMAP controller doesn't support new plugin hook
         'test_new_without_resource', # Error message missing from template
         'test_redirect_after_new_using_config', # 200 should be 302
         'test_redirect_after_new_using_param', # 200 should be 302
        ],
    'ckan.tests.functional.test_package.TestReadAtRevision':
        ['test_read_date1', # KeyError: u'revision_id'
         'test_read_date2', # KeyError: u'revision_id'
         'test_read_date3', # KeyError: u'revision_id'
         'test_read_revision1', # KeyError: u'revision_id'
         'test_read_revision2', # KeyError: u'revision_id'
         'test_read_revision3', # KeyError: u'revision_id'
        ],
    'ckan.tests.functional.test_package.TestReadOnly':
        ['test_read_war_rdf', # 'notes' missing from package
         'test_resource_list', # The input field __junk was not expected
        ],
    'ckan.tests.functional.test_package.TestRevisions':
        ['test_4_history_revision_package_link', # KeyError: u'revision_id
        ],
    # Looks like vocabs don't work, probably a validation thing.
    'ckan.tests.functional.test_tag_vocab.TestWUI':
        ['test_01_dataset_view', # The input field __junk was not expected.
         'test_02_dataset_edit_add_vocab_tag',
         'test_03_dataset_edit_remove_vocab_tag', # The input field __junk was not expected."
         'test_04_dataset_edit_change_vocab_tag',
         'test_05_dataset_edit_add_multiple_vocab_tags',
         'test_02_dataset_edit_add_free_and_vocab_tags_then_edit_again',
        ],
    'ckan.tests.logic.test_action.TestAction':
        ['test_03_create_update_package', # No org in package, and __junk field
         'test_19_update_resource', # No org in package
         'test_20_task_status_update', # No org in package
         'test_21_task_status_update_many', # No org in package
         'test_24_task_status_show', # No org in package
         'test_25_task_status_delete', # No org in package
         'test_41_create_resource', # KeyError: 'resources'
         'test_4_sort_by_metadata_modified', # The input field __junk was not expected
        ],

    # These are all broken by 401 Unauthorized, NotAuthorized exception or
    # 403 Forbidden from the the cmap_auth_functions plugin (only authorizes
    # sysadmins to create groups/organizations).
    'ckan.tests.functional.api.model.test_group.TestGroupsUnversioned':
        ['test_10_edit_group',
         'test_register_post_ok',
        ],
    'ckan.tests.functional.api.model.test_group.TestGroupsVersion1':
        ['test_10_edit_group',
         'test_register_post_ok',
        ],
    'ckan.tests.functional.api.model.test_group.TestGroupsVersion2':
        ['test_10_edit_group',
         'test_register_post_ok',
        ],
}

class CMAPNosePlugin(nose.plugins.Plugin):
    name = 'CMAPNosePlugin'

    def options(self, parser, env=os.environ):
        super(CMAPNosePlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(CMAPNosePlugin, self).configure(options, conf)
        self.enabled = True

    def wantMethod(self, method):
        # Skip any methods from skip_methods.
        for test_class in skip_methods.keys():
            if test_class in str(getattr(method, 'im_class', None)):
                if method.__name__ in skip_methods[test_class]:
                    return False
        return None
