import django_tables2 as tables
from .models import Entry
from django.utils.html import format_html

class MoneyColumn(tables.Column):
    def render(self,value):
        if value is not None:
            return "$" + str(value)
        else:
            return ''

class BoolColumn(tables.Column):
    def render(self,value):
        if value:
            return format_html("<i class=\"fas fa-check\" style=\"color:green;\"></i>")
        else:
            return format_html("<i class=\"fas fa-times\" style=\"color:red;\"></i>")

class EntryTable(tables.Table):
    min_price = MoneyColumn()
    max_price = MoneyColumn()
    rv = BoolColumn()
    gc = BoolColumn()
    cl = BoolColumn()
    id = tables.Column(verbose_name='')
    edit = tables.TemplateColumn("<div style='text-align:center'><button type='button' class='edit btn btn-sm btn-primary' data-id='{% url 'edit' record.id %}'><span class='fa fa-pencil'></button> " +
                                 "<button type='button' class='delete btn btn-sm btn-danger' data-id='{% url 'delete' record.id %}'><span class='fa fa-trash'></button></div>"
                                 ,verbose_name='')

    class Meta:
        model = Entry
        exclude = ('user','initiallyScanned')
        template_name = "django_tables2/bootstrap4.html"
        '''attrs = {"td":
                    {"style":"color: black;"},
                }'''
    
    def render_id(self, value):
        return format_html('<input type="hidden" name="id" value="{}" />', str(value))