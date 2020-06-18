@register.filter(name='exercise_distance')
def distance(value):
    # if less than a quarter mile, return meters
    if value < 402:
        return f'{value}m'

    # otherwise return miles
    return f'{value/1609}mi'