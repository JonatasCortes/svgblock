<p align="center">
  <img src="assets/hero.svg" alt="Welcome to svgblock" width="900">
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/svgblock?color=3776AB&logo=pypi&logoColor=white" alt="PyPI version">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-none-2ea44f" alt="No dependencies">
  <img src="https://img.shields.io/badge/themes-50-ff0055" alt="50 themes">
  <img src="https://img.shields.io/badge/animations-5-8A2BE2" alt="5 animations">
  <img src="https://img.shields.io/badge/easings-8-00B8D9" alt="8 easings">
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
    </ul>
  </li>
  <li><a href="#animations">🎞️ Animations</a>
    <ul>
      <li><a href="#base-animations">Base animations</a></li>
      <li><a href="#animation-parameters">Parameters</a></li>
      <li><a href="#easings">Easings</a></li>
      <li><a href="#repeating">Repeating</a></li>
      <li><a href="#sequences">Sequences</a></li>
      <li><a href="#animation-errors">Errors</a></li>
    </ul>
  </li>
  <li><a href="#customization">🛠️ Customization</a>
    <ul>
      <li><a href="#creating-your-own-theme">Creating your own theme</a></li>
      <li><a href="#editing-a-theme">Editing a theme</a></li>
      <li><a href="#constants-reference">Constants reference</a></li>
    </ul>
  </li>
  <li><a href="#themes">🎨 Themes</a>
    <ul>
      <li><a href="#1-dark-colors">1. Dark Colors</a></li>
      <li><a href="#2-light-colors-pastels">2. Light Colors (Pastels)</a></li>
      <li><a href="#3-seasons">3. Seasons</a></li>
      <li><a href="#4-drinks">4. Drinks</a></li>
      <li><a href="#5-countries--geography">5. Countries & Geography</a></li>
      <li><a href="#6-aesthetics--culture">6. Aesthetics & Culture</a></li>
      <li><a href="#7-classical-ui-dev-themes">7. Classical UI (Dev Themes)</a></li>
      <li><a href="#8-mythology--concepts">8. Mythology & Concepts</a></li>
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
pip install svgblock
```

<p align="center">
  <img src="assets/use_step_2.svg" alt="Step 2: write your first block" width="900">
</p>

```python
rom svgblock import Block, Rise, Theme

(
    Block(theme=Theme.NEON, width=900, animation=Rise())
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
  <img src="assets/use_step_4.svg" alt="Step 4: use the SVG" width="900">
</p>

```html
<img src="assets/block.svg" alt="About me" width="900">
```

```markdown
![About me](assets/block.svg)
```

<p align="center">
  <img src="assets/use_more.svg" alt="Optional: add more blocks" width="900">
</p>

```python
from svgblock import Block, Fade, Pop, Theme

Block(theme=Theme.DRACULA, animation=Fade()).title("About me").text("...").save("assets/about.svg")
Block(theme=Theme.NORD, animation=Pop()).title("Projects").text("...").save("assets/projects.svg")
```

<p align="center">
  <img src="assets/use_local.svg" alt="Optional: use the repository locally" width="900">
</p>

```bash
git clone https://github.com/JonatasCortes/svgblock.git
cd svgblock
pip install -e .
```

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>

<a id="building-a-block"></a>
<a id="creating-a-block"></a>

<p align="center">
  <img src="assets/building_create.svg" alt="Creating a block" width="900">
</p>

```python
from svgblock import Block, Fade, Theme

Block(theme=Theme.RED, width=900, padding=32, animation=Fade())
```

<a id="adding-content"></a>

<p align="center">
  <img src="assets/building_content.svg" alt="Adding content" width="900">
</p>

```python
(
    Block(theme=Theme.COFFEE)
    .title("Projects")
    .text("A few things I built.", font_size=18)
    .subsection("Log parser")
    .text("Reads log files and prints a short summary.")
    .divider()
    .table(["Project", "Stars"], [["logparse", 120], ["tinyserver", 85]])
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
.text("**bold**, __underlined__, --struck-- and ##italic##")
.text(r"A literal \*\* needs a backslash before each asterisk.")
```

<a id="columns"></a>

<p align="center">
  <img src="assets/columns.svg" alt="Columns" width="900">
</p>

```python
from svgblock import Block, Column, Theme

(
    Block(theme=Theme.NORD)
    .columns(
        Column(1).subsection("Weight 1").text("A narrow column."),
        Column(2).subsection("Weight 2").text("A column twice as wide."),
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
    column_dividers=True,
)
```

<a id="images"></a>

<p align="center">
  <img src="assets/images.svg" alt="Images" width="900">
</p>

```python
(
    Block(theme=Theme.NEON)
    .columns(
        Column().image("assets/logo.png", width=350),
        Column().subsection("A logo beside the text").text("The image sits in a column and the text takes the rest of the width"),
    )
)
```

<a id="saving-the-result"></a>

<p align="center">
  <img src="assets/saving.svg" alt="Saving the result" width="900">
</p>

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>

<a id="animations"></a>

<p align="center">
  <img src="assets/animations.svg" alt="Animations" width="900">
</p>

```python
from svgblock import Block, Pop, Rise, Sequence, Show

# Default values
Block(animation=Rise())

# A configured animation
Block(animation=Rise(distance=80, duration=1.2))

# A sequence: enter, rest for 3 seconds and enter again, forever
Block(animation=Sequence(Pop(), Show(3), loop_limit=None))
```

<a id="base-animations"></a>

<p align="center">
  <img src="assets/animations_base.svg" alt="Base animations" width="900">
</p>

<p align="center">
  <img src="assets/animation_fade.svg" alt="fade animation" width="49%">
  <img src="assets/animation_rise.svg" alt="rise animation" width="49%">
  <img src="assets/animation_drop.svg" alt="drop animation" width="49%">
  <img src="assets/animation_pop.svg" alt="pop animation" width="49%">
  <img src="assets/animation_pulse.svg" alt="pulse animation" width="49%">
</p>

<a id="animation-parameters"></a>

<p align="center">
  <img src="assets/animations_parameters.svg" alt="Animation parameters" width="900">
</p>

```python
from svgblock import Drop, Fade, Linear, Pop, Pulse, Rise

Rise(distance=80, duration=1.6, fade=False)
Drop(distance=20, duration=0.4)
Pop(start_scale=0.3, duration=1.2)
Pulse(amount=0.1, duration=1, loop_limit=4)
Fade(duration=2, easing=Linear())
```

<p align="center">
  <img src="assets/animation_rise_custom.svg" alt="customized rise animation" width="49%">
  <img src="assets/animation_drop_custom.svg" alt="customized drop animation" width="49%">
  <img src="assets/animation_pop_custom.svg" alt="customized pop animation" width="49%">
  <img src="assets/animation_pulse_custom.svg" alt="customized pulse animation" width="49%">
</p>

<a id="easings"></a>

<p align="center">
  <img src="assets/animations_easings.svg" alt="Easings" width="900">
</p>

```python
from svgblock import CubicBezier, EaseInOut, Rise, Steps

Rise(easing=EaseInOut())
Rise(easing=CubicBezier(0.4, 0, 0.2, 1))
Rise(easing=Steps(10))
```

<p align="center">
  <img src="assets/animation_easing_back.svg" alt="overshoot easing" width="49%">
  <img src="assets/animation_easing_bezier.svg" alt="custom curve easing" width="49%">
  <img src="assets/animation_easing_steps.svg" alt="steps easing" width="49%">
</p>

<a id="repeating"></a>

<p align="center">
  <img src="assets/animations_repeating.svg" alt="Repeating animations" width="900">
</p>

```python
from svgblock import Pulse

Pulse()                  # runs once
Pulse(loop_limit=4)      # runs five times
Pulse(loop_limit=None)   # never stops
```

<a id="sequences"></a>

<p align="center">
  <img src="assets/animations_sequence.svg" alt="Sequences" width="900">
</p>

```python
from svgblock import Hide, Show, Pop, Pulse, Rise, Sequence

Sequence(Pop(), Show(3), loop_limit=None)

Sequence(Hide(0.5), Rise(), Pulse(loop_limit=1), Show(2), loop_limit=None)
```

<p align="center">
  <img src="assets/animation_seq_pop_show.svg" alt="replay sequence" width="49%" valign="top">
  <img src="assets/animation_seq_hide_pulse_show.svg" alt="enter, then pulse sequence" width="49%" valign="top">
</p>

<a id="animation-errors"></a>

<p align="center">
  <img src="assets/animations_errors.svg" alt="Animation errors" width="900">
</p>

```python
from svgblock import CubicBezier, Pulse, Rise, Sequence, Show

Rise(distance=-10)                 # ValueError: distance must be 0 or more
Rise(loop_limit=2)                 # TypeError: unexpected keyword argument 'loop_limit'
Rise(easing="ease-out")            # TypeError: easing must be an Easing, such as EaseOut() ...
CubicBezier(1.5, 0, 0.5, 1)        # ValueError: x1 must be between 0 and 1
Sequence(Rise, Pulse())            # TypeError: A sequence step must be an animation, such as Rise() ...

# ValueError: the Show after an infinite step would never play
Sequence(Pulse(loop_limit=None), Show(1))
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
from svgblock import Block, ThemeData

ocean = ThemeData(
    background_center="#1B2B34", background_edge="#0B1014",
    border_start="#6699CC", border_end="#223344",
    title_text="#99C794", title_bar="#99C794",
    subsection_text="#FAC863", subsection_marker="#FAC863",
    text="#D8DEE9", highlight="#FFFFFF",
    underline="#6699CC", strikethrough="#65737E", italic="#C0C5CE",
    table_background="#10181D", table_header_background="#223540",
    table_header_text="#99C794", table_text="#D8DEE9",
    table_divider="#33505F", table_stripe_background="#15222A",
    table_border="#33505F", divider="#6699CC",
)

Block(theme=ocean).title("Ocean").text("A theme created in my own code.").save("assets/ocean.svg")
```

<a id="editing-a-theme"></a>

<p align="center">
  <img src="assets/edit_theme.svg" alt="Editing a theme" width="900">
</p>

```python
from svgblock import Block, Theme

# Changes the theme for the whole program: set it before building the blocks
Theme.RED.value.update(title_text="#FF9900", title_bar="#FF9900")
Block(theme=Theme.RED).title("Orange titles on the red theme")

# Makes a variation and keeps the original untouched
softer_red = Theme.RED.value.copy()
softer_red.update(background_center="#2A1414", text="#FFD9D9")
Block(theme=softer_red).title("A softer red")
```

<a id="constants-reference"></a>

<p align="center">
  <img src="assets/constants.svg" alt="Constants reference" width="900">
</p>

<p align="right"><a href="#table-of-contents">⬆ back to top</a></p>

<a id="themes"></a>

<p align="center">
  <img src="assets/themes_overview.svg" alt="Themes" width="900">
</p>

```python
from svgblock import Block, Theme

Block(theme=Theme.DRACULA)

# List every ready-made theme
for theme in Theme:
    print(theme.name)
```

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
  <img src="assets/footer.svg" alt="Made with love" width="900">
</p>