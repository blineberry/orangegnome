from bs4 import BeautifulSoup
from django import template
from django.template.defaultfilters import slugify, stringfilter

register = template.Library()

def get_filename(src:str)->str:
    return src.split("/")[-1].split(".")[0]

@register.filter(is_safe=True)
@stringfilter
def auto_id(value):
    soup = BeautifulSoup(value, "html.parser")

    els = soup.find_all(['h1','h2','h3','h4','h5','h6','img'])

    for e in els:
        if e.get("id") is not None:
            continue

        if e.name == "img":
            src = e.get("src")
            if src is not None:
                e["id"] = f'img-{slugify(get_filename(src))}'
            continue

        text = e.text
        if text.strip() != "":
            e["id"] = slugify(e.text)

    return str(soup)