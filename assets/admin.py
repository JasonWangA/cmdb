from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from assets import  models
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# Register your models here.
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.UserProfile
        # fields = ('email','token')
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label="Password",
        help_text=("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = models.UserProfile
        # fields = ('email', 'password','is_active', 'is_admin')
        fields = ('email', 'password','is_active',)


    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    # list_display = ('id','email','is_admin','is_active')
    list_display = ('id','email','is_active')
    # list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('department','tel','mobile','memo')}),
        ('API TOKEN info', {'fields': ('token',)}),
        ('Permissions', {'fields': ('is_active','is_admin')}),
        ('账户有效期', {'fields': ('valid_begin_time','valid_end_time')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            #'fields': ('email',  'password1', 'password2','is_active','is_admin')}
            'fields': ('email',  'password1', 'password2','is_active',)}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

#服务类型反向关联资产 所以使用这种方式
class ServerInline(admin.TabularInline):
    model = models.Server
    exclude = ('memo',)
    readonly_fields = ['create_date']
#服务类型反向关联资产 所有使用这种方式
class CPUInline(admin.TabularInline):
    model = models.CPU
    exclude = ('memo',)
    readonly_fields = ['create_date']
#服务类型反向关联资产 所有使用这种方式
class NICInline(admin.TabularInline):
    model = models.NIC
    exclude = ('memo',)
    readonly_fields = ['create_date']

class RAMInline(admin.TabularInline):
    model = models.RAM
    exclude = ('memo',)
    readonly_fields = ['create_date']
class DiskInline(admin.TabularInline):
    model = models.Disk
    exclude = ('memo',)
    readonly_fields = ['create_date']


# class AssetAdmin(admin.ModelAdmin):
#     list_display = ('id','asset_type','name','sn','manufactory','model','management_ip','business_unit','idc')
#     #把反向关联自己的表都显示出来
#     inlines = [ServerInline,CPUInline,RAMInline,DiskInline,NICInline,]
#     search_fields = ['sn',]
class AssetAdmin(admin.ModelAdmin):
    list_display = ('id','asset_type','sn','name','manufactory','management_ip','idc','business_unit','admin','trade_date')
    inlines = [ServerInline,CPUInline,RAMInline,DiskInline,NICInline]
    search_fields = ['sn',]
    # list_filter = ['idc','manufactory','business_unit','asset_type']
    choice_fields = ('asset_type',)
    fk_fields = ('manufactory','idc','business_unit','admin')
    list_per_page = 10
    list_filter = ('asset_type','manufactory','idc','business_unit','admin','trade_date','sn','management_ip')
    dynamic_fk = 'asset_type'
    dynamic_list_display = ('型号','二级资产类型')
    dynamic_choice_fields = ('sub_asset_type',)
#资产
admin.site.register(models.Asset,AssetAdmin)

class CPUadmin(admin.ModelAdmin):
    list_display =('cpu_model','cpu_count','cpu_core_count','memo')
#cpu
admin.site.register(models.CPU,CPUadmin)
class NICadmin(admin.ModelAdmin):
    list_display =('name','sn','model','macaddress','ipaddress')
#网卡
admin.site.register(models.NIC,NICadmin)
#raid
admin.site.register(models.RaidAdaptor)
#内存
admin.site.register(models.RAM)
#IP
#硬盘
admin.site.register(models.Disk)

#设备厂商
admin.site.register(models.Manufactory)
#
#标签
admin.site.register(models.Tags)
#网络设备
admin.site.register(models.NetworkDevice)
#服务
admin.site.register(models.Server)
#系统or软件
admin.site.register(models.Software)
#业务线
admin.site.register(models.BusinessUnit)


#模块
class MoudleInline(admin.TabularInline):
    model = models.Moudle
    extra = 2
    exclude = ('memo',)

class CabinetInline(admin.TabularInline):
    model = models.Cabinet
    exclude = ('memo',)
#机房
class IdcAdmin(admin.ModelAdmin):

    list_display = ('name','contacts','idc_phone','idc_addr','contract','operator','memo')
    inlines = [MoudleInline,]
#机房表
admin.site.register(models.IDC,IdcAdmin)
#机房模块
admin.site.register(models.Moudle)
#机柜表
admin.site.register(models.Cabinet)
#运营商
admin.site.register(models.Operator)
#合同
admin.site.register(models.Contract)
