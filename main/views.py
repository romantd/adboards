from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

def index(request):
    ads = Ad.objects.filter(is_active=True)[:10]
    context = {'ads':ads}
    return render(request, 'main/index.html', context)

class BBLoginView(LoginView):
    template_name = 'main/login.html'


class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'

@login_required
def profile(request):
    return render(request, 'main/profile.html')

from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from .models import AdvUser
from .forms import ChangeUserInfoForm

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/edit_profile.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'User data changed successfully'

    def setup(self, request: HttpRequest, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)
    

from django.contrib.auth.views import PasswordChangeView
class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Password changed successfully'


from django.views.generic.edit import CreateView
from.forms import RegisterUserForm
class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')

from django.views.generic.base import TemplateView
class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


from django.core.signing import BadSignature
from .utilities import signer
def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


# User delete
from django.views.generic.edit import DeleteView
from django.contrib.auth import logout
from django.contrib import messages
class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')
    
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'User deleted successfully')
        return super().post(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

#Ads
from django.core.paginator import Paginator
from django.db.models import Q
from .models import SubCategory, Ad, SuperCategory
from .forms import SearchForm
def by_category(request, pk):
    try:
        category = get_object_or_404(SubCategory, pk=pk)
        ads = Ad.objects.filter(is_active=True, category=pk)
        if 'keyword' in request.GET:
            keyword = request.GET['keyword']
            q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
            ads = ads.filter(q)
        else:
            keyword = ''
        form = SearchForm(initial={'keyword': keyword})
        paginator = Paginator(ads, 10)
        if 'page' in request.GET:
            page_num = request.GET['page']
        else:
            page_num = 1
        page = paginator.get_page(page_num)
        context = {'category':category, 'page':page, 'ads':page.object_list, 'form':form}
        return render(request, 'main/by_category.html', context)        
    except:
        pass
        category = get_object_or_404(SuperCategory, pk=pk)
        ads = Ad.objects.filter(is_active=True, category__parent=pk)
        if 'keyword' in request.GET:
            keyword = request.GET['keyword']
            q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
            ads = ads.filter(q)
        else:
            keyword = ''
        form = SearchForm(initial={'keyword': keyword})
        paginator = Paginator(ads, 6)
        if 'page' in request.GET:
            page_num = request.GET['page']
        else:
            page_num = 1
        page = paginator.get_page(page_num)
        context = {'category':category, 'page':page, 'ads':page.object_list, 'form':form}
        return render(request, 'main/by_category.html', context)    
    
    

#Details
def detail(request, category_pk, pk):
    ad = get_object_or_404(Ad, pk=pk)
    ais = ad.additionalimage_set.all()
    context = {'ad':ad, 'ais':ais}
    return render(request, 'main/detail.html', context)

#Profile
@login_required
def profile(request):
    ads = Ad.objects.filter(author=request.user.pk)
    context = {'ads':ads}
    return render(request, 'main/profile.html', context)


from django.shortcuts import redirect
from .forms import AdForm, AIFormSet
@login_required
def profile_ad_add(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=ad)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Ad added successfully')
                return redirect('main:profile')
            return redirect('main:profile')
    else:
        form = AdForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_ad_add.html', context)


@login_required
def profile_ad_change(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            ad = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=ad)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Ad saved')
                return redirect('main:profile')
    else:
        form = AdForm(instance=ad)
        formset = AIFormSet(instance=ad)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_ad_change.html')

@login_required
def profile_ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        ad.delete()
        messages.add_message(request, messages.SUCCESS, 'Ad deleted successfully')
        return redirect('main:profile')
    else:
        context = {'ad':ad}
        return render(request, 'main/profile_ad_delete.html', context)
    
#NEED_WRITE
@login_required
def profile_ad_detail(request, category_pk, pk):
    ad = get_object_or_404(Ad, pk=pk)
    ais = ad.additionalimage_set.all()
    context = {'ad':ad, 'ais':ais}
    return render(request, 'main/profile_ad_detail.html', context)


