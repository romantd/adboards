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
def index(request):
    ads = Ad.objects.filter(is_active=True)[:10]
    context = {'ads':ads}
    return render(request, 'main/index.html', context)
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
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from .models import Ad, Conversation
from .forms import MessageForm
import logging

logger = logging.getLogger(__name__)

def detail(request, category_pk, pk):
    try:
        ad = get_object_or_404(Ad, pk=pk)
        ais = ad.additionalimage_set.all()
    except Exception as e:
        logger.error(f"Ad not found: category_pk={category_pk}, pk={pk}, error={e}")
        return render(request, '404.html', status=404)
    
    form = None
    context = {
        'ad': ad,
        'ais': ais,
        'form': form,
        'is_author': False,
        'conversations': [],
        'messages': [],
        'user': request.user,
    }

    if request.user.is_authenticated:
        form = MessageForm(request.POST or None)
        
        if request.method == 'POST' and form.is_valid():
            message = form.save(commit=False)
            # Перевірка існування розмови
            conversation = Conversation.objects.filter(ad=ad, buyer=request.user).first()
            if not conversation:
                # Створення нової розмови
                conversation = Conversation.objects.create(ad=ad, buyer=request.user, seller=ad.author)
            
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect('main:detail', category_pk=category_pk, pk=pk)
    
        if request.user == ad.author:
            # User is an author
            conversations = Conversation.objects.filter(ad=ad, seller=request.user)
            buyers = []
            for conversation in conversations:
                if conversation.buyer != request.user:
                    buyers.append({'buyer': conversation.buyer, 'conversation': conversation})
            context.update({
                'conversations': conversations,
                'form': form,
                'is_author': True,
                'buyers': buyers,
            })
        else:
            # User is a buyer
            conversation = Conversation.objects.filter(ad=ad, buyer=request.user).first()
            umessages = conversation.messages.all() if conversation else []
            context.update({
                'conversations': [conversation] if conversation else [],
                'form': form,
                'umessages': messages,
            })

    return render(request, 'main/detail.html', context)
# Profile
@login_required
def profile(request):
    ads = Ad.objects.filter(author=request.user.pk)
    context = {'ads': ads}
    return render(request, 'main/profile.html', context)

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
    form = None
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
    return render(request, 'main/profile_ad_change.html', context)

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


#Conversation
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView
from .models import Conversation, Message, Ad
from .forms import MessageForm

@login_required
def start_conversation(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            conversation = Conversation.objects.create(ad=ad, seller=ad.author, buyer=request.user)
            Message.objects.create(conversation=conversation, sender=request.user, text=form.cleaned_data['text'])
            return redirect('conversation_detail', pk=conversation.pk)
    else:
        form = MessageForm()
    return render(request, 'main/start_conversation.html', {'form': form, 'ad': ad})

class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'main/conversation_list.html'

    def get_queryset(self):
        return Conversation.objects.filter(seller=self.request.user) | Conversation.objects.filter(buyer=self.request.user)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from .models import Conversation
from .forms import MessageForm

class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = 'main/conversation_detail.html'
    context_object_name = 'conversation'

    def get_object(self, queryset=None):
        # Отримання об'єкта розмови з перевіркою доступу
        obj = get_object_or_404(Conversation, pk=self.kwargs['pk'])
        if self.request.user != obj.buyer and self.request.user != obj.seller:
            raise Http404("No conversation found matching the query")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm()
        context['umessages'] = self.object.messages.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = self.object
            message.sender = request.user
            message.save()
            return self.get(request, *args, **kwargs)
        else:
            return self.render_to_response(self.get_context_data(form=form))
from django.contrib.auth.decorators import login_required

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Перевірка, чи є користувач учасником розмови
    if request.user != conversation.buyer and request.user != conversation.seller:
        return redirect('main:profile')  # або інша відповідна дія

    umessages = conversation.messages.all()

    context = {
        'conversation': conversation,
        'umessages': messages,
        'user': request.user,
    }

    return render(request, 'main/conversation_detail.html', context)
@login_required
def send_message(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if not conversation.can_access(request.user):
        return redirect('conversation_list')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(conversation=conversation, sender=request.user, text=form.cleaned_data['text'])
            return redirect('conversation_detail', pk=pk)
    return redirect('conversation_detail', pk=pk)