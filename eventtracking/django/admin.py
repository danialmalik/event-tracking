from django.contrib import admin
from django.apps import apps

from eventtracking.django.models import RegExFilter
# RegExFilter = apps.get_model('eventtracking_django', 'RegExFilter')

class RegExFilterAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        has_permission = super().has_add_permission(request)

        if has_permission and RegExFilter.objects.exists():
            return False

        return has_permission


admin.site.register(RegExFilter, RegExFilterAdmin)
