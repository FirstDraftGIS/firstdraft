from django.db.models.fields.related import ForeignKey

def get_sorted_field_names(model):
    fieldnames = []
    foreign_keys = []
    for field in model._meta.fields:
        if isinstance(field, ForeignKey):
            foreign_keys.append(field.name + "_id")
        else:
            fieldnames.append(field.name)
            
    # add foreign key fields to the end, which is what django does
    fieldnames += foreign_keys
    print("fieldnames:", fieldnames)
    
    return fieldnames