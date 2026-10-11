#!/usr/bin/env python3
"""Builds preview/index.html: the README as GitHub's org page shows it, in light, dark and phone width,
plus the brand kit. Only for looking; GitHub never sees this file.

    python3 src/preview.py
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "profile" / "README.md"
OUT = ROOT / "preview" / "index.html"

PICTURE = re.compile(
    r'<picture>\s*<source media="\(prefers-color-scheme: dark\)" srcset="([^"]+)">\s*'
    r'<img ([^>]*?)src="([^"]+)"([^>]*)>\s*</picture>', re.S)


def inline(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def render(md):
    """Just enough Markdown for this README: raw HTML blocks, h3, lists and paragraphs."""
    md = PICTURE.sub(lambda m: f'<img {m[2]}src="{m[3]}" data-light="{m[3]}" data-dark="{m[1]}"{m[4]}>', md)
    out, blocks = [], re.split(r"\n\s*\n", md.strip())
    for block in blocks:
        lines = block.splitlines()
        if block.lstrip().startswith("<"):
            out.append(block)
        elif block.startswith("### "):
            out.append(f"<h3>{inline(block[4:])}</h3>")
        elif all(l.startswith("- ") for l in lines):
            out.append("<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in lines) + "</ul>")
        else:
            out.append(f"<p>{inline(chr(10).join(lines))}</p>")
    body = "\n".join(out)
    return body.replace('src="assets/', 'src="../profile/assets/') \
               .replace('data-light="assets/', 'data-light="../profile/assets/') \
               .replace('data-dark="assets/', 'data-dark="../profile/assets/')


ICONS = ROOT / "brand" / "icons"


def icon(name, cls=""):
    """Inline an icon file, so currentColor picks up the text colour like it will in the apps."""
    svg = (ICONS / f"{name}.svg").read_text().strip()
    return svg.replace("<svg ", f'<svg class="ic {cls}" ', 1)


# Stand-in icons for the other tabs, only so the Pulse tab has neighbours.
HOME = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round">'
        '<path d="M4 10.5L12 4L20 10.5V19Q20 20 19 20H15V14.5H9V20H5Q4 20 4 19Z"/></svg>')
HOME_ON = HOME.replace('fill="none"', 'fill="currentColor"', 1)
CHAT = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round">'
        '<path d="M5 5H19Q20 5 20 6V15Q20 16 19 16H10L6 19.5V16H5Q4 16 4 15V6Q4 5 5 5Z"/></svg>')
SLIDERS = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
           '<path d="M4 7H13M19 7H20M4 17H5M11 17H20"/><circle cx="16" cy="7" r="2.5"/><circle cx="8" cy="17" r="2.5"/></svg>')


def sidebar(theme):
    rows = [(HOME, "Home", False), (icon("pulse-16-active"), "Pulse", True), (CHAT, "Agents", False),
            (SLIDERS, "Settings", False)]
    items = "".join(f'<li class="{"on" if on else ""}">{ic}<span>{label}</span></li>' for ic, label, on in rows)
    return f'<div class="app sb {theme}"><div class="app-title">Your app</div><ul>{items}</ul></div>'


def tabbar(theme, active):
    tabs = [(HOME_ON if active == "home" else HOME, "Home", active == "home"),
            (icon("pulse-24-active") if active == "pulse" else icon("pulse-24"), "Pulse", active == "pulse"),
            (CHAT, "Agents", False), (SLIDERS, "Settings", False)]
    items = "".join(f'<li class="{"on" if on else ""}">{ic}<span>{label}</span></li>' for ic, label, on in tabs)
    return f'<div class="app tb {theme}"><ul>{items}</ul></div>'


def sizes(theme):
    cells = []
    for size in (16, 24):
        for name, label in ((f"pulse-{size}", "Tab"), (f"pulse-{size}-active", "Active tab"),
                            (f"pulse-{size}-color", "Colour")):
            cells.append(f'<div class="cell">{icon(name, f"s{size}")}<small>{label} · {size}</small></div>')
    return f'<div class="sizes {theme}">{"".join(cells)}</div>'


def tab_demo():
    return f"""
<section class="kit">
  <h2>The Pulse tab</h2>
  <p class="note">The icons use <code>currentColor</code>, so each app tints them in its own colours.
  The outline is the tab at rest, the filled one is the open tab. These neighbours are stand-ins.</p>
  <div class="demo">
    {sidebar("light")}{sidebar("dark")}
  </div>
  <div class="demo">
    {tabbar("light", "home")}{tabbar("dark", "pulse")}
  </div>
  <div class="demo">
    {sizes("light")}{sizes("dark")}
  </div>
</section>
"""


KIT = """
<section class="kit">
  <h2>The logo</h2>
  <div class="kit-grid">
    <figure class="on-dark wide"><img src="../brand/logo/lockup-dark.svg" width="380" alt=""><figcaption>Lockup, dark</figcaption></figure>
    <figure class="on-light wide"><img src="../brand/logo/lockup-light.svg" width="380" alt=""><figcaption>Lockup, light</figcaption></figure>
    <figure class="on-dark"><img src="../brand/logo/avatar.svg" width="120" style="border-radius:16px" alt=""><figcaption>Org avatar</figcaption></figure>
    <figure class="on-light"><img src="../brand/logo/mark.svg" width="120" alt=""><figcaption>Mark</figcaption></figure>
    <figure class="on-dark"><span class="row"><img src="../profile/assets/icon-evidence.svg" width="64" alt=""><img src="../profile/assets/icon-limits.svg" width="64" alt=""><img src="../profile/assets/icon-code.svg" width="64" alt=""></span><figcaption>README icons</figcaption></figure>
    <figure class="on-light"><span class="row"><img src="../brand/logo/mark.svg" width="16" alt=""><img src="../brand/logo/mark.svg" width="24" alt=""><img src="../brand/logo/mark.svg" width="32" alt=""><img src="../brand/logo/mark.svg" width="48" alt=""></span><figcaption>Mark at 16, 24, 32, 48</figcaption></figure>
  </div>
</section>
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Org Profile Preview</title>
<style>
  :root { --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --border:#d1d9e0; --link:#0969da; --chrome:#f6f8fa; }
  body.dark { --bg:#0d1117; --fg:#f0f6fc; --muted:#9198a1; --border:#3d444d; --link:#4493f8; --chrome:#151b23; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
    font:16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif; }
  .bar { position:sticky; top:0; z-index:5; display:flex; gap:8px; align-items:center; justify-content:center;
    padding:10px 16px; background:var(--chrome); border-bottom:1px solid var(--border); font-size:13px; }
  .bar button { font:inherit; color:var(--fg); background:transparent; border:1px solid var(--border);
    border-radius:999px; padding:5px 14px; cursor:pointer; }
  .bar button[aria-pressed="true"] { background:var(--fg); color:var(--bg); border-color:var(--fg); }
  .bar .sep { width:1px; height:18px; background:var(--border); margin:0 6px; }
  .org { max-width:1012px; margin:0 auto; padding:32px 16px 0; display:flex; gap:20px; align-items:center; }
  .org img { width:100px; height:100px; border-radius:12px; border:1px solid var(--border); }
  .org h1 { margin:0; font-size:24px; font-weight:600; }
  .org p { margin:4px 0 0; color:var(--muted); font-size:14px; }
  .tabs { max-width:1012px; margin:20px auto 0; padding:0 16px; display:flex; gap:22px; font-size:14px;
    border-bottom:1px solid var(--border); }
  .tabs span { padding:8px 2px 10px; color:var(--muted); }
  .tabs span:first-child { color:var(--fg); font-weight:600; box-shadow:inset 0 -2px 0 #fd8c73; }
  .wrap { max-width:1012px; margin:24px auto 64px; padding:0 16px; }
  .box { border:1px solid var(--border); border-radius:6px; padding:24px; max-width:830px; }
  .box .file { font-size:12px; color:var(--muted); margin:-8px 0 16px; font-family:ui-monospace, SFMono-Regular, Menlo, monospace; }
  body.phone .org, body.phone .tabs, body.phone .wrap { max-width:390px; }
  body.phone .org img { width:64px; height:64px; }
  body.phone .box { padding:16px; }
  .md h3 { font-size:1.25em; font-weight:600; line-height:1.25; margin:24px 0 16px; }
  .md p, .md ul { margin:0 0 16px; }
  .md ul { padding-left:2em; }
  .md li + li { margin-top:.25em; }
  .md img { max-width:100%; box-sizing:content-box; }
  .md img[align=left] { float:left; padding-right:20px; }
  .md a { color:var(--link); }
  .md sub { font-size:75%; color:var(--fg); }
  .md > :first-child { margin-top:0; }
  .kit { max-width:1012px; margin:0 auto 80px; padding:0 16px; }
  .kit h2 { font-size:20px; font-weight:600; padding-bottom:8px; border-bottom:1px solid var(--border); }
  .kit-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:16px; }
  .kit figure { margin:0; border:1px solid var(--border); border-radius:12px; padding:24px 16px 12px;
    display:flex; flex-direction:column; align-items:center; gap:12px; min-height:200px; justify-content:center; }
  .kit figure.wide { grid-column:span 2; }
  .kit .on-dark { background:#0d1117; } .kit .on-light { background:#ffffff; }
  .kit figcaption { font-size:12px; color:#8b949e; }
  .kit .row { display:flex; gap:12px; }
  .kit img { max-width:100%; height:auto; }
  @media (max-width: 560px) { .kit figure.wide { grid-column:span 1; } }
  .kit .note { color:var(--muted); font-size:14px; margin:-4px 0 16px; }
  .kit code { font-size:85%; background:rgba(127,127,127,.15); padding:.15em .4em; border-radius:6px; }
  .demo { display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:16px; margin-bottom:16px; }
  .app { border-radius:14px; padding:14px; font-size:14px; }
  .app.light { background:#ffffff; color:#5b6474; border:1px solid #e3e7ee; --on:#4f46e5; --onbg:#eef0ff; --title:#0b1222; }
  .app.dark { background:#11161f; color:#8b95a7; border:1px solid #232a36; --on:#a5b4fc; --onbg:#1c2140; --title:#f1f5fb; }
  .app ul { list-style:none; margin:0; padding:0; }
  .app .ic { flex:none; }
  .sb .app-title { font-weight:600; color:var(--title); padding:4px 10px 12px; }
  .sb li { display:flex; align-items:center; gap:10px; padding:8px 10px; border-radius:8px; }
  .sb li .ic { width:16px; height:16px; }
  .sb li.on { background:var(--onbg); color:var(--on); font-weight:600; }
  .tb ul { display:flex; justify-content:space-around; }
  .tb li { display:flex; flex-direction:column; align-items:center; gap:4px; font-size:11px; padding:4px 6px; }
  .tb li .ic { width:24px; height:24px; }
  .tb li.on { color:var(--on); font-weight:600; }
  .sizes { display:grid; grid-template-columns:repeat(3, 1fr); gap:8px; border-radius:14px; padding:16px; }
  .sizes.light { background:#ffffff; color:#0b1222; border:1px solid #e3e7ee; }
  .sizes.dark { background:#11161f; color:#f1f5fb; border:1px solid #232a36; }
  .sizes .cell { display:flex; flex-direction:column; align-items:center; gap:8px; padding:10px 0; }
  .sizes small { font-size:11px; opacity:.6; }
  .ic.s16 { width:16px; height:16px; } .ic.s24 { width:24px; height:24px; }
</style>
</head>
<body>
<div class="bar" role="toolbar" aria-label="Preview">
  <button data-theme="light" aria-pressed="true">Light</button>
  <button data-theme="dark" aria-pressed="false">Dark</button>
  <span class="sep"></span>
  <button data-width="desktop" aria-pressed="true">Desktop</button>
  <button data-width="phone" aria-pressed="false">Phone</button>
</div>
<header class="org">
  <img src="../brand/logo/avatar.svg" alt="">
  <div><h1>PulseAgenticTrader</h1><p>Evidence first. Hard limits. Only code trades.</p></div>
</header>
<nav class="tabs"><span>Overview</span><span>Repositories</span><span>Projects</span><span>Packages</span><span>People</span></nav>
<main class="wrap">
  <div class="box">
    <div class="file">PulseAgenticTrader/.github/profile/README.md</div>
    <article class="md">
__README__
    </article>
  </div>
</main>
__KIT__
<script>
  const body = document.body;
  const imgs = [...document.querySelectorAll("img[data-light]")];
  function setTheme(t) {
    body.classList.toggle("dark", t === "dark");
    imgs.forEach(i => { i.src = i.dataset[t]; });
    press("theme", t);
  }
  function press(kind, val) {
    document.querySelectorAll(`[data-${kind}]`).forEach(b => b.setAttribute("aria-pressed", String(b.dataset[kind] === val)));
  }
  document.querySelectorAll("[data-theme]").forEach(b => b.onclick = () => setTheme(b.dataset.theme));
  document.querySelectorAll("[data-width]").forEach(b => b.onclick = () => {
    body.classList.toggle("phone", b.dataset.width === "phone"); press("width", b.dataset.width);
  });
  const start = new URLSearchParams(location.search);
  if (start.get("theme") === "dark") setTheme("dark");
  if (start.get("width") === "phone") { body.classList.add("phone"); press("width", "phone"); }
</script>
</body>
</html>
"""


def main():
    md = README.read_text()
    page = PAGE.replace("__README__", render(md)).replace("__KIT__", tab_demo() + KIT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
