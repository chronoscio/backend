from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import *

# Register your models here.
admin.site.register(Territory, SimpleHistoryAdmin)
admin.site.register(PoliticalEntity, SimpleHistoryAdmin)
admin.site.register(DiplomaticRelation, SimpleHistoryAdmin)
