import os
from compute import compute_drag_free_landing as compute_function

from flask import Flask, render_template, request
from compute_drag_free_landing_model import DragFreeLanding

# Application object
app = Flask(__name__)

# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    form = DragFreeLanding(request.form)
    if request.method == 'POST' and form.validate():

        result = compute(form)

    else:
        result = None

    return render_template("compute_drag_free_landing_view.html", form=form, result=result)


def compute(form):
    """
    Generic function for compute_function with arguments
    taken from a form object (wtforms.Form subclass).
    Return the output from the compute_function.
    """
    # Extract arguments to the compute function
    import inspect
    arg_names = inspect.getargspec(compute_function).args

    # Extract values from form
    form_values = [getattr(form, name) for name in arg_names
                   if hasattr(form, name)]

    form_data = [value.data for value in form_values]

    # Convert data to right types (if necessary)
    # for i in range(len(form_data)):
    #    name = arg_names[i]
    #    if name == '...':
    #         form_data[i] = int(form_data[i])
    #    elif name == '...':

    # Run computations
    result = compute_function(*form_data)
    return result

if __name__ == '__main__':
    app.run(debug=True)
