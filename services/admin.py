from django.contrib import admin
from .models import BirthChartRequest, RitualRequest, WitchQuestion, DreamSubmission, MediumContactRequest

admin.site.register(BirthChartRequest)
admin.site.register(RitualRequest)
admin.site.register(WitchQuestion)
admin.site.register(DreamSubmission)
admin.site.register(MediumContactRequest)

