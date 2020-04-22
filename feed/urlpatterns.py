from django.urls import path

def date(views): 
    return [
        path('<int:year>/<int:month>/<int:day>', views.day, name='day'),
        path('<int:year>/<int:month>', views.month, name='month'),
        path('<int:year>', views.year, name='year'),
    ]