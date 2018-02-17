from appfd.models import Place
@then('The number of places should be greater than 10 million')
def check_number_of_places(context):
    assert(Place.objects.count() > 10000000)
