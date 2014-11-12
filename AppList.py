import datetime, pickle
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

    def __str__(self):
        s = 'Company Name: {0}\nStatus: {1}\nDate: {2}/{3}/{4}\nInterest: {5}\nURL: {6}\n{7}\n'.format(self.company_name, self.status, self.date[0], self.date[1], self.date[2], self.interest, self.url, self.category)
        if self.notes:
            s += self.notes + '\n'
        return s

class ApplicationList:
    def __init__(self, filename = ''):
        if filename:
            #read in data from filename, adds each job application to self.apps
            with open(filename, 'rb') as f:
                self.apps = pickle.load(f).apps
        else:
            self.apps = []

    def add(self, application):
        self.apps.append(application)

    def remove(self, company_name):
        #removes app based on app.company_name, may add ability to remove based on more factors
        self.apps = [app for app in self.apps if app.company_name != company_name]

    def search(self, key, value):
        if key == 'name':
            key = 'company_name'
        found = ApplicationList()
        k = attrgetter(key)
        for app in self.apps:
            if k(app) == value:
                found.add(app)
        return found

    def sort(self, sort_key, reverse=False):
        #sorts self.apps by key
        if sort_key == 'name':
            sort_key = 'company_name'
        self.apps.sort(key=attrgetter(sort_key))
        if reverse:
            self.apps = self.apps[::-1]
    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    def __str__(self):
        #string rep when using as CLI
        s = ''
        for app in self.apps:
            s += (str(app) + '\n')
        return s

appList = ApplicationList('apps.txt')
appList.sort("interest", True) #defaults to listing companies by interest from highest to lowest

while(True):
    print('[0] print out applications')
    print('[1] sort')
    print('[2] filter')
    user_input = int(input())
    if user_input == 0:
        print(str(appList))
    elif user_input == 1:
        print('What attribute would you like to sort by?')
        sort_key = input()
        appList.sort(sort_key)
    elif user_input == 2:
        print('What attribute would you like to filter by?')
        filter_key = input()
        print('For what value?')
        value = input()
        print(str(appList.search(filter_key, value)))
    else:
        print('invalid input')
