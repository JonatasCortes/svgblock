<p align="center">
  <img src="assets/hero.svg" alt="Welcome to svgblock" width="900">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-none-2ea44f" alt="No dependencies">
  <img src="https://img.shields.io/badge/themes-50-ff0055" alt="50 themes">
  <img src="https://img.shields.io/badge/entry_animations-6-8A2BE2" alt="6 entry animations">
  <img src="https://img.shields.io/badge/output-SVG-FFB13B?logo=svg&logoColor=white" alt="SVG output">
</p>

<p align="center">
  <img src="assets/intro.svg" alt="What svgblock does" width="900">
</p>


<a id="table-of-contents"></a>
<p align="center">
  <img src="assets/toc.svg" alt="Table of Contents" width="900">
</p>

<ul>
  <li><a href="#how-a-block-is-built">🧭 How a Block Is Built</a></li>
  <li><a href="#how-to-use">🚀 How to Use</a></li>
  <li><a href="#building-a-block">🧱 Building a Block</a>
    <ul>
      <li><a href="#creating-a-block">Creating a block</a></li>
      <li><a href="#adding-content">Adding content</a></li>
      <li><a href="#text-markers">Text markers</a></li>
      <li><a href="#columns">Columns</a></li>
      <li><a href="#tables">Tables</a></li>
      <li><a href="#images">Images</a></li>
      <li><a href="#saving-the-result">Saving the result</a></li>
      <li><a href="#animations">Animations</a></li>
    </ul>
  </li>
  <li><a href="#customization">🛠️ Customization</a>
    <ul>
      <li><a href="#creating-your-own-theme">Creating your own theme</a></li>
      <li><a href="#constants-reference">Constants reference</a></li>
    </ul>
  </li>
  <li><a href="#themes">🎨 Themes</a>
    <ul>
      <li><a href="#1-dark-colors">1. Dark Colors</a></li>
      <li><a href="#2-light-colors-pastels">2. Light Colors (Pastels)</a></li>
      <li><a href="#3-seasons">3. Seasons</a></li>
      <li><a href="#4-drinks">4. Drinks</a></li>
      <li><a href="#5-countries--geography">5. Countries &amp; Geography</a></li>
      <li><a href="#6-aesthetics--culture">6. Aesthetics &amp; Culture</a></li>
      <li><a href="#7-classical-ui-dev-themes">7. Classical UI (Dev Themes)</a></li>
      <li><a href="#8-mythology--concepts">8. Mythology &amp; Concepts</a></li>
    </ul>
  </li>
  <li><a href="#troubleshooting">🩺 Troubleshooting</a></li>
</ul>


<a id="how-a-block-is-built"></a>
<p align="center">
  <img src="assets/how_it_is_built.svg" alt="How a block is built" width="900">
</p>

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>



<a id="how-to-use"></a>
<p align="center">
  <img src="assets/use_overview.svg" alt="How to use" width="900">
</p>

<p align="center">
  <img src="assets/use_step_1.svg" alt="Step 1: install svgblock" width="900">
</p>

```bash
python --version
pip install git+https://github.com/JonatasCortes/svgblock.git

# or clone the repository and install it from the folder
git clone https://github.com/JonatasCortes/svgblock.git
cd svgblock
pip install .
```

<p align="center">
  <img src="assets/use_step_2.svg" alt="Step 2: write your first block" width="900">
</p>

```python
from svgblock import Block

(
    Block(theme="neon", width=900, animation="slide-up")
    .title("Hello, I'm Bob")
    .text("I build **small tools** in **pure Python** and I love open source.")
    .subsection("What I am learning")
    .text("Right now I am studying **graph algorithms** and **computer vision**.")
    .save("assets/block.svg")
)
```

<p align="center">
  <img src="assets/use_step_3.svg" alt="Step 3: run the script" width="900">
</p>

```bash
python generate_blocks.py
```

<p align="center">
  <img src="assets/use_step_4.svg" alt="Step 4: show the block in your profile" width="900">
</p>

```html
<p align="center">
  <img src="assets/block.svg" alt="About me" width="900">
</p>
```

<p align="center">
  <img src="assets/use_more.svg" alt="Optional: add more blocks" width="900">
</p>

```python
from svgblock import Block

Block(theme="dracula", animation="fade").title("About me").text("...").save("assets/about.svg")
Block(theme="nord", animation="pop").title("Projects").text("...").save("assets/projects.svg")
```

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>



<a id="building-a-block"></a>
<a id="creating-a-block"></a>
<p align="center">
  <img src="assets/building_create.svg" alt="Creating a block" width="900">
</p>

```python
Block(theme="red", width=900, animation="fade")
```

<a id="adding-content"></a>
<p align="center">
  <img src="assets/building_content.svg" alt="Adding content" width="900">
</p>

```python
(
    Block(theme="coffee")
    .title("Projects")
    .text("A few things I built.", font_size=18)
    .subsection("HNSW Character Recognition")
    .text("Train and test your own model.")
    .divider()
    .table(["Project", "Stars"], [["HNSW", 120], ["Voronoi Stats", 85]])
    .image("assets/preview.png", width=300)
    .divider(0.5)
    .title("Contact")
    .text("Find me on GitHub.")
)
```

<a id="text-markers"></a>
<p align="center">
  <img src="assets/markers.svg" alt="Text markers" width="900">
</p>

```python
.text("**ola __mundo__** ola, --errado-- e ##inclinado##")
.text(r"A literal \*\* needs a backslash before each asterisk.")
```

<a id="columns"></a>
<p align="center">
  <img src="assets/columns.svg" alt="Columns" width="900">
</p>

```python
from svgblock import Block, Column

(
    Block(theme="nord")
    .columns(
        Column(1).subsection("Weight 1").text("A narrow column, good for short notes."),
        Column(2).subsection("Weight 2").text("A column twice as wide, ideal for the main text."),
    )
)
```

<a id="tables"></a>
<p align="center">
  <img src="assets/tables.svg" alt="Tables" width="900">
</p>

```python
.table(
    ["Language", "Level", "Typed"],
    [
        ["Python", "**Advanced**", True],
        ["Rust", "##Learning##", True],
        ["COBOL", "--Retired--", None],
    ],
    align=("left", "center", "center"),
    weights=(2, 2, 1),
    striped=True,
    row_dividers=True,
    column_dividers=False,
)
```

<a id="images"></a>
<p align="center">
  <img src="assets/images.svg" alt="Images" width="900">
</p>

```python
(
    Block(theme="mocha")
    .columns(
        Column(1).image("assets/logo.png", width=110),
        Column(4).subsection("A logo beside the text").text("The text takes the rest of the width."),
    )
)
```

<a id="saving-the-result"></a>
<p align="center">
  <img src="assets/saving.svg" alt="Saving the result" width="900">
</p>

<a id="animations"></a>
<p align="center">
  <img src="assets/animations.svg" alt="Animations" width="900">
</p>

<p align="center">
  <img src="assets/animation_fade.svg" alt="fade animation" width="49%">
  <img src="assets/animation_pop.svg" alt="pop animation" width="49%">
  <img src="assets/animation_slide-up.svg" alt="slide-up animation" width="49%">
  <img src="assets/animation_slide-down.svg" alt="slide-down animation" width="49%">
  <img src="assets/animation_slide-left.svg" alt="slide-left animation" width="49%">
  <img src="assets/animation_slide-right.svg" alt="slide-right animation" width="49%">
</p>

```python
from svgblock import Animation, Block

# No animation (the default)
Block()

# Plays once
Block(animation="pop")
Block(animation=Animation.SLIDE_UP)

# Replays every 5 seconds
Block(animation="slide-up", animation_loop=5)
```

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>



<a id="customization"></a>
<p align="center">
  <img src="assets/customization.svg" alt="Customization" width="900">
</p>

<a id="creating-your-own-theme"></a>
<p align="center">
  <img src="assets/custom_theme.svg" alt="Creating your own theme" width="900">
</p>

```python
"mytheme": {
    "background_center": "#1B2B34", "background_edge": "#0B1014",
    "border_start": "#6699CC", "border_end": "#223344",
    "title_text": "#99C794", "title_bar": "#99C794",
    "subsection_text": "#FAC863", "subsection_marker": "#FAC863",
    "text": "#D8DEE9", "highlight": "#FFFFFF",
    "underline": "#6699CC", "strikethrough": "#65737E", "italic": "#C0C5CE",
    "table_background": "#10181D", "table_header_background": "#223540",
    "table_header_text": "#99C794", "table_text": "#D8DEE9",
    "table_divider": "#33505F", "table_stripe_background": "#15222A",
    "table_border": "#33505F", "divider": "#6699CC",
},
```

<a id="constants-reference"></a>
<p align="center">
  <img src="assets/constants.svg" alt="Constants reference" width="900">
</p>

```bash
git clone https://github.com/JonatasCortes/svgblock.git
cd svgblock
pip install -e .
```

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>



<a id="themes"></a>
<p align="center">
  <img src="assets/themes_overview.svg" alt="Themes" width="900">
</p>

<a id="1-dark-colors"></a>
<p align="center">
  <img src="assets/category_dark.svg" alt="Dark colors" width="900">
</p>
<p align="center">
  <img src="assets/block_red.svg" alt="red theme" width="49%">
  <img src="assets/block_orange.svg" alt="orange theme" width="49%">
  <img src="assets/block_yellow.svg" alt="yellow theme" width="49%">
  <img src="assets/block_green.svg" alt="green theme" width="49%">
  <img src="assets/block_blue.svg" alt="blue theme" width="49%">
  <img src="assets/block_purple.svg" alt="purple theme" width="49%">
  <img src="assets/block_pink.svg" alt="pink theme" width="49%">
  <img src="assets/block_obsidian.svg" alt="obsidian theme" width="49%">
</p>

<a id="2-light-colors-pastels"></a>
<p align="center">
  <img src="assets/category_light.svg" alt="Light colors" width="900">
</p>
<p align="center">
  <img src="assets/block_mint.svg" alt="mint theme" width="49%">
  <img src="assets/block_chocomint.svg" alt="chocomint theme" width="49%">
  <img src="assets/block_lavender.svg" alt="lavender theme" width="49%">
  <img src="assets/block_peach.svg" alt="peach theme" width="49%">
  <img src="assets/block_sky.svg" alt="sky theme" width="49%">
</p>

<a id="3-seasons"></a>
<p align="center">
  <img src="assets/category_seasons.svg" alt="Seasons" width="900">
</p>
<p align="center">
  <img src="assets/block_spring.svg" alt="spring theme" width="49%">
  <img src="assets/block_summer.svg" alt="summer theme" width="49%">
  <img src="assets/block_autumn.svg" alt="autumn theme" width="49%">
  <img src="assets/block_winter.svg" alt="winter theme" width="49%">
</p>

<a id="4-drinks"></a>
<p align="center">
  <img src="assets/category_drinks.svg" alt="Drinks" width="900">
</p>
<p align="center">
  <img src="assets/block_wine.svg" alt="wine theme" width="49%">
  <img src="assets/block_beer.svg" alt="beer theme" width="49%">
  <img src="assets/block_coffee.svg" alt="coffee theme" width="49%">
  <img src="assets/block_matcha.svg" alt="matcha theme" width="49%">
  <img src="assets/block_berrymatcha.svg" alt="berrymatcha theme" width="49%">
  <img src="assets/block_latte.svg" alt="latte theme" width="49%">
</p>

<a id="5-countries--geography"></a>
<p align="center">
  <img src="assets/category_countries.svg" alt="Countries and geography" width="900">
</p>
<p align="center">
  <img src="assets/block_brazil.svg" alt="brazil theme" width="49%">
  <img src="assets/block_usa.svg" alt="usa theme" width="49%">
  <img src="assets/block_miami.svg" alt="miami theme" width="49%">
  <img src="assets/block_france.svg" alt="france theme" width="49%">
  <img src="assets/block_japandark.svg" alt="japandark theme" width="49%">
  <img src="assets/block_japanlight.svg" alt="japanlight theme" width="49%">
  <img src="assets/block_sakura.svg" alt="sakura theme" width="49%">
  <img src="assets/block_india.svg" alt="india theme" width="49%">
  <img src="assets/block_china.svg" alt="china theme" width="49%">
  <img src="assets/block_mexico.svg" alt="mexico theme" width="49%">
  <img src="assets/block_fiesta.svg" alt="fiesta theme" width="49%">
  <img src="assets/block_greece.svg" alt="greece theme" width="49%">
  <img src="assets/block_egypt.svg" alt="egypt theme" width="49%">
</p>

<a id="6-aesthetics--culture"></a>
<p align="center">
  <img src="assets/category_aesthetics.svg" alt="Aesthetics and culture" width="900">
</p>
<p align="center">
  <img src="assets/block_neon.svg" alt="neon theme" width="49%">
  <img src="assets/block_cyberpunk.svg" alt="cyberpunk theme" width="49%">
  <img src="assets/block_steampunk.svg" alt="steampunk theme" width="49%">
  <img src="assets/block_synthwave.svg" alt="synthwave theme" width="49%">
  <img src="assets/block_lofi.svg" alt="lofi theme" width="49%">
</p>

<a id="7-classical-ui-dev-themes"></a>
<p align="center">
  <img src="assets/category_dev.svg" alt="Classical UI dev themes" width="900">
</p>
<p align="center">
  <img src="assets/block_dracula.svg" alt="dracula theme" width="49%">
  <img src="assets/block_mocha.svg" alt="mocha theme" width="49%">
  <img src="assets/block_nord.svg" alt="nord theme" width="49%">
  <img src="assets/block_solarizeddark.svg" alt="solarizeddark theme" width="49%">
  <img src="assets/block_solarizedlight.svg" alt="solarizedlight theme" width="49%">
  <img src="assets/block_atlas.svg" alt="atlas theme" width="49%">
</p>

<a id="8-mythology--concepts"></a>
<p align="center">
  <img src="assets/category_mythology.svg" alt="Mythology and concepts" width="900">
</p>
<p align="center">
  <img src="assets/block_heaven.svg" alt="heaven theme" width="49%">
  <img src="assets/block_hell.svg" alt="hell theme" width="49%">
  <img src="assets/block_abyss.svg" alt="abyss theme" width="49%">
</p>

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>



<a id="troubleshooting"></a>
<p align="center">
  <img src="assets/troubleshooting.svg" alt="Troubleshooting" width="900">
</p>

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>



<p align="center">
  <img src="assets/footer.svg" alt="Made with love for GitHub profiles" width="900">
</p>