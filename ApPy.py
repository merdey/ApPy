import datetime, pickle, os
from operator import attrgetter

valid_status_options = ['interested',
                        'researched',
                        'applied',
                        'phone screen',
                        'interview',
                        'offer',
                        ]

#mainly to ensure categories maintain some sense of order (for sorting) and to act as a spell/sanity check when inputting new apps
valid_categories = ['Varied', #alias for "I'm not quite sure"
                    'Web',
                    'iOS',
                    'Telecom',
                    'Education',
                    'Data',
                    'Games',
                    'Business',
                    ]

app_attributes = ['Status',
                  'Interest',
                  'URL',
                  'Category',
                  'Date',
                  'Notes']

DEFAULT_SORT = 'interest'
NAME_WIDTH = 20
INTEREST_WIDTH = 20
URL_WIDTH = 100

class JobApplication:
    def __init__(self, company_name, status, interest, url, category, notes=''):
        assert status in valid_status_options, 'Invalid Status'
        assert category in valid_categories, 'Invalid category: check spelling or ammend the list of valid categories'
        
        self.company_name = company_name
        self.status = status
        self.interest = interest
        self.url = url
        self.category = category
        self.date = datetime.datetime.now()
        self.date = [self.date.month, self.date.day, self.date.year]
        self.notes = notes


    def changeStatus(self, new_status):
        assert status in valid_status_options, 'Invalid Status'
        
        self.status = new_status

    def toDictionary(self):
        d = {'Company Name': self.company_name,
			 'Status': self.status,
             'Interest': self.interest,
             'URL': self.url,
             'Category': self.category,
             'Date': self.date,
             'Notes': self.notes}
        return d

    def __str__(self):
        s = 'Company Name: {0}\nStatus: {1}\nDate: {2}/{3}/{4}\nInterest: {5}\nURL: {6}\n{7}\n'.format(self.company_name, self.status, self.date[0], self.date[1], self.date[2], self.interest, self.url, self.category)
        if self.notes:
            s += self.notes + '\n'
        return s

class ApplicationList:
    def __init__(self, filename = ''):
        if filename:
            path = os.path.dirname(os.path.abspath(__file__))
            #read in data from filename, adds each job application to self.apps
            with open(path + '\\' + filename, 'rb') as f:
                self.apps = pickle.load(f).apps
        else:
            self.apps = []

    def add(self, application):
        self.apps.append(application)

    def remove(self, company_name):
        #removes app based on app.company_name, may add ability to remove based on more factors
        self.apps = [app for app in self.apps if app.company_name != company_name]

    def search(self, key, value):
        found = ApplicationList()
        k = attrgetter(key)
        for app in self.apps:
            if k(app) == value:
                found.add(app)
        return found

    def sort(self, sort_key, reverse=False):
        #sorts self.apps by key
        self.apps.sort(key=attrgetter(sort_key))
        if reverse:
            self.apps = self.apps[::-1]

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    def toDictionary(self):
        #for use with kivy list view
        app_data = {}
        for app in self.apps:
            app_data[app.company_name] = app.toDictionary()
        return app_data

    def __str__(self):
        #string rep when using as CLI
        s = ''
        for app in self.apps:
            s += (str(app) + '\n')
        return s

appList = ApplicationList('apps.txt')
app_data = appList.toDictionary()

#######
#Kivy
#######
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView, ListItemButton
from kivy.adapters.dictadapter import DictAdapter
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.properties import StringProperty


class MasterDetailView(GridLayout):
    def __init__(self,  items, **kwargs):
        kwargs['cols'] = 2
        super(MasterDetailView, self).__init__(**kwargs)

        list_item_args_converter = lambda row_index, rec: {'text': rec['Company Name'],
                                                           'size_hint_y': None,
                                                           'height': 25}
        dict_adapter = DictAdapter(sorted_keys=sorted(app_data.keys()),
                                   data=app_data,
                                   args_converter=list_item_args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=False,
                                   cls=ListItemButton)


        master_list_view = ListView(adapter=dict_adapter,
                                    size_hint=(.3, 1.0))
        self.add_widget(master_list_view)


        detail_view = AppDetailView(
            app_name=dict_adapter.selection[0].text,
            size_hint=(.7, 1.0))
        
        dict_adapter.bind(on_selection_change=detail_view.app_changed)
        self.add_widget(detail_view)


class AppDetailView(GridLayout):
    app_name = StringProperty('', allownone=True)

    def __init__(self, **kwargs):
        kwargs['cols'] = 2
        self.app_name = kwargs.get('app_name', '')
        super(AppDetailView, self).__init__(**kwargs)
        if self.app_name:
            self.redraw()

    def redraw(self, *args):
        self.clear_widgets()
        if self.app_name:
            self.add_widget(Label(text="Name:", halign='right'))
            self.add_widget(Label(text=self.app_name))
            for attribute in app_attributes:
                self.add_widget(Label(text="{0}:".format(attribute),
                                      halign='right'))
                self.add_widget(Label(text=str(app_data[self.app_name][attribute])))

    def app_changed(self, list_adapter, *args):
        if len(list_adapter.selection) == 0:
            self.app_name = None
        else:
            selected_object = list_adapter.selection[0]
            if type(selected_object) is str:
                self.app_name = selected_object
            else:
                self.app_name = selected_object.text
        self.redraw()


class AppObserverDetailView(GridLayout):
    app_name = StringProperty('')

    def __init__(self, **kwargs):
        kwargs['cols'] = 2
        super(AppObserverDetailView, self).__init__(**kwargs)
        self.bind(app_name=self.redraw)

    def redraw(self, *args):
        self.clear_widgets()
        if self.app_name:
            self.add_widget(Label(text="Name:", halign='right'))
            self.add_widget(Label(text=self.app_name))
            for attribute in app_attributes:
                self.add_widget(Label(text="{0}:".format(attribute),
                                      halign='right'))
                if self.app_name == '':
                    self.add_widget(Label(text=''))
                else:
                    self.add_widget(Label(text=str(app_data[self.app_name][attribute])))

    def update(self, object_adapter, *args):
        if object_adapter.obj is None:
            return

        if type(object_adapter.obj) is str:
            self.app_name = object_adapter.obj
        else:
            self.app_name =str(object_adapter.obj)
        self.redraw()

if __name__ == '__main__':
	from kivy.base import runTouchApp
	master_detail = MasterDetailView(sorted(app_data.keys()), width=800)
	runTouchApp(master_detail)
