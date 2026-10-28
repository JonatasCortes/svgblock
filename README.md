<h1 align="center">Welcome to svgblock</h1>

<p align="center">
  <img src="assets/block_neon.svg" alt="svgblock example, neon theme" width="800">
</p>

<p align="center">
  <b>Themed and animated text blocks, as .svg files, to make your GitHub profile README beautiful.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-none-2ea44f" alt="No dependencies">
  <img src="https://img.shields.io/badge/themes-50-ff0055" alt="50 themes">
  <img src="https://img.shields.io/badge/entry_animations-6-8A2BE2" alt="6 entry animations">
  <img src="https://img.shields.io/badge/output-SVG-FFB13B?logo=svg&logoColor=white" alt="SVG output">
</p>

---

Do you want your profile README to look like a designed page, instead of plain Markdown text? Then you are in the right place!

svgblock lets you write a **title**, some **paragraphs**, **subsections** and **highlighted words** in a few lines of Python, and turns them into a single `.svg` image: a block with a gradient border, a glowing background and an entrance animation. You pick a **theme** and an **animation**, and the library takes care of the rest: colors, spacing, line breaks and the height of the block.

It is also as light as it can be: **plain Python, no external dependencies** (only the standard library).

## Table of Contents

- [🧭 How a Block Is Built](#how-a-block-is-built)
- [🚀 How to Use](#how-to-use)
  - [Step 1: Install svgblock](#step-1-install-svgblock)
  - [Step 2: Write your first block](#step-2-write-your-first-block)
  - [Step 3: Run the script](#step-3-run-the-script)
  - [Step 4: Show the block in your profile](#step-4-show-the-block-in-your-profile)
  - [Optional: add more blocks](#optional-add-more-blocks)
- [🧱 Building a Block](#building-a-block)
  - [Creating a block](#creating-a-block)
  - [Adding content](#adding-content)
  - [Highlighting words](#highlighting-words)
  - [Saving the result](#saving-the-result)
  - [Animations](#animations)
- [🛠️ Customization](#customization)
  - [What you can change](#what-you-can-change)
  - [Creating your own theme](#creating-your-own-theme)
  - [Constants reference](#constants-reference)
- [🎨 Themes](#themes)
  - [1. Dark Colors](#1-dark-colors)
  - [2. Light Colors (Pastels)](#2-light-colors-pastels)
  - [3. Seasons](#3-seasons)
  - [4. Drinks](#4-drinks)
  - [5. Countries & Geography](#5-countries--geography)
  - [6. Aesthetics & Culture](#6-aesthetics--culture)
  - [7. Classical UI (Dev Themes)](#7-classical-ui-dev-themes)
  - [8. Mythology & Concepts](#8-mythology--concepts)
- [🩺 Troubleshooting](#troubleshooting)

---

## How a Block Is Built

A block is a stack of **components** (titles, subsections and paragraphs) inside a frame. You choose what goes inside, in which order, and the theme chooses every color.

| What you see | What it means |
| --- | --- |
| **Border** | A diagonal gradient between two colors defined by the theme, with rounded corners. |
| **Background** | A radial glow that starts bright in the center and fades to a darker color at the edges. Both colors come from the theme. |
| **Title** | A bold line with a small rounded bar on its left. The text and the bar have their own colors in the theme. |
| **Subsection** | A smaller bold line with a dot on its left. The text and the dot have their own colors in the theme. |
| **Text** | A paragraph. It breaks into lines by itself to fit the width of the block. |
| **Highlighted word** | A word in **bold** and in the highlight color of the theme. |
| **Entrance animation** | The whole block (frame and content) appears when the page loads. The animation is chosen by you, never by the theme. |

Some rules you should know:

- The **height** of the block is calculated automatically from its content.
- Components appear in the order you add them. A block can have **no title, or many**, and they can be anywhere.
- **Text** breaks lines automatically, but **titles and subsections stay on a single line**.
- The **font** is not a setting. It is always Arial, falling back to Helvetica and then to the default sans-serif font of the system. You choose only the **size**.
- **Colors** are never set one by one. They always come from a [theme](#themes).

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>

---

## How to Use

Follow the steps below in order. In the end you will have a block in your profile.

> [!NOTE]
> The blocks are generated **once, on your computer**, and the `.svg` files are committed to your **profile repository**, the special repository named exactly like your GitHub username (for example, `Bob/Bob`). You do not need a GitHub Action or a token.

### Step 1: Install svgblock

You need **Python 3.10 or newer**. To check your version:

```bash
python --version
```

Then install the library directly from this repository:

```bash
pip install git+https://github.com/JonatasCortes/svgblock.git
```

> [!TIP]
> If you prefer, you can also clone the repository and install it from the folder:
>
> ```bash
> git clone https://github.com/JonatasCortes/svgblock.git
> cd svgblock
> pip install .
> ```

### Step 2: Write your first block

In the root of your profile repository, create a file called `generate_blocks.py` with the following content:

```python
from svgblock import Block

(
    Block(theme="neon", width=800, animation="slide-up")
    .title("Hello, I'm Bob")
    .text("I build **small tools** in **pure Python** and I love open source.")
    .subsection("What I am learning")
    .text("Right now I am studying **graph algorithms** and **computer vision**.")
    .save("assets/block.svg")
)
```

Every line of the chain adds something to the block, in order. The last one, `.save(...)`, writes the file (and creates the `assets` folder if it does not exist).

> [!NOTE]
> Wondering what each line does? The [Building a Block](#building-a-block) section explains every option.

### Step 3: Run the script

```bash
python generate_blocks.py
```

When it finishes, the file `assets/block.svg` will exist. Open it in your browser to see the result and the entrance animation. (Reload the page to watch the animation again.)

### Step 4: Show the block in your profile

Add the following to your profile `README.md`:

```html
<p align="center">
  <img src="assets/block.svg" alt="About me" width="800">
</p>
```

Set the `width` value that best suits your README, then **commit and push** both the `assets/block.svg` file and the change in the README.

> [!TIP]
> The `width` in the HTML only resizes the image. The real size of the block is the `width` you passed to `Block(...)`. Use the same value (or a smaller one) so the text stays readable. 🎉

### Optional: add more blocks

You can create as many blocks as you want in the same script, each one saved in its own file and with its own theme and animation:

```python
from svgblock import Block

Block(theme="dracula", animation="fade").title("About me").text("...").save("assets/about.svg")
Block(theme="nord", animation="pop").title("Projects").text("...").save("assets/projects.svg")
```

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>

---

## Building a Block

Everything in svgblock revolves around one class, `Block`. You create it, add content with chained methods and save it.

### Creating a block

```python
Block(theme="red", width=800, animation="fade")
```

| Parameter | Default | What it does |
| --- | --- | --- |
| `theme` | `"red"` | The name of the theme, which defines every color. See [Themes](#themes). |
| `width` | `800` | The width of the block, in pixels. The height is calculated for you. |
| `animation` | `"fade"` | The entrance animation. See [Animations](#animations). |

All parameters are optional. `Block()` alone already works.

### Adding content

| Method | What it adds | Default `font_size` |
| --- | --- | --- |
| `.title(text, font_size)` | A bold title with the side bar. | `20` |
| `.subsection(text, font_size)` | A bold subsection title with a dot. | `17` |
| `.text(text, font_size, highlight)` | A paragraph that breaks lines by itself. | `16` |

You can call each method **any number of times and in any order**. Every method returns the block, so they can be chained:

```python
(
    Block(theme="coffee")
    .title("Projects")
    .text("A few things I built.", font_size=18)
    .subsection("HNSW Character Recognition")
    .text("Train and test your own model.")
    .subsection("Voronoi Stats")
    .text("A card with my languages.")
    .title("Contact")
    .text("Find me on GitHub.")
)
```

### Highlighting words

There are two ways to highlight words, and you can use both in the same paragraph.

**1. With `**` inside the text:**

```python
.text("Build with **pure Python** and no ML libraries.")
```

**2. With the `highlight` list:**

```python
.text("Explore accuracy and a 47-class confusion matrix.", highlight=["accuracy", "47-class"])
```

Highlighted words are drawn in **bold** and in the highlight color of the theme.

A few details:

- The `highlight` list looks for the exact text, **respecting upper and lower case**, and it also matches inside bigger words (`"pure"` matches the beginning of `"pureness"`).
- If two entries overlap (`"pure"` and `"pure Python"`), the longest one wins.
- To write a literal `**` in the text, put a backslash before each asterisk: `\*\*`.

> [!WARNING]
> In a normal Python string, `"\*"` is an invalid escape sequence, and Python 3.12 shows a warning for it. Write the backslash twice (`"\\*\\*"`) or use a raw string (`r"\*\*"`).

### Saving the result

| Method | What it does |
| --- | --- |
| `.save(path)` | Writes the `.svg` file, creating the folders of the path if needed. |
| `.render()` | Returns the SVG as a string, without writing any file. |

### Animations

Choose the entrance animation with the `animation` parameter. It plays once, in 0.8 seconds, when the block appears.

| Name | What it does |
| --- | --- |
| `"fade"` | The block fades in. It is the most discreet one and the default. |
| `"slide-up"` | The block fades in while moving up, entering from below. |
| `"slide-down"` | The block fades in while moving down, entering from above. |
| `"slide-left"` | The block fades in while moving to the left, entering from the right. |
| `"slide-right"` | The block fades in while moving to the right, entering from the left. |
| `"pop"` | The block fades in while growing slightly, from a bit smaller to its final size. |

You can pass the name as a string (`animation="pop"`) or use the `Animation` enum, which gives you autocomplete in your editor:

```python
from svgblock import Animation, Block

Block(animation=Animation.SLIDE_UP)
```

> [!NOTE]
> People who turned on "reduce motion" in their system settings see the block with no animation at all.

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>

---

## Customization

svgblock was made to be simple, so it has **a few things you can choose** and a clear place to change everything else.

### What you can change

| What | How | Where |
| --- | --- | --- |
| **Colors and visual style** | Pick a ready-made theme | `theme=` in `Block(...)` → see [Themes](#themes) |
| **Entrance animation** | Pick one of the six options | `animation=` in `Block(...)` → see [Animations](#animations) |
| **Width of the block** | Set a number of pixels | `width=` in `Block(...)` |
| **Size of the text** | Set a number of pixels | `font_size=` in `.title()`, `.subsection()` and `.text()` |
| **A new theme** | Add an entry to `THEMES` | `svgblock/theme.py` → see [Creating your own theme](#creating-your-own-theme) |
| **Anything else** (spacing, border, glow, animation time...) | Edit the constants | See [Constants reference](#constants-reference) |

> [!NOTE]
> The font family is not customizable on purpose: the library measures text using the widths of the Arial font to break lines correctly, so it always asks for Arial first (then Helvetica, then the default sans-serif font).

### Creating your own theme

A theme is an entry in the `THEMES` dictionary, in the file `svgblock/theme.py`. The name must be in lowercase and it is exactly what you will pass to `Block(theme=...)`. Every entry needs these ten colors, all written as hexadecimal values (`#RRGGBB`):

| Color | What it paints |
| --- | --- |
| `background_center` | The center of the radial glow in the background. |
| `background_edge` | The outer color of the background, at the edges of the block. |
| `border_start` | The start of the border gradient (top left). |
| `border_end` | The end of the border gradient (bottom right). |
| `title_text` | The text of titles. |
| `title_bar` | The bar on the left of titles. |
| `subsection_text` | The text of subsections. |
| `subsection_marker` | The dot on the left of subsections. |
| `text` | Regular paragraphs. |
| `highlight` | Highlighted words. |

```python
"mytheme": {
    "background_center": "#1B2B34", "background_edge": "#0B1014",
    "border_start": "#6699CC", "border_end": "#223344",
    "title_text": "#99C794", "title_bar": "#99C794",
    "subsection_text": "#FAC863", "subsection_marker": "#FAC863",
    "text": "#D8DEE9", "highlight": "#FFFFFF",
},
```

> [!TIP]
> The background is always a radial glow, so the two background colors need some difference between them. If you use the same color in both, the glow becomes invisible.

### Constants reference

Everything else is controlled by constants at the top of each file of the `svgblock/` folder. To edit them, install the library from a clone of the repository in editable mode, so your changes take effect right away:

```bash
git clone https://github.com/JonatasCortes/svgblock.git
cd svgblock
pip install -e .
```

Here is what each group of constants is for:

| File | Constants | What it controls |
| --- | --- | --- |
| **`block.py`** (defaults) | `DEFAULT_THEME_NAME`, `DEFAULT_WIDTH`, `DEFAULT_ANIMATION`, `TITLE_FONT_SIZE`, `SUBSECTION_FONT_SIZE`, `TEXT_FONT_SIZE` | The values used when you do not pass a parameter |
| **`block.py`** (layout) | `BLOCK_PADDING`, `COMPONENT_GAP` | The space between the border and the content, and between one component and the next |
| **`block.py`** (font) | `FONT_FAMILY` | The font stack written in the SVG |
| **`components.py`** (text) | `LINE_HEIGHT_RATIO`, `BASELINE_RATIO`, `BOLD_WEIGHT` | The height of each line and the weight of bold text |
| **`components.py`** (title) | `TITLE_BAR_WIDTH`, `TITLE_BAR_HEIGHT_RATIO`, `TITLE_BAR_GAP` | The size of the title bar and its distance to the text |
| **`components.py`** (subsection) | `SUBSECTION_MARKER_RADIUS_RATIO`, `SUBSECTION_MARKER_GAP` | The size of the subsection dot and its distance to the text |
| **`frame.py`** | `BORDER_WIDTH`, `CORNER_RADIUS`, `BACKGROUND_GLOW_RADIUS` | The border thickness, the rounded corners and how far the background glow spreads |
| **`animation.py`** | `ANIMATION_DURATION_SECONDS`, `SLIDE_DISTANCE_PX`, `POP_START_SCALE` | How long the entrance takes, how far the slides travel and how small the pop starts |

> [!TIP]
> The easiest and most noticeable changes are `ANIMATION_DURATION_SECONDS` (a slower or faster entrance) and `BACKGROUND_GLOW_RADIUS` (a more concentrated or more spread glow).

> [!CAUTION]
> Be careful with `FONT_FAMILY`. The line breaks are calculated with the widths of the Arial font, so a very different font can make lines look too short or too long. If something looks wrong, restore the original values.

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>

---

## Themes

A theme defines **only colors**: the border gradient, the glowing background, the title, the subsection, the text and the highlighted words. The layout, the font and the animation are the same in every theme, so you can switch themes without anything else moving.

To use a theme, pass its name to the block:

```python
Block(theme="japan_dark")
```

> [!NOTE]
> Theme names are written in lowercase, exactly as listed below. Names with two words use an underscore (`japan_dark`, `solarized_light`) or are written together (`chocomint`, `berrymatcha`).

Jump straight to a category:

<table align="center">
  <thead>
    <tr>
      <th align="center">🎨 Dark Colors</th>
      <th align="center">💡 Light Colors</th>
      <th align="center">🍂 Seasons</th>
      <th align="center">🍷 Drinks</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><a href="#1-dark-colors"><b>Explore ↗</b></a></td>
      <td align="center"><a href="#2-light-colors-pastels"><b>Explore ↗</b></a></td>
      <td align="center"><a href="#3-seasons"><b>Explore ↗</b></a></td>
      <td align="center"><a href="#4-drinks"><b>Explore ↗</b></a></td>
    </tr>
  </tbody>
  <thead>
    <tr>
      <th align="center">🌍 Countries & Geo</th>
      <th align="center">🌸 Aesthetics & Culture</th>
      <th align="center">💻 Classical UI (Dev)</th>
      <th align="center">✨ Mythology</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><a href="#5-countries--geography"><b>Explore ↗</b></a></td>
      <td align="center"><a href="#6-aesthetics--culture"><b>Explore ↗</b></a></td>
      <td align="center"><a href="#7-classical-ui-dev-themes"><b>Explore ↗</b></a></td>
      <td align="center"><a href="#8-mythology--concepts"><b>Explore ↗</b></a></td>
    </tr>
  </tbody>
</table>

### 1. Dark Colors

Simple, bold, and deep classic colors.
Available themes: [`red`](#red) · [`orange`](#orange) · [`yellow`](#yellow) · [`green`](#green) · [`blue`](#blue) · [`purple`](#purple) · [`pink`](#pink) · [`obsidian`](#obsidian)

#### Red
`theme="red"`
<p align="center"><img src="assets/block_red.svg" alt="svgblock example, red theme" width="800"></p>

#### Orange
`theme="orange"`
<p align="center"><img src="assets/block_orange.svg" alt="svgblock example, orange theme" width="800"></p>

#### Yellow
`theme="yellow"`
<p align="center"><img src="assets/block_yellow.svg" alt="svgblock example, yellow theme" width="800"></p>

#### Green
`theme="green"`
<p align="center"><img src="assets/block_green.svg" alt="svgblock example, green theme" width="800"></p>

#### Blue
`theme="blue"`
<p align="center"><img src="assets/block_blue.svg" alt="svgblock example, blue theme" width="800"></p>

#### Purple
`theme="purple"`
<p align="center"><img src="assets/block_purple.svg" alt="svgblock example, purple theme" width="800"></p>

#### Pink
`theme="pink"`
<p align="center"><img src="assets/block_pink.svg" alt="svgblock example, pink theme" width="800"></p>

#### Obsidian
`theme="obsidian"`
<p align="center"><img src="assets/block_obsidian.svg" alt="svgblock example, obsidian theme" width="800"></p>

<p align="right"><a href="#themes">⬆ back to themes</a></p>

---

### 2. Light Colors (Pastels)

Beautifully tinted light backgrounds for a clean and fresh look.
Available themes: [`mint`](#mint) · [`chocomint`](#choco-mint) · [`lavender`](#lavender) · [`peach`](#peach) · [`sky`](#sky)

#### Mint
`theme="mint"`
<p align="center"><img src="assets/block_mint.svg" alt="svgblock example, mint theme" width="800"></p>

#### Choco Mint
`theme="chocomint"`
<p align="center"><img src="assets/block_chocomint.svg" alt="svgblock example, chocomint theme" width="800"></p>

#### Lavender
`theme="lavender"`
<p align="center"><img src="assets/block_lavender.svg" alt="svgblock example, lavender theme" width="800"></p>

#### Peach
`theme="peach"`
<p align="center"><img src="assets/block_peach.svg" alt="svgblock example, peach theme" width="800"></p>

#### Sky
`theme="sky"`
<p align="center"><img src="assets/block_sky.svg" alt="svgblock example, sky theme" width="800"></p>

<p align="right"><a href="#themes">⬆ back to themes</a></p>

---

### 3. Seasons

Earthy and atmospheric palettes inspired by the natural world.
Available themes: [`spring`](#spring) · [`summer`](#summer) · [`autumn`](#autumn) · [`winter`](#winter)

#### Spring
`theme="spring"`
<p align="center"><img src="assets/block_spring.svg" alt="svgblock example, spring theme" width="800"></p>

#### Summer
`theme="summer"`
<p align="center"><img src="assets/block_summer.svg" alt="svgblock example, summer theme" width="800"></p>

#### Autumn
`theme="autumn"`
<p align="center"><img src="assets/block_autumn.svg" alt="svgblock example, autumn theme" width="800"></p>

#### Winter
`theme="winter"`
<p align="center"><img src="assets/block_winter.svg" alt="svgblock example, winter theme" width="800"></p>

<p align="right"><a href="#themes">⬆ back to themes</a></p>

---

### 4. Drinks

Warm tones and aesthetics inspired by classic beverages.
Available themes: [`wine`](#wine) · [`beer`](#beer) · [`coffee`](#coffee) · [`matcha`](#matcha) · [`berrymatcha`](#berry-matcha) · [`latte`](#latte)

#### Wine
`theme="wine"`
<p align="center"><img src="assets/block_wine.svg" alt="svgblock example, wine theme" width="800"></p>

#### Beer
`theme="beer"`
<p align="center"><img src="assets/block_beer.svg" alt="svgblock example, beer theme" width="800"></p>

#### Coffee
`theme="coffee"`
<p align="center"><img src="assets/block_coffee.svg" alt="svgblock example, coffee theme" width="800"></p>

#### Matcha
`theme="matcha"`
<p align="center"><img src="assets/block_matcha.svg" alt="svgblock example, matcha theme" width="800"></p>

#### Berry Matcha
`theme="berrymatcha"`
<p align="center"><img src="assets/block_berrymatcha.svg" alt="svgblock example, berrymatcha theme" width="800"></p>

#### Latte
`theme="latte"`
<p align="center"><img src="assets/block_latte.svg" alt="svgblock example, latte theme" width="800"></p>

<p align="right"><a href="#themes">⬆ back to themes</a></p>

---

### 5. Countries & Geography

Colors inspired by flags and cultural landmarks.
Available themes: [`brazil`](#brazil) · [`usa`](#usa) · [`miami`](#miami) · [`france`](#france) · [`japan_dark`](#japan-dark) · [`japan_light`](#japan-light) · [`sakura`](#sakura) · [`india`](#india) · [`china`](#china) · [`mexico`](#mexico) · [`fiesta`](#fiesta) · [`greece`](#greece) · [`egypt`](#egypt)

#### Brazil
`theme="brazil"`
<p align="center"><img src="assets/block_brazil.svg" alt="svgblock example, brazil theme" width="800"></p>

#### USA
`theme="usa"`
<p align="center"><img src="assets/block_usa.svg" alt="svgblock example, usa theme" width="800"></p>

#### Miami
`theme="miami"`
<p align="center"><img src="assets/block_miami.svg" alt="svgblock example, miami theme" width="800"></p>

#### France
`theme="france"`
<p align="center"><img src="assets/block_france.svg" alt="svgblock example, france theme" width="800"></p>

#### Japan Dark
`theme="japan_dark"`
<p align="center"><img src="assets/block_japandark.svg" alt="svgblock example, japan_dark theme" width="800"></p>

#### Japan Light
`theme="japan_light"`
<p align="center"><img src="assets/block_japanlight.svg" alt="svgblock example, japan_light theme" width="800"></p>

#### Sakura
`theme="sakura"`
<p align="center"><img src="assets/block_sakura.svg" alt="svgblock example, sakura theme" width="800"></p>

#### India
`theme="india"`
<p align="center"><img src="assets/block_india.svg" alt="svgblock example, india theme" width="800"></p>

#### China
`theme="china"`
<p align="center"><img src="assets/block_china.svg" alt="svgblock example, china theme" width="800"></p>

#### Mexico
`theme="mexico"`
<p align="center"><img src="assets/block_mexico.svg" alt="svgblock example, mexico theme" width="800"></p>

#### Fiesta
`theme="fiesta"`
<p align="center"><img src="assets/block_fiesta.svg" alt="svgblock example, fiesta theme" width="800"></p>

#### Greece
`theme="greece"`
<p align="center"><img src="assets/block_greece.svg" alt="svgblock example, greece theme" width="800"></p>

#### Egypt
`theme="egypt"`
<p align="center"><img src="assets/block_egypt.svg" alt="svgblock example, egypt theme" width="800"></p>

<p align="right"><a href="#themes">⬆ back to themes</a></p>

---

### 6. Aesthetics & Culture

Highly stylized themes based on internet cultures and artistic movements.
Available themes: [`neon`](#neon) · [`cyberpunk`](#cyberpunk) · [`steampunk`](#steampunk) · [`synthwave`](#synthwave) · [`lofi`](#lofi)

#### Neon
`theme="neon"`
<p align="center"><img src="assets/block_neon.svg" alt="svgblock example, neon theme" width="800"></p>

#### Cyberpunk
`theme="cyberpunk"`
<p align="center"><img src="assets/block_cyberpunk.svg" alt="svgblock example, cyberpunk theme" width="800"></p>

#### Steampunk
`theme="steampunk"`
<p align="center"><img src="assets/block_steampunk.svg" alt="svgblock example, steampunk theme" width="800"></p>

#### Synthwave
`theme="synthwave"`
<p align="center"><img src="assets/block_synthwave.svg" alt="svgblock example, synthwave theme" width="800"></p>

#### Lofi
`theme="lofi"`
<p align="center"><img src="assets/block_lofi.svg" alt="svgblock example, lofi theme" width="800"></p>

<p align="right"><a href="#themes">⬆ back to themes</a></p>

---

### 7. Classical UI (Dev Themes)

Beloved themes from your favorite code editors and IDEs.
Available themes: [`dracula`](#dracula) · [`mocha`](#mocha) · [`nord`](#nord) · [`solarized_dark`](#solarized-dark) · [`solarized_light`](#solarized-light) · [`atlas`](#atlas)

#### Dracula
`theme="dracula"`
<p align="center"><img src="assets/block_dracula.svg" alt="svgblock example, dracula theme" width="800"></p>

#### Mocha
`theme="mocha"`
<p align="center"><img src="assets/block_mocha.svg" alt="svgblock example, mocha theme" width="800"></p>

#### Nord
`theme="nord"`
<p align="center"><img src="assets/block_nord.svg" alt="svgblock example, nord theme" width="800"></p>

#### Solarized Dark
`theme="solarized_dark"`
<p align="center"><img src="assets/block_solarizeddark.svg" alt="svgblock example, solarized_dark theme" width="800"></p>

#### Solarized Light
`theme="solarized_light"`
<p align="center"><img src="assets/block_solarizedlight.svg" alt="svgblock example, solarized_light theme" width="800"></p>

#### Atlas
`theme="atlas"`
<p align="center"><img src="assets/block_atlas.svg" alt="svgblock example, atlas theme" width="800"></p>

<p align="right"><a href="#themes">⬆ back to themes</a></p>

---

### 8. Mythology & Concepts

Epic, concept-driven abstract aesthetics.
Available themes: [`heaven`](#heaven) · [`hell`](#hell) · [`abyss`](#abyss)

#### Heaven
`theme="heaven"`
<p align="center"><img src="assets/block_heaven.svg" alt="svgblock example, heaven theme" width="800"></p>

#### Hell
`theme="hell"`
<p align="center"><img src="assets/block_hell.svg" alt="svgblock example, hell theme" width="800"></p>

#### Abyss
`theme="abyss"`
<p align="center"><img src="assets/block_abyss.svg" alt="svgblock example, abyss theme" width="800"></p>

<p align="right"><a href="#themes">⬆ back to themes</a> · <a href="#table-of-contents">⬆ back to top</a></p>

---

## Troubleshooting

| Problem | What to check |
| --- | --- |
| **`ValueError: Unknown theme '...'`** | The theme name does not exist. The error message lists every available theme. Names are lowercase, exactly as shown in the [Themes](#themes) section. |
| **`ValueError: Unknown animation '...'`** | The animation name is wrong. The six valid names are `fade`, `slide-up`, `slide-down`, `slide-left`, `slide-right` and `pop`. |
| **`ValueError: Unclosed highlight marker '**'`** | A `**` in the text was never closed. Every highlight needs an opening and a closing `**`. To write a literal `**`, use `\*\*` (see [Highlighting words](#highlighting-words)). |
| **`SyntaxWarning: invalid escape sequence '\*'`** | Python is warning about the backslash. Write it twice (`"\\*"`) or use a raw string (`r"\*"`). |
| **The code fails with errors about the `\|` symbol in type hints** | You are using a Python older than 3.10. Update Python and install again. |
| **A title, a subsection or a very long word goes past the border** | Titles and subsections stay on a single line, and a word bigger than the block cannot be broken. Shorten the text, reduce the `font_size` or increase the `width` of the block. |
| **A highlighted word is not highlighted** | The `highlight` list respects upper and lower case, so the text must match exactly. |
| **Lines break earlier or later than expected** | The width of the text is estimated with the Arial font. On a system without Arial the browser uses another font, so lines can look slightly different. Emojis and curly quotes are measured as a full letter wide, so a line can break a little early. |
| **The block does not appear in my profile** | Check that the `.svg` file was committed and pushed, and that the path in the `<img src="...">` matches the file name exactly (GitHub paths are case sensitive). |
| **The animation does not play** | The animation plays once, when the image loads, so reload the page to see it again. It is also disabled for people who turned on "reduce motion" in the system, and some image viewers and editors do not run animations. Open the file in a browser to check. |

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>

---

<p align="center">
  Made with 💜 for GitHub profiles. If you liked it, leave a ⭐ on the repository!
</p>