from django.contrib import admin


class MyAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = []
        app_list.append({
            'has_module_perms': True,
            'models': [
                {
                    'add_url': '/admin/inventory/object/add/',
                    'admin_url': '/admin/inventory/object/',
                    'name': 'Объекты',
                    'object_name': 'Object',
                    'perms': {'add': True,
                              'change': True,
                              'delete': True,
                              'view': True},
                    'view_only': False
                },
                {
                    'add_url': '/admin/inventory/instance/add/',
                    'admin_url': '/admin/inventory/instance/',
                    'name': 'Оборудование',
                    'object_name': 'Instance',
                    'perms': {'add': True,
                              'change': True,
                              'delete': True,
                              'view': True},
                    'view_only': False
                },
                {
                    'add_url': '/admin/inventory/consumable/add/',
                    'admin_url': '/admin/inventory/consumable/',
                    'name': 'Расходники',
                    'object_name': 'Consumable',
                    'perms': {'add': True,
                              'change': True,
                              'delete': True,
                              'view': True},
                    'view_only': False
                },
                {
                    'add_url': '/admin/inventory/contractnumber/add/',
                    'admin_url': '/admin/inventory/contractnumber/',
                    'name': 'Номера контрактов',
                    'object_name': 'ContractNumber',
                    'perms': {'add': True,
                              'change': True,
                              'delete': True,
                              'view': True},
                    'view_only': False
                },
            ],
            'name': 'Основные действия'
        })
        app_list.extend(super().get_app_list(request))
        return app_list


site = MyAdminSite()
admin.site = site

from django.contrib.auth.admin import User, UserAdmin, Group, GroupAdmin

site.register(User, UserAdmin)
site.register(Group, GroupAdmin)
