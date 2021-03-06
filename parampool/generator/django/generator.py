import os, shutil, tarfile

from generate_models import generate_models
from generate_views import generate_views
from generate_template import generate_template
from django_setup import start_all

def generate(compute_function,
             pool_function=None,
             projectname=None,
             appname=None,
             classname=None,
             enable_login=False,
             default_field='TextField',
             filename_template="index.html",
             filename_views="views.py",
             filename_models="models.py",
             doc='',
             MathJax=False):
    """
    Given a function `compute_function` that takes a series of
    arguments, generate a Django web form where

     * the arguments can be given values,
     * the `compute_function` is called with the given arguments, and
     * the return values from `compute_function` are presented.

    There are two basic ways to extract information about the input
    arguments to `compute_function`. Either a `pool` of type `Pool`)
    is specified, or the code can inspect the names of the arguments
    of the `compute_function`.

    The `pool` object organizes a tree of input parameters, each with
    at least two attribues: a name and a default value. Other
    attribures, such as widget (form) type, valid range of values,
    help string, etc., can also be assigned.  The `pool` object is
    mapped to a web form and `compute_function` is called with keyword
    arguments, each argument consisting of the name of the parameter
    in the pool and the value read from the web form. The names of the
    arguments in `compute_function` and the names of the parameters in
    the `pool` object must correspond exactly.

    If no `pool` object is given, the names of the arguments in
    `compute_function` are extracted and used in the web form.
    In the case where all arguments are positional (no default values),
    the web form consists of text fields for each argument, unless
    `default_field` is set to something else, e.g., `FloatField`.
    Since `TextField` is default, the user **must** go into the
    generated `output_forms` file, find ``# Convert data to right types``
    and apply a data conversion as outlined in the example. Any
    keyword argument in `compute_function` can be used to detect the
    argument type and assign a proper web form type. We therefore
    recommend to use keyword arguments only in `compute_function`.
    """

    if compute_function.__name__.startswith('compute_'):
        _compute_function_name = compute_function.__name__[8:]
    else:
        _compute_function_name = compute_function.__name__

    if projectname is None:
        projectname = _compute_function_name
    if appname is None:
        appname = "app"
    if classname is None:
        classname = ''.join([s.capitalize()
                             for s in _compute_function_name.split('_')])


    project_dir = os.path.join(os.getcwd(), projectname)
    start_all(projectname, appname, project_dir, enable_login)
    app_dir = os.path.join(project_dir, appname)
    static_dir = os.path.join(app_dir, "static")
    templates_dir = os.path.join(app_dir, "templates")

    if not os.path.isdir(templates_dir):
        os.mkdir(templates_dir)

    filename_models_path = os.path.join(app_dir, filename_models)
    filename_views_path = os.path.join(app_dir, filename_views)
    filename_template_path = os.path.join(templates_dir, filename_template)
    if enable_login:
        output_forms_path = os.path.join(app_dir, "forms.py")

    if pool_function:
        pool = pool_function()
    else:
        pool = None

    # Copy static files
    shutil.copy(compute_function.__module__ + ".py", app_dir)
    if pool_function:
        shutil.copy(pool_function.__module__ + ".py", app_dir)

    if pool is not None:
        os.chdir(app_dir)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'static.tar.gz'),
                    os.curdir)
        archive = tarfile.open('static.tar.gz')
        archive.extractall()
        os.remove('static.tar.gz')
        os.chdir("../../")
    else:
        if not os.path.isdir(static_dir):
            os.mkdir(static_dir)
    # No need for clean-up script since all generated files are in
    # the project subdirectory which can be easily removed

    generate_template(compute_function, classname, filename_template_path,
                      pool, enable_login, MathJax, doc)
    generate_models(compute_function, classname, filename_models_path,
                    default_field, pool, enable_login)
    generate_views(compute_function, classname, filename_views_path,
                   filename_template, pool_function,
                   filename_models, enable_login)
    if enable_login:
        from generate_forms import generate_forms
        generate_forms(output_forms_path)

    print "Django app successfully created in %s/" % projectname
    print "Run python %s/manage.py runserver" % projectname
    print "and access the app at http://127.0.0.1:8000/"
    if enable_login:
        print "PS - remember to run python %s/manage.py syncdb before python %s/manage.py runserver" \
                % (projectname, projectname)
