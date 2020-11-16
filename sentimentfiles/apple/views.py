from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from django.shortcuts import render


from apple.forms import UserForm,UserProfileInfoForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Review

# import tweepy
# from textblob import TextBlob
import pandas as pd
import numpy as np
# import pickle
from sklearn.model_selection import train_test_split


df = pd.read_csv('tweets.csv')


text = df['tweet_text']

target = df['is_there_an_emotion_directed_at_a_brand_or_product']

#print(len(text))

target = target[pd.notnull(text)]
text = text[pd.notnull(text)]


count_vect = CountVectorizer()
count_vect.fit(text)
l_count = len(count_vect.vocabulary_)
#print(count_vect.vocabulary_)
counts = count_vect.transform(text)
#print(counts)


nb = MultinomialNB()
nb.fit(counts, target)


# split into train and test sets
x_train, x_test, y_train, y_test = train_test_split(
    counts, target, train_size=0.80, test_size=0.20, random_state=0)

nb = MultinomialNB()
nb.fit(x_train, y_train)

y_predicted = nb.predict(x_test)
print(y_predicted)
#print(x_train, y_train)
#print(x_test, y_test)

#accuracy = accuracy_score(y_test, y_predicted)
accuracy = accuracy_score(y_test, y_predicted)

confuse = confusion_matrix(y_test, y_predicted)
print(confuse)


report = classification_report(y_test, y_predicted)
print(report)


def home(request):
    sentiment = nb.predict(count_vect.transform(["I hate iphones"]))

    context = {'sentiment': sentiment, 'accuracy': accuracy,
               'confuse': confuse, 'report': report, 'counts': l_count}
    #sentiment = nb.predict(count_vect.transform(['I hate my iphone']))
    return render(request, 'apple/home.html', context)


def new_page(request):
    data = request.GET['fulltextarea']
    print(nb.predict(count_vect.transform([data])))
    sentiment = nb.predict(count_vect.transform([data]))

    review = Review()
    review.text = data
    review.value = sentiment
    review.save()

    context = {'sentiment': sentiment, 'accuracy': accuracy,
               'confuse': confuse, 'data': data, 'report': report, 'counts': l_count}

    return render(request, 'apple/display.html', context)


def index(request):
    return render(request, 'apple/index.html')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                print('found it')
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request, 'apple/registration.html',
                  {'user_form': user_form,
                           'profile_form': profile_form,
                           'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(
                username, password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'apple/login.html', {})
