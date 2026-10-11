# Pulse brand

## The Pulse tab icon

For the Pulse tab in each partner's app.

| File | Use |
|---|---|
| `icons/pulse-24.svg` | The tab at rest |
| `icons/pulse-24-active.svg` | The open tab |
| `icons/pulse-24-color.svg` | Where colour is welcome, such as a menu or an alert |
| `icons/pulse-16.svg`, `-active`, `-color` | The same three, redrawn for 16 px sidebars |

- **Colour.** The icons use `currentColor`, so they take the tab's text colour. Inline the SVG or import it as a component; as a plain `<img>` it renders black.
- **Size.** Use the 16 px files at 16 to 20 px, and the 24 px files at 24 px and up.
- **The peak dot stays.** It's what tells Pulse apart from a generic activity icon.

## The logo

| File | Use |
|---|---|
| `logo/mark.svg` | The app-icon tile. The same in both themes. |
| `logo/wordmark.svg` | "pulse" in `currentColor` |
| `logo/lockup-dark.svg`, `logo/lockup-light.svg` | Mark and wordmark, for dark and light backgrounds |
| `logo/avatar.svg`, `png/avatar-1024.png` | Full-bleed square for the GitHub org avatar. GitHub rounds the corners. |
| `png/` | PNG exports at 1024 px |

## Colours

| | Dark | Light |
|---|---|---|
| Teal | `#2DD4BF` | `#0EA5A4` |
| Indigo | `#818CF8` | `#6366F1` |
| Background | `#0A0F1E` | `#FBFCFE` |
| Text | `#F1F5FB` | `#0B1222` |

## Rebuilding

Every image comes from `src/build.py`; edit it there, not in the SVGs.

```bash
python3 src/build.py --png
```
