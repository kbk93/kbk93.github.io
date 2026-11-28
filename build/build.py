#!/usr/bin/env python3
"""Generates the whole static site from build/data/.

Run from the repo root:  python3 build/build.py
To add images: use the private page /admin/ on the live site (it uploads
the image and updates galleries.json and the gallery pages in one commit),
or add entries at the TOP of the matching list in build/data/galleries.json
(newest first; for "arts" just after the first item, which is the hero image),
then rebuild.
"""
import json, os, html, datetime, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "build", "data")
# Version tag on the stylesheet link: when style.css changes, phones load the new one
CSS_V = hashlib.md5(open(os.path.join(ROOT, "assets", "style.css"), "rb").read()).hexdigest()[:8]
WP = "https://benkhalifas.wordpress.com/wp-content/uploads/2026/11/"

SITE = "Ben Khalifa's"
TAGLINE = "Art, writing and web"
LOGO = WP + "logo-ben-khalifas.jpg"

# Contact e-mail addresses. They never appear in clear in the pages:
# each part is reversed and base64-encoded, and site.js rebuilds the
# address only when a visitor taps the button (bots that read the HTML
# get nothing usable).
# Stored already encoded (user, domain): this file is public on GitHub too.
CONTACT = {"karim": ("bWlyYWs=", "bnQuYWZpbGFoa25lYg=="),
           "mehdi": ("NjFhZmlsYWhrbmViaWRoZW0=", "bW9jLmxpYW1n")}

THEMES = [
    ("architecture", "Architecture", WP + "hello-weekend.jpg"),
    ("politics", "Politics", WP + "protesting-the-french-exception.jpg"),
    ("funny", "Funny", WP + "funny-caricature-01.jpg"),
    ("misc", "Misc", WP + "bye-bye-chrome.jpg"),
    # New themes: no cover yet, the hub shows the latest caricature once there is one
    ("social", "Social", None),
    ("it", "IT", None),
    ("work", "Work", None),
    ("huh", "Huh!", None),
    ("junk", "Junk", None),
]

# Collections inside Arts: slug, name, CSS class of the empty cover.
ARTS_COLLECTIONS = [
    ("palestine", "Palestine 🇵🇸", "flag-ps"),
    ("orient", "Orient &amp; miniatures", ""),
    ("patterns", "Patterns &amp; tiles", ""),
    ("mediterranean", "Mediterranean", ""),
    ("cubism", "Cubism", ""),
    ("dada", "Dada &amp; pop", ""),
    ("posters", "Retro posters", ""),
    ("classics", "Classics revisited", ""),
    ("abstract", "Abstract", ""),
    ("sketches", "Sketches", ""),
]
ARTS_INTROS = {
    "palestine": "Pieces for Palestine and its people.",
    "orient": "Miniatures, musicians, arches and old courtyards, in the spirit of Persian and Arab painting.",
    "patterns": "Tiles, carpets, arabesques and calligraphy, turned into repeating patterns.",
    "mediterranean": "Windows on the sea, white towns, gardens and terraces around the Mediterranean.",
    "cubism": "Faces and bodies broken into flat planes, after Picasso and his friends.",
    "dada": "Collages, slogans, brands and odd dreams, in the Dada and pop art tradition.",
    "posters": "Flat colours and clean lines, like old travel posters and Art Deco prints.",
    "classics": "Old masters, marble statues and famous paintings, each with a twist.",
    "abstract": "Shapes, colours and rhythm, with no story to tell.",
    "sketches": "Pencil lines, watercolours and quick street scenes.",
}
ARTS_HOWTO = "AI-generated from Karim's ideas, newest first. Tap any image to open it full screen, then swipe or use the arrows to browse."

POLITICS = {
    "intro": ["Caricatures · Politics", "Caricatures about politics and current events."],
    "items": [{
        "src": WP + "protesting-the-french-exception.jpg",
        "alt": 'Caricature: riot police charge protesters under a banner reading "Protesting the French exception" while two international observers watch through binoculars',
        "title": "Protesting the French exception",
        "caption": "They say “democracy we are..” .. really ?",
    }],
}

# Articles: "blog" goes to /blog/, "deen" to the page و الحمد لله (/alhamdulillah/).
# Same list (posts.json, newest first), told apart by "section". /admin/ writes
# the same markup as below, so keep the two in step when changing it.
DEEN_NAME = "و الحمد لله"
DEEN_FRAME = "/uploads/deen/frame.jpg"
SECTIONS = {
    "blog": {"path": "blog", "label": "Blog", "default_image": ""},
    "deen": {"path": "alhamdulillah", "label": f'<span lang="ar">{DEEN_NAME}</span>', "default_image": DEEN_FRAME},
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

e = html.escape


def nav(active):
    sub = "".join(
        f'<li><a href="/caricatures/{slug}/"{cur(active, "caricatures/" + slug)}>{name}</a></li>'
        for slug, name, _ in THEMES
    )
    arts_sub = "".join(
        f'<li><a href="/arts/{slug}/"{cur(active, "arts/" + slug)}>{name}</a></li>'
        for slug, name, _ in ARTS_COLLECTIONS
    )
    return f"""<nav class="nav" aria-label="Main">
<ul>
<li><a href="/"{cur(active, "home")}>Home</a></li>
<li class="has-sub"><a href="/arts/"{cur(active, "arts")}>Arts</a><ul>{arts_sub}</ul></li>
<li class="has-sub"><a href="/caricatures/"{cur(active, "caricatures")}>Caricatures</a><ul>{sub}</ul></li>
<li><a href="/blog/"{cur(active, "blog")}>Blog</a></li>
<li><a href="/alhamdulillah/"{cur(active, "deen")} lang="ar">{DEEN_NAME}</a></li>
<li><a href="/web-design/"{cur(active, "web-design")}>Web Design</a></li>
<li><a href="/about/"{cur(active, "about")}>About</a></li>
<li><a href="/contact/"{cur(active, "contact")}>Contact</a></li>
<li><a class="ext" href="https://kbkarchitecture.com" target="_blank" rel="noopener">KBK Architecture ↗</a></li>
</ul>
</nav>"""


def cur(active, key):
    return ' aria-current="page"' if active == key else ""


def page(path, title, body, active="", description=""):
    out = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(title, body, active, description))


def render(title, body, active="", description=""):
    full_title = f"{title} – {SITE}" if title else f"{SITE} – {TAGLINE}"
    desc = description or "Karim Ben Khalifa's arts, caricatures and blog, and the websites Mehdi Ben Khalifa builds."
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
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@400;500;600&family=Labrada:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={CSS_V}">
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
<span>© {year} Karim &amp; Mehdi Ben Khalifa · All images on this site are generated by AI, from ideas by Karim Ben Khalifa.</span>
<span><a href="https://kbkarchitecture.com" target="_blank" rel="noopener">KBK Architecture</a> · <a href="/contact/">Contact</a></span>
</div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    return doc


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
        alt = it.get("alt") or it.get("title") or "AI-generated image, idea by Karim Ben Khalifa"
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


def fdate(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"


def post_thumb(p):
    src = p.get("image") or SECTIONS[p.get("section", "blog")]["default_image"]
    if not src:
        return ""
    return thumb(src) if src.startswith("/uploads/") else src + "?w=400&h=400&crop=1"


def list_item(p):
    sec = SECTIONS[p.get("section", "blog")]
    url = f'/{sec["path"]}/{p["slug"]}/'
    t = post_thumb(p)
    imgtag = f'<a href="{url}"><img src="{e(t)}" alt="" loading="lazy"></a>' if t else ""
    exc = f'<p dir="auto">{e(p["excerpt"])}</p>' if p.get("excerpt") else ""
    return (f'<div class="post-item{"" if t else " noimg"}">{imgtag}<div>'
            f'<h2 dir="auto"><a href="{url}">{e(p["title"])}</a></h2>'
            f'<span class="date">{fdate(p["date"])}</span>{exc}</div></div>')


def article(section, title, date, body, desc):
    """Full page of one article. Called with @@…@@ placeholders, it also gives
    /admin/ its template (build/data/shell.json)."""
    sec = SECTIONS[section]
    band = '<div class="deen-band" aria-hidden="true"></div>\n' if section == "deen" else ""
    return render(title, f"""<div class="wrap narrow{" deen" if section == "deen" else ""}">
{band}<article>
<p class="eyebrow"><a href="/{sec["path"]}/">{sec["label"]}</a></p>
<h1 dir="auto">{e(title)}</h1>
<span class="date">{date} · Karim Ben Khalifa</span>
{body}
</article>
<div class="more"><a class="btn outline" href="/{sec["path"]}/">← All articles</a></div>
</div>""", section, desc)


def main():
    g = json.load(open(os.path.join(DATA, "galleries.json"), encoding="utf-8"))
    g.setdefault("politics", POLITICS)
    posts = json.load(open(os.path.join(DATA, "posts.json"), encoding="utf-8"))

    # Home
    page("", "", f"""<div class="wrap">
<section class="hero">
<img src="{WP}kbk-hero.jpg?w=600" alt="Ben Khalifa's logo: purple and pale yellow shapes inside a speech bubble on a mustard background" width="240" height="240">
<div>
<p class="eyebrow">Arts · Caricatures · Writing · Websites</p>
<h1>Two brothers, one site</h1>
<p class="lead">We're Karim and Mehdi Ben Khalifa. This site holds Karim's arts, caricatures and blog, and the websites Mehdi builds.</p>
</div>
</section>
<div class="cards">
<div class="card"><h3><a class="card-title" href="/arts/">Arts</a></h3><p>AI-generated pieces from Karim's ideas, sorted into collections.</p>
<div class="btns"><a class="btn" href="/arts/">See the arts</a></div></div>
<div class="card"><h3><a class="card-title" href="/caricatures/">Caricatures</a></h3><p>Caricatures from Karim's ideas, sorted by theme, newest first.</p>
<div class="btns"><a class="btn" href="/caricatures/">See the caricatures</a></div></div>
<div class="card"><h3><a class="card-title" href="/blog/">Blog</a></h3><p>Karim writes about whatever is on his mind. No single topic.</p>
<div class="btns"><a class="btn" href="/blog/">Read the blog</a></div></div>
<div class="card"><h3 lang="ar"><a class="card-title" href="/alhamdulillah/">{DEEN_NAME}</a></h3><p>Writing about our deen, as a thank-you to Allah for His mercy.</p>
<div class="btns"><a class="btn" href="/alhamdulillah/">Read</a></div></div>
<div class="card"><h3><a class="card-title" href="/web-design/">Websites</a></h3><p>Mehdi builds websites from scratch.</p>
<div class="btns"><a class="btn" href="/web-design/">Web design</a></div></div>
</div>
</div>""", "home")

    # Arts (first item is the hero image)
    for slug, _, _ in ARTS_COLLECTIONS:
        g.setdefault(slug, {"intro": [], "items": []})

    def arts_cover(s, n, cls):
        items = g[s]["items"]
        if not items:
            return f'<span class="cover-empty {cls}">{n}</span>'
        src = items[0]["src"]
        return f'<img src="{e(thumb(src) if src.startswith("/uploads/") else src + "?w=800")}" alt="{n}" loading="lazy">'

    def pieces_count(k):
        return "Coming soon" if k == 0 else f'{k} piece{"s" if k > 1 else ""}'

    collections = "".join(
        f'<a class="theme" href="/arts/{s}/">{arts_cover(s, n, cls)}'
        f'<h3>{n}</h3><small>{pieces_count(len(g[s]["items"]))}</small></a>'
        for s, n, cls in ARTS_COLLECTIONS
    )
    arts = g["arts"]["items"]
    hero = arts[0]  # the rest of g["arts"] is the old flat list, kept as an archive
    page("arts", "Arts", f"""<div class="wrap">
<section class="hero">
<a class="lightbox" href="{e(big(hero['src']))}" data-caption="{e(hero['title'])}"><img src="{e(hero['src'])}?w=600" alt="{e(hero['alt'])}" width="240" height="240"></a>
<div>
<p class="eyebrow">Arts · {len(ARTS_COLLECTIONS)} collections</p>
<p class="lead">AI-generated pieces from Karim's ideas, sorted into collections. Pick one to browse.</p>
</div>
</section>
<div class="collections"><p class="eyebrow">Collections</p><div class="themes">{collections}</div></div>
</div>""", "arts", "AI-generated art from ideas by Karim Ben Khalifa.")

    for s, n, cls in ARTS_COLLECTIONS:
        items = g[s]["items"]
        count = f" · {len(items)} pieces" if len(items) > 1 else ""
        band = f'<div class="band {cls}" aria-hidden="true"></div>\n' if cls else ""
        page(f"arts/{s}", f"{html.unescape(n)} – Arts", f"""<div class="wrap collection">
{band}<p class="eyebrow"><a href="/arts/">Arts</a> · {n}{count}</p>
<h1>{n}</h1>
<p class="lead">{ARTS_INTROS[s]} {ARTS_HOWTO}</p>
{grid(items)}
<div class="more"><a class="btn outline" href="/arts/">← All arts</a></div>
</div>""", "arts/" + s, f"{html.unescape(n)}: AI-generated art from ideas by Karim Ben Khalifa.")

    # Caricatures hub
    def cover(s, n, img):
        items = g[s]["items"]
        src = img or (items[0]["src"] if items else None)
        if not src:
            return f'<span class="cover-empty">{e(n)}</span>'
        return f'<img src="{e(thumb(src) if src.startswith("/uploads/") else src + "?w=800")}" alt="{e(n)} caricatures" loading="lazy">'

    def howmany(k):
        return "Coming soon" if k == 0 else f'{k} caricature{"s" if k > 1 else ""}'

    cards = "".join(
        f'<a class="theme" href="/caricatures/{s}/">{cover(s, n, img)}'
        f'<h3>{n}</h3><small>{howmany(len(g[s]["items"]))}</small></a>'
        for s, n, img in THEMES
    )
    page("caricatures", "Caricatures", f"""<div class="wrap">
<p class="eyebrow">Caricatures · {len(THEMES)} themes</p>
<h1>Caricatures</h1>
<p class="lead">Caricatures generated by AI from Karim Ben Khalifa's ideas, sorted by theme. Pick one to browse.</p>
<div class="themes">{cards}</div>
</div>""", "caricatures", "AI-generated caricatures from ideas by Karim Ben Khalifa, sorted by theme.")

    intros = {
        "architecture": "Life as an architect: school, the office, software, clients. Tap any caricature to open it full screen, then swipe or use the arrows.",
        "politics": "Caricatures about politics and current events.",
        "funny": "The lighter side: everyday absurdities, tech fails and family chaos. Tap any caricature to open it full screen, then swipe or use the arrows.",
        "misc": "Everything else: caricatures that don't fit in one theme. Tap any caricature to open it full screen, then swipe or use the arrows.",
        "social": "People, social media and the way we live together. Tap any caricature to open it full screen, then swipe or use the arrows.",
        "it": "Computers, apps, updates and the rest of our digital troubles. Tap any caricature to open it full screen, then swipe or use the arrows.",
        "work": "Bosses, meetings, deadlines and the office in general. Tap any caricature to open it full screen, then swipe or use the arrows.",
        "huh": "The ones that leave you puzzled. Tap any caricature to open it full screen, then swipe or use the arrows.",
        "junk": "Quick sketches, odd ideas and leftovers. Tap any caricature to open it full screen, then swipe or use the arrows.",
    }
    for s, n, _ in THEMES:
        items = g[s]["items"]
        count = f" · {len(items)} caricatures" if len(items) > 1 else ""
        page(f"caricatures/{s}", f"{n} caricatures", f"""<div class="wrap">
<p class="eyebrow">Caricatures · {n}{count}</p>
<h1>{n}</h1>
<p class="lead">{intros[s]}</p>
{grid(items)}
{more_themes(s)}
</div>""", "caricatures/" + s, f"{n} AI-generated caricatures from ideas by Karim Ben Khalifa.")

    # Articles (Blog and و الحمد لله)
    lists = {k: [] for k in SECTIONS}
    for p in posts:
        sec = p.setdefault("section", "blog")
        lists[sec].append(list_item(p))
        body = open(os.path.join(DATA, "posts", p["slug"] + ".html"), encoding="utf-8").read()
        out = os.path.join(ROOT, SECTIONS[sec]["path"], p["slug"], "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(article(sec, p["title"], fdate(p["date"]), body, p.get("excerpt") or p["title"]))
    page("blog", "Blog", f"""<div class="wrap narrow">
<p class="eyebrow">Blog</p>
<h1>Blog</h1>
<p class="lead">Karim writes about whatever is on his mind. No single topic.</p>
<div class="post-list">{"".join(lists["blog"])}</div>
</div>""", "blog")

    page("alhamdulillah", DEEN_NAME, f"""<div class="wrap narrow deen">
<section class="deen-frame">
<div class="inner">
<p class="bismillah" lang="ar" dir="rtl">بسم الله الرحمن الرحيم</p>
<h1 class="deen-title" lang="ar" dir="rtl">{DEEN_NAME}</h1>
<p class="lead">A page for our deen, and a small thank-you to Allah for His mercy and for making us His servants. Alhamdulillah.</p>
</div>
</section>
<p>I write here about faith as I live it: what I read, what I learn, and the reminders I need first of all for myself. I'm not a scholar. What is right comes from Allah, and the mistakes are mine. Allah knows best.</p>
<div class="post-list">{"".join(lists["deen"])}</div>
</div>""", "deen", "Writing about our deen by Karim Ben Khalifa, as a tribute to Allah's mercy.")

    # Templates for /admin/, which writes new articles without running this script
    P = "@@"
    shell = {k: article(k, P + "TITLE" + P, P + "DATE" + P, P + "BODY" + P, P + "DESC" + P) for k in SECTIONS}
    with open(os.path.join(DATA, "shell.json"), "w", encoding="utf-8") as f:
        json.dump(shell, f, ensure_ascii=False, indent=1)

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
<a class="lightbox" href="{WP}about-hero.jpg?w=1600"><img src="{WP}about-hero.jpg?w=1200" alt="Two AI-generated images from ideas by Karim Ben Khalifa, side by side: a cheerful man jumping with his arms up in green and pink colours, and a pencil sketch of a faceless man waving on lined notebook paper" style="border-radius:16px" width="1024" height="576"></a>
<h2>Karim</h2>
<p>I'm Karim Ben Khalifa, an architect. I worked in Paris until 2023, then opened my own practice, <a href="https://kbkarchitecture.com" target="_blank" rel="noopener">KBK Architecture</a>, in Bizerte, Tunisia.</p>
<p>This site isn't about architecture, though. It's where I put my arts and caricatures and write about whatever I feel like writing about.</p>
<p>All the images on this site, caricatures and art alike, are generated by AI. The ideas behind them are mine.</p>
<h2>Mehdi</h2>
<p>Mehdi Ben Khalifa is my brother, and he's very good at what he does: creating websites. He's the one who built the KBK Architecture site.</p>
<p>More about his work on the <a href="/web-design/">Web Design</a> page.</p>
</div>""", "about")

    # Contact
    def mail_button(who, label, subject):
        user, domain = CONTACT[who]
        return f"""<p class="mail-wrap"><a class="btn mail" href="/contact/#{who}" data-u="{user}" data-d="{domain}" data-s="{e(subject)}">{label}</a></p>
<p class="mail-shown" hidden></p>"""
    page("contact", "Contact", f"""<div class="wrap narrow">
<h1>Contact</h1>
<p class="lead">There are two of us. Write to the one you need.</p>
<h2 id="karim">Karim: arts, caricatures and blog</h2>
<p>A question about an image, something you read on the blog, or anything else.</p>
{mail_button("karim", "Email Karim", "Hello Karim (benkhalifa.tn)")}
<h2 id="mehdi">Mehdi: websites</h2>
<p>Need a new website? Tell Mehdi a bit about your project.</p>
{mail_button("mehdi", "Email Mehdi", "Website project (benkhalifa.tn)")}
<p class="small">Tapping a button opens your mail app with a new message ready to write.</p>
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
