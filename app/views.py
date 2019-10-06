import calendar
from flask import render_template
from flask_appbuilder.fieldwidgets import Select2Widget
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.charts.views import GroupByChartView
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.widgets import ListThumbnail
from flask_appbuilder.widgets import FormHorizontalWidget, FormInlineWidget, FormVerticalWidget
from flask_babel import lazy_gettext as _
from flask_appbuilder import ModelView, AppBuilder, expose, BaseView, has_access
from app import appbuilder, db, app
from .models import Employee, Department, Function, EmployeeHistory
"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""
def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()

def department_query():
    return db.session.query(Department)


class EmployeeHistoryView(ModelView):
    datamodel = SQLAInterface(EmployeeHistory)
    base_permissions = ['can_add', 'can_show']
    list_columns = ['department', 'begin_date']

class EmployeeModelView(ModelView):
    datamodel = SQLAInterface(Employee, db.session)

    # list_widget = ListThumbnail


    label_columns = {'full_name': 'Name', 'photo_img': 'Photo', 'photo_img_thumbnail': 'Photo'}
    list_columns = ['photo_img_thumbnail', 'full_name', 'department.name', 'personal_phone', 'birthday', 'function.name']

    base_order = ('full_name', 'asc')
    show_fieldsets = [
        ('Summary', {'fields': ['photo_img', 'full_name', 'gender', 'department', 'function', 'begin_date']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'bank_number'], 'expanded': False}),
    ]

    add_fieldsets = [
        ('Summary', {'fields': ['full_name', 'photo', 'gender', 'department', 'function', 'begin_date']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone', 'bank_number'], 'expanded': False}),
    ]

    edit_fieldsets = [
        ('Summary', {'fields': ['full_name', 'photo', 'gender', 'function']}),
        (
            'Personal Info',
            {'fields': ['address', 'birthday', 'personal_phone'], 'expanded': False}),
    ]
                         

class FunctionView(ModelView):
    datamodel = SQLAInterface(Function)
    related_views = [EmployeeModelView]

class DepartmentView(ModelView):
    datamodel = SQLAInterface(Department)
    related_views = [EmployeeModelView]

class EmployeeChartView(GroupByChartView):
    datamodel = SQLAInterface(Employee)
    chart_title = 'Function of Employee'
    label_columns = EmployeeModelView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group' : 'function',
            'series' : [(aggregate_count,'function')]
        },
        {
            'group' : 'gender',
            'series' : [(aggregate_count,'function')]
        }
    ]



def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)

def pretty_year(value):
    return str(value.year)


class EmployeeTimeChartView(GroupByChartView):
    datamodel = SQLAInterface(Employee)

    chart_title = 'Grouped Birth Employees'
    chart_type = 'AreaChart'
    label_columns = EmployeeModelView.label_columns
    definitions = [
        {
            'group' : 'month_year',
            'formatter': pretty_month_year,
            'series': [(aggregate_count, 'group')]
        },
        {
            'group': 'year',
            'formatter': pretty_year,
            'series': [(aggregate_count, 'group')]
        }
    ]


db.create_all()
fill_gender()
appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")
appbuilder.add_view(EmployeeModelView, "List Employees", icon="fa-envelope", category="Company")
appbuilder.add_separator("Company")
appbuilder.add_view(DepartmentView, "Departments", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(FunctionView, "Functions", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(EmployeeChartView, "Employee Chart", icon="fa-dashboard", category="Company")
appbuilder.add_view(EmployeeTimeChartView, "Employee Birth Chart", icon="fa-dashboard", category="Company")

class MyView(BaseView):

    default_view = 'method1'

    @expose('/method1/')
    
    def method1(self):
        # do something with param1
        # and return to previous page or index
        return 'Hello'

    @expose('/method2/<string:param1>')
   
    def method2(self, param1):
        # do something with param1
        # and render template with param
        param1 = 'Goodbye %s' % (param1)
        return param1

appbuilder.add_view(MyView, "Method1", category='My View')
appbuilder.add_link("Method2", href='/myview/method2/john', category='My View')
"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404




