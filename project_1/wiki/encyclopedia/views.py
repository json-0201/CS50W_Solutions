from markdown2 import Markdown
from django.shortcuts import render
import random

from . import util

def convert_md_to_html(entry):
    content = util.get_entry(entry)
    markdowner = Markdown()
    if content:
        return markdowner.convert(content)
    else:
        return None


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
        })


def entry(request, entry):
    content_html = convert_md_to_html(entry)
    if content_html:
        return render(request, "encyclopedia/entry.html", {
            "entry": entry,
            "content": content_html,
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": f"\"{entry}\" was not found!",
        })


def search(request):
    if request.method == "POST":
        search = request.POST["q"]
        content_html = convert_md_to_html(search)

        if content_html:
            return render(request, "encyclopedia/entry.html", {
                "entry": search,
                "content": content_html,
                })
        
        else:
            suggestions = [entry for entry in util.list_entries() if search.lower() in entry.lower()]
            return render(request, "encyclopedia/error.html", {
                "message": f"\"{search}\" was not found! Did you mean to type...",
                "suggestions": suggestions,
            })


def new_page(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]

        if util.get_entry(title):
            return render(request, "encyclopedia/error.html", {
                "message": f"\"{title}\" already exists in the encyclopedia!"
            })
        else:
            util.save_entry(title, content)
            content_html = convert_md_to_html(title)
            return render(request, "encyclopedia/entry.html", {
                "entry": title,
                "content": content_html,
            })
    else:
        return render(request, "encyclopedia/new.html")


def edit_page(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content,
        })


def save_page(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        util.save_entry(title, content)
        return render(request, "encyclopedia/entry.html", {
            "entry": title,
            "content": convert_md_to_html(title),
        })


def random_page(request):
    title_random = random.choice(util.list_entries())
    return render(request, "encyclopedia/entry.html", {
        "entry": title_random,
        "content": convert_md_to_html(title_random),
    })