import random

from django import forms
from django.shortcuts import render, redirect
from . import util


class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, empty_value=False)


class CreateEntryForm(forms.Form):
    title = forms.CharField(label="Title", empty_value=False)
    content = forms.CharField(widget=forms.Textarea, empty_value=False)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def show_title(request, title):
    if util.get_entry(title):
        return render(request, "encyclopedia/title.html", {
            "title": title,
            "content": util.get_entry(title)
        })
    else:
        return redirect('error', error="404")


def search(request):
    search_q = request.GET.get("q")
    if util.get_entry(search_q):
        return redirect('title', title=search_q)
    search_list = []
    for entries in util.list_entries():
        if search_q.casefold() in entries.casefold():
            search_list.append(entries)
    return render(request, "encyclopedia/search.html", {
        "title": "Search",
        "page_h1": "Search result",
        "entries": search_list
        })


def create(request):
    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {
            "title": "Create New Page",
            "page_h1": "Create New Page",
            "form": CreateEntryForm
        })

    form = CreateEntryForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data["title"]
        if util.get_entry(title.casefold()):
            return render(request, "encyclopedia/create.html", {
                "title": "Create New Page",
                "page_h1": "Create New Page",
                "error": "Page already exist",
                "form": CreateEntryForm(request.POST)
            })
    util.save_entry(title, form.cleaned_data["content"])
    return redirect('title', title=title)


def edit(request, title):
    if request.method == "GET":
        form = EditEntryForm(initial={"content": util.get_entry(title)})
        return render(request, "encyclopedia/edit.html", {
            "title": f"{title}",
            "page_h1": f"Edit {title}",
            "form": form
        })

    form = CreateEntryForm(request.POST)
    if form.is_valid():
        util.save_entry(title, form.cleaned_data["content"])
        return redirect('title', title=title)


def random_entry(request):
    return redirect('title', title=random.choice(util.list_entries()))


def error(request, error):
    return render(request, "encyclopedia/error.html")
