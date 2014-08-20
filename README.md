MangoTrac
===============================================================================================

MangoTrac is an issue tracker based on Django admin app. It's targeted at small and medium-sized
teams and projects.

Setup
===============================================================================================

MangoTrac is a Django app and should be set up / deployed based on instructions from your web
provider.

You will need to load status codes from the fixture, using this command:

    manage.py loaddata issues/fixtures/status.json

(also see SPECIAL_STATUS_CODES note in the settings section below)

Once set up and running, you should log into the Django Admin (at /admin/) and populate the
following tables: priority codes (e.g. 1-highest), types (e.g. bug, enhancement).


Features
===

 - issue fields: status, project, priority, difficulty, version, type, milestone.

 - since it's based on the Django Admin, all of the sorting / filtering admin features are
   available: sort by multiple columns, filter by any of the values in columns

 - filter by: priority, difficulty, project, tags, status, owner

 - reports with multiple filters can be easily created (see reports section below)

 - add multiple issues on one page

 - codebase is small and simple and easy to tweak and add custom features

 - email notifications

 - comments (status / owner may be updated on the comment form)

 - tested with Django 1.6

 - close / open issues with one click from the main listing ()

    (done/wontfix issues will be shown as 'closed', all others as 'open'; using the toggle button
    will do these actions: 'closed' => 'open', any non-closed => 'done')


Limitations
===============================================================================================

 - no integration with revision control systems like Git, Mercurial, etc.

 - no built-in wiki

 - simple permissions system with two levels:

    - users set as staff members can list, add / update issues and reports

    - advanced users can add / edit status codes, projects, versions, etc -- set up by adding
      per-table permissions in Django Admin

Reports
===============================================================================================

Reports can be used to create outlines of outstanding issues, based on multiple filters, grouped
by categories and customizable set of columns

Example 1:

    filters: status = 1 - open, 2 - waiting for feedback

    columns: title, status, owner, created datetime, difficulty

    group by: owner, status

Example 2:

    filters:
        owner = ak
        project = MangoTrac, Pyramid

    columns: id, title, description, priority_code

    group by: priority_code, project

Notes
===============================================================================================

If you need to allow non-staff members to add issues, you can edit the issues/urls.py file to
change the 'create_issue' view to use login_required() decorator instead of
staff_member_required().

Similarly, if you need non-logged in users to add issues, you can removed the decorator from the
above urlconf line.

Most of the views are using staff_member_required() decorator, you can change or remove the
decorator as needed for each view.

Settings
===============================================================================================

    SHOW_PROGRESS_BAR = True

Shows progress bar for each issue on the issue listing, you can click on a position on the bar to set progress.

    SEARCH_ON         = True        # search in admin

Show search box in admin (will search titles and descriptions, may get slow with large number of
issues)

    SPECIAL_STATUS_CODES = dict(
                                open    = "1 - open",
                                done    = "4 - done",
                                wontfix = "5 - won't fix",
                                )

You can change status codes to be anything you like, but the toggle switch logic needs to know
which status codes stand for 'open', 'wontfix', 'done', so if you change their values, you'll need
to update them in SPECIAL_STATUS_CODES as well.

Note that other status codes are not used by the app logic and therefore can be set to anything.
