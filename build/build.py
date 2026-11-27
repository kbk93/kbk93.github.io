#!/usr/bin/env python3
"""Generates the whole static site from build/data/.

Run from the repo root:  python3 build/build.py
To add drawings: use the private page /admin/ on the live site (it uploads
the image and updates galleries.json and the gallery pages in one commit),
or add entries at the TOP of the matching list in build/data/galleries.json
(newest first; for "arts" just after the first item, which is the hero image),
then rebuild.
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "build", "data")
WP = "https://benkhalifas.wordpress.com/wp-content/uploads/2026/11/"

SITE = "Ben Khalifa's"
TAGLINE = "Art, writing and web"
LOGO = WP + "logo-ben-khalifas.jpg"

# E-mail addresses that receive the contact forms (FormSubmit, free).
CONTACT = {"karim": "", "mehdi": ""}

THEMES = [
    ("architecture", "Architecture", WP + "hello-weekend.jpg"),
    ("politics", "Politics", WP + "protesting-the-french-exception.jpg"),
    ("funny", "Funny", WP + "funny-caricature-01.jpg"),
    ("misc", "Misc", WP + "bye-bye-chrome.jpg"),
]

POLITICS = {
    "intro": ["Caricatures · Politics", "Caricatures about politics and current events."],
    "items": [{
        "src": WP + "protesting-the-french-exception.jpg",
        "alt": 'Caricature: riot police charge protesters under a banner reading "Protesting the French exception" while two international observers watch through binoculars',
        "title": "Protesting the French exception",
        "caption": "They say “democracy we are..” .. really ?",
    }],
}

e = html.escape


def nav(active):
    sub = "".join(
        f'<li><a href="/caricatures/{slug}/"{cur(active, "caricatures/" + slug)}>{name}</a></li>'
        for slug, name, _ in THEMES
    )
    return f"""<nav class="nav" aria-label="Main">
<ul>
<li><a href="/"{cur(active, "home")}>Home</a></li>
<li><a href="/arts/"{cur(active, "arts")}>Arts</a></li>
<li class="has-sub"><a href="/caricatures/"{cur(active, "caricatures")}>Caricatures</a><ul>{sub}</ul></li>
<li><a href="/blog/"{cur(active, "blog")}>Blog</a></li>
<li><a href="/web-design/"{cur(active, "web-design")}>Web Design</a></li>
<li><a href="/about/"{cur(active, "about")}>About</a></li>
<li><a href="/contact/"{cur(active, "contact")}>Contact</a></li>
<li><a class="ext" href="https://kbkarchitecture.com" target="_blank" rel="noopener">KBK Architecture ↗</a></li>
</ul>
</nav>"""


def cur(active, key):
    return ' aria-current="page"' if active == key else ""


def page(path, title, body, active="", description=""):
    full_title = f"{title} – {SITE}" if title else f"{SITE} – {TAGLINE}"
    desc = description or "Karim Ben Khalifa's drawings, caricatures and blog, and the websites Mehdi Ben Khalifa builds."
    year = datetime.date.today().year
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{LOGO}">
<link rel="icon" href="{LOGO}?w=64">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Labrada:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site-header">
<div class="wrap header-inner">
<a class="brand" href="/"><img src="{LOGO}?w=96" alt="" width="42" height="42"><span>{SITE}</span></a>
<button class="menu-toggle" aria-label="Menu" aria-expanded="false"><span></span></button>
{nav(active)}
</div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<span>© {year} Karim &amp; Mehdi Ben Khalifa</span>
<span><a href="https://kbkarchitecture.com" target="_blank" rel="noopener">KBK Architecture</a> · <a href="/contact/">Contact</a></span>
</div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    out = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)


def thumb(src):
    # Images added from /admin/ live in the repo, with a ready-made square thumbnail
    if src.startswith("/uploads/"):
        return src.rsplit(".", 1)[0] + "-thumb.jpg"
    return src + "?w=480&h=480&crop=1"


def big(src):
    if src.startswith("/uploads/"):
        return src
    return src + "?w=1600"


def grid(items):
    cells = []
    for it in items:
        cap = it.get("caption") or ""
        alt = it.get("alt") or it.get("title") or "Drawing by Karim Ben Khalifa"
        cells.append(
            f'<a href="{e(big(it["src"]))}" data-caption="{e(cap)}">'
            f'<img src="{e(thumb(it["src"]))}" alt="{e(alt)}" loading="lazy" width="240" height="240"></a>'
        )
    return '<div class="grid">' + "".join(cells) + "</div>"


def more_themes(skip):
    btns = "".join(
        f'<a class="btn outline" href="/caricatures/{s}/">{n}</a>' for s, n, _ in THEMES if s != skip
    )
    return f'<div class="more"><p class="eyebrow">More caricatures</p><div class="btns">{btns}</div></div>'


def main():
    g = json.load(open(os.path.join(DATA, "galleries.json"), encoding="utf-8"))
    g.setdefault("politics", POLITICS)
    posts = json.load(open(os.path.join(DATA, "posts.json"), encoding="utf-8"))

    # Home
    page("", "", f"""<div class="wrap">
<section class="hero">
<img src="{WP}kbk-hero.jpg?w=600" alt="Ben Khalifa's logo: purple and pale yellow shapes inside a speech bubble on a mustard background" width="240" height="240">
<div>
<p class="eyebrow">Drawings · Writing · Websites</p>
<h1>Two brothers, one site</h1>
<p class="lead">We're Karim and Mehdi Ben Khalifa. This site holds Karim's drawings and blog, and the websites Mehdi builds.</p>
</div>
</section>
<div class="cards">
<div class="card"><h3>Drawings</h3><p>Karim's drawings and caricatures, added as he finishes them.</p>
<div class="btns"><a class="btn" href="/arts/">See the arts</a><a class="btn outline" href="/caricatures/">Caricatures</a></div></div>
<div class="card"><h3>Blog</h3><p>Karim writes about whatever is on his mind. No single topic.</p>
<div class="btns"><a class="btn" href="/blog/">Read the blog</a></div></div>
<div class="card"><h3>Websites</h3><p>Mehdi builds websites from scratch.</p>
<div class="btns"><a class="btn" href="/web-design/">Web design</a></div></div>
</div>
</div>""", "home")

    # Arts (first item is the hero image)
    arts = g["arts"]["items"]
    hero, pieces = arts[0], arts[1:]
    page("arts", "Arts", f"""<div class="wrap">
<section class="hero">
<a class="lightbox" href="{e(big(hero['src']))}" data-caption="{e(hero['title'])}"><img src="{e(hero['src'])}?w=600" alt="{e(hero['alt'])}" width="240" height="240"></a>
<div>
<p class="eyebrow">Arts · {len(pieces)} pieces</p>
<p class="lead">Drawings, sketches and digital pieces, newest first. Tap any image to open it full screen, then swipe or use the arrows to browse.</p>
</div>
</section>
{grid(pieces)}
</div>""", "arts", "Drawings, sketches and digital pieces by Karim Ben Khalifa.")

    # Caricatures hub
    cards = "".join(
        f'<a class="theme" href="/caricatures/{s}/"><img src="{img}?w=800" alt="{n} caricatures" loading="lazy">'
        f'<h3>{n}</h3><small>{len(g[s]["items"])} drawing{"s" if len(g[s]["items"]) > 1 else ""}</small></a>'
        for s, n, img in THEMES
    )
    page("caricatures", "Caricatures", f"""<div class="wrap">
<p class="eyebrow">Caricatures · {len(THEMES)} themes</p>
<h1>Caricatures</h1>
<p class="lead">Caricatures by Karim Ben Khalifa, sorted by theme. Pick one to browse.</p>
<div class="themes">{cards}</div>
</div>""", "caricatures", "Caricatures by Karim Ben Khalifa, sorted by theme.")

    intros = {
        "architecture": "Life as an architect: school, the office, software, clients. Tap any drawing to open it full screen, then swipe or use the arrows.",
        "politics": "Caricatures about politics and current events.",
        "funny": "The lighter side: everyday absurdities, tech fails and family chaos. Tap any drawing to open it full screen, then swipe or use the arrows.",
        "misc": "Everything else: caricatures that don't fit in one theme. Tap any drawing to open it full screen, then swipe or use the arrows.",
    }
    for s, n, _ in THEMES:
        items = g[s]["items"]
        count = f" · {len(items)} drawings" if len(items) > 1 else ""
        page(f"caricatures/{s}", f"{n} caricatures", f"""<div class="wrap">
<p class="eyebrow">Caricatures · {n}{count}</p>
<h1>{n}</h1>
<p class="lead">{intros[s]}</p>
{grid(items)}
{more_themes(s)}
</div>""", "caricatures/" + s, f"{n} caricatures by Karim Ben Khalifa.")

    # Blog
    items = []
    for p in posts:
        d = datetime.date.fromisoformat(p["date"]).strftime("%B %-d, %Y")
        imgtag = f'<a href="/blog/{p["slug"]}/"><img src="{p["image"]}?w=400&h=400&crop=1" alt="" loading="lazy"></a>' if p["image"] else ""
        exc = f'<p>{e(p["excerpt"])}</p>' if p["excerpt"] else ""
        items.append(f'<div class="post-item{"" if p["image"] else " noimg"}">{imgtag}<div>'
                     f'<h2><a href="/blog/{p["slug"]}/">{e(p["title"])}</a></h2>'
                     f'<span class="date">{d}</span>{exc}</div></div>')
        body = open(os.path.join(DATA, "posts", p["slug"] + ".html"), encoding="utf-8").read()
        page(f"blog/{p['slug']}", p["title"], f"""<div class="wrap narrow">
<article>
<p class="eyebrow"><a href="/blog/">Blog</a></p>
<h1>{e(p["title"])}</h1>
<span class="date">{d} · Karim Ben Khalifa</span>
{body}
</article>
<div class="more"><a class="btn outline" href="/blog/">← All posts</a></div>
</div>""", "blog", p["excerpt"] or p["title"])
    page("blog", "Blog", f"""<div class="wrap narrow">
<p class="eyebrow">Blog</p>
<h1>Blog</h1>
<p class="lead">Karim writes about whatever is on his mind. No single topic.</p>
<div class="post-list">{"".join(items)}</div>
</div>""", "blog")

    # Web design
    page("web-design", "Web Design", """<div class="wrap narrow">
<p class="eyebrow">Mehdi Ben Khalifa</p>
<h1>Web Design</h1>
<p class="lead">Mehdi Ben Khalifa builds websites from scratch, designed around what you need to show and the people you want to reach.</p>
<h2>Website creation</h2>
<p>From the first sketch to the site going live: structure, design, pages and content, all set up so it works well on a phone as on a computer.</p>
<h2>Recent work</h2>
<p><a href="https://kbkarchitecture.com" target="_blank" rel="noopener">KBK Architecture</a>, an architecture practice in Bizerte, Tunisia. Mehdi designed and built the site.</p>
<div class="btns"><a class="btn" href="/contact/#mehdi">Contact Mehdi</a></div>
</div>""", "web-design", "Mehdi Ben Khalifa builds websites from scratch.")

    # About
    page("about", "About", f"""<div class="wrap narrow">
<a class="lightbox" href="{WP}about-hero.jpg?w=1600"><img src="{WP}about-hero.jpg?w=1200" alt="Two drawings by Karim Ben Khalifa side by side: a cheerful man jumping with his arms up in green and pink colours, and a pencil sketch of a faceless man waving on lined notebook paper" style="border-radius:16px" width="1024" height="576"></a>
<h2>Karim</h2>
<p>I'm Karim Ben Khalifa, an architect. I worked in Paris until 2023, then opened my own practice, <a href="https://kbkarchitecture.com" target="_blank" rel="noopener">KBK Architecture</a>, in Bizerte, Tunisia.</p>
<p>This site isn't about architecture, though. It's where I put my drawings and write about whatever I feel like writing about.</p>
<h2>Mehdi</h2>
<p>Mehdi Ben Khalifa is my brother, and he's very good at what he does: creating websites. He's the one who built the KBK Architecture site.</p>
<p>More about his work on the <a href="/web-design/">Web Design</a> page.</p>
</div>""", "about")

    # Contact
    def form(who, subject):
        email = CONTACT[who]
        if not email:
            return '<p><em>Form coming soon.</em></p>'
        return f"""<form class="contact" action="https://formsubmit.co/{email}" method="POST">
<input type="hidden" name="_subject" value="{e(subject)}">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_next" value="/contact/thanks/">
<input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
<label>Name<input type="text" name="name" required></label>
<label>Email<input type="email" name="email" required></label>
<label>Message<textarea name="message" required></textarea></label>
<button class="btn" type="submit">Send</button>
</form>"""
    page("contact", "Contact", f"""<div class="wrap narrow">
<h1>Contact</h1>
<p class="lead">There are two of us, so there are two forms. Pick the one that fits.</p>
<h2 id="karim">Karim: drawings and blog</h2>
<p>A question about a drawing, something you read on the blog, or anything else.</p>
{form("karim", "New message for Karim (Ben Khalifa's)")}
<h2 id="mehdi">Mehdi: websites</h2>
<p>Need a new website? Tell Mehdi a bit about your project.</p>
{form("mehdi", "New website request for Mehdi (Ben Khalifa's)")}
</div>""", "contact")
    page("contact/thanks", "Thanks", """<div class="wrap narrow">
<h1>Thanks!</h1>
<p class="lead">Your message is on its way. We'll get back to you soon.</p>
<div class="btns"><a class="btn" href="/">Back home</a></div>
</div>""", "contact")

    # 404
    page("404tmp", "Page not found", """<div class="wrap narrow">
<h1>Page not found</h1>
<p class="lead">This page doesn't exist, or it moved.</p>
<div class="btns"><a class="btn" href="/">Back home</a></div>
</div>""")
    os.replace(os.path.join(ROOT, "404tmp", "index.html"), os.path.join(ROOT, "404.html"))
    os.rmdir(os.path.join(ROOT, "404tmp"))
    print("Site built.")


if __name__ == "__main__":
    main()
