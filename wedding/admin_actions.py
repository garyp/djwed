import csv
from django.http import HttpResponse
from django.contrib.admin.util import lookup_field, label_for_field

# based on http://djangosnippets.org/snippets/2020/
def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def write_encoded(writer, row):
        return writer.writerow([unicode(i).encode('utf-8') for i in row])

    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        model = modeladmin.model
        if fields:
            field_names = set(fields)
        else:
            field_names = set([field.name for field in model._meta.fields])
            if exclude:
                excludeset = set(exclude)
                field_names = field_names - excludeset

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % (
                unicode(model._meta).replace('.', '_'),)

        writer = csv.writer(response)
        if header:
            write_encoded(writer, (label_for_field(field, model, modeladmin)
                                   for field in field_names))
        for obj in queryset:
            write_encoded(writer, (lookup_field(field, obj, modeladmin)[2]
                                   for field in field_names))
        return response
    export_as_csv.short_description = description
    return export_as_csv

