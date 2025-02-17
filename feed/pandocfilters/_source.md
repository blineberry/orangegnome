<div id="main" role="main">

<nav id="nav">

## Navigation

- [Sections](#sections)
- [Grouping content](#grouping-content)
- [Text-level semantics](#text-level-semantics)
- [Edits](#edits)
- [Embedded content](#embedded-content)
- [Tabular data](#tabular-data)
- [Forms](#forms)
- [Interactive elements](#interactive-elements)
- [Scripting](#scripting)

</nav>

<div id="sections" class="section">

<div>

## Sections

Elements: `<body>`, `<article>`, `<section>`, `<nav>`, `<aside>`, `<h1>–<h6>`, `<header>`, `<footer>`

</div>

<article>

<div>

### `<h1>–<h6>`:

</div>

<!--
        Note that, in this context, this use of <h*>s is not of appropriate
          (accessible) rank, but used for testing purposes.
        -->

# `<h1>` A unique title, specific for the page

## `<h2>` Heading levels should reflect structure, not style

It can also be useful to test how body text below a heading appears on the page, for example to check the margin. This text is wrapped in \<p\> and is a direct sibling to the above \<h2\>.

### `<h3>` If you need a visually smaller title, use CSS

To create a semantically correct HTML structure that's accessible for everyone, make sure you're nesting the headings correctly. Never use more than one \<h1\> per page, and don't skip heading levels.

#### `<h4>` Headings below level 4 are not used as much

##### `<h5>` But that doesn't mean you should forget about them

###### `<h6>` And last, but not least, the heading with the lowest rank

</article>

<article id="article">

<div id="header">

### `<body> + <article> + <section> + <nav> + <aside> + <header> + <footer>`:

</div>

All these tags are already in use on the page. The list below contains links to each use case. See the source code of this file for more details.

- [`<body>`](#body)
- [`<article>`](#article)
- [`<section>`](#sections)
- [`<nav>`](#nav)
- [`<aside>`](#aside)
- [`<header>`](#header)
- [`<footer>`](#footer)

</article>

<footer id="footer">

[Back to top 👆](#body)
</footer>

</div>

<div id="grouping-content" class="section">

<div>

## Grouping content

Elements: `<p>`, `<address>`, `<hr>`, `<pre>`, `<blockquote>`, `<ol>`, `<ul>`, `<li>`, `<dl>`, `<dt>`, `<dd>`, `<figure>`, `<figcaption>`, `<main>`, `<div>`

</div>

<article>

<div>

### `<p>`:

</div>

Paragraphs are usually represented in visual media as blocks of text separated from adjacent blocks by blank lines and/or first-line indentation, but HTML paragraphs can be any structural grouping of related content, such as images or form fields. \[1\]

</article>

<article>

<div>

### `<address>`:

</div>

<address>

Name: Alexander Sandberg  
Street adress: 1 Rover street  
State: N/A  
Planet: Mars  
Digital home: [alexandersandberg.com](https://alexandersandberg.com)  
</address>

</article>

<article>

<div>

### `<hr>`:

</div>

------------------------------------------------------------------------

</article>

<article>

<div>

### `<pre>`:

</div>

    Preformatted text
              will be presented
        exactly as written
              in the         HTML file.
            

</article>

<article>

<div>

### `<blockquote>`:

</div>

> The text inside this blockquote is wrapped in `<p>` tags. Sometimes the quote is really long, and possibly have to occupy multiple lines, but that shouldn't be a problem.

</article>

<article>

<div>

### `<ol> + <ul> + <li>`:

</div>

1.  List item 1
2.  List item 2
    1.  List item 1
3.  List item 3
    - List item 1
    - List item 2
      - List item 1
        1.  List item 1
        2.  List item 2
      - List item 2
    - List item 3
4.  List item 4

- List item 1
  - List item 1
    - List item 1
  - List item 2
- List item 2
- List item 3
  1.  List item 1
  2.  List item 2

</article>

<article>

<div>

### `<dl> + <dt> + <dd>`:

</div>

This is a term  
And this is the accompanying description, explaining the above term.

You can also have multiple descriptions (`<dt>`), like this one, for each term (`<dt>`).

And why not nest lists inside this description?

Another term  
With some description.

- List item 1

1.  List item 1
2.  List item 2

</article>

<article>

<div>

### `<figure> + <figcaption>`:

</div>

Used with an `<img>`:

<figure>
<img src="https://placekeanu.com/600/300" alt="Keanu Reeves looking fine" />
<figcaption>Wholesome Keanu Reeves from <a href="https://placekeanu.com" target="_blank">placekeanu.com</a>.</figcaption>
</figure>

Used with a `<blockquote>`:

<figure>
<blockquote>
<p>Seek wealth, not money or status. Wealth is having assets that earn while you sleep. Money is how we transfer time and wealth. Status is your place in the social hierarchy.</p>
</blockquote>
<figcaption><cite>Naval Ravikant (@naval)</cite> on <a href="https://twitter.com/naval/status/1002103497725173760">Twitter</a>.</figcaption>
</figure>

</article>

<article>

<div>

### `<main>`:

</div>

See the [main content](#main) of this page for a use case of `<main>`.

</article>

<article>

<div>

### `<div>`:

</div>

<div>

This paragraph of text is contained inside a `<div>`. The element really has no special meaning, other than grouping content together, and should be used as a last resort when no other element is suitable.

</div>

</article>

<footer>

[Back to top 👆](#body)
</footer>

</div>

<div id="text-level-semantics" class="section">

<div>

## Text-level semantics

Elements: `<a>`, `<em>`, `<strong>`, `<small>`, `<s>`, `<cite>`, `<q>`, `<dfn>`, `<abbr>`, `<ruby>`, `<rb>`, `<rt>`, `<rtc>`, `<rp>`, `<data>`, `<time>`, `<code>`, `<var>`, `<samp>`, `<kbd>`, `<sub>`, `<sup>`, `<i>`, `<b>`, `<u>`, `<mark>`, `<bdi>`, `<bdo>`, `<span>`, `<br>`, `<wbr>`

</div>

<article id="a">

<div>

### `<a>`:

</div>

Here is [a link](#a) inside a paragraph of text. Below you can find a list of links with different `href` attributes.

- [Link to an external website](https://github.com/alexandersandberg/html5-elements-tester)
- [Anchor link to this element](#a)
- [Link with an empty `href` attribute]()
- Link missing an `href` attribute

</article>

<article>

<div>

### `<em> + <i> + <strong> + <b>`:

</div>

The `<em>` element represents *stress emphasis* of its contents. Meanwhile, `<i>` is since HTML5 used for text in an alternative voice or mood, or otherwise offset from the *normal prose*, as you may define it.

If you want to **draw attention** to some text, feel free to use `<b>`. However, if you want to mark the importance of something, **you should use `<strong>`**.

</article>

<article>

<div>

### `<small> + <u> + <mark> + <s>`:

</div>

<span class="small">When you want your text to represent small print, use `<small>`.</span>

In most cases, there's a better element than `<u>` to use, but it can be useful for labelling <u>msispelt</u> text. Avoid using it, however, where the text could be confused for a hyperlink.

You can <span class="mark">highlight text</span> for reference purposes with `<mark>`, or if the contents is <s>no longer accurate or relevant</s>, wrap it with `<s>`.

</article>

<article>

<div>

### `<abbr> + <dfn>`:

</div>

By wrapping an abbreviation like <span class="dfn"><abbr title="Cascading Style Sheets">CSS</abbr></span> in both `<dfn>` and `<abbr>`, we define the term. This can later be used only using `<abbr>`, since we already defined <abbr title="Cascading Style Sheets">CSS</abbr> once before.

</article>

<article>

<div>

### `<q> + <cite> + <data> + <time>`:

</div>

When citing creative work, include the reference with a `<cite>` element. <cite>www.w3.org</cite> explains that “A citation is not a quote (for which the `<q>` element is appropriate)” instead, like used here.

If you want to link content with a <data value="123">machine-readable</data> translation, use `<data>` with a `value` attribute. However, if this data is a time- or date-related, like the date <time datetime="2019-07-04">July 4</time>, you have to use `<time>` together with the `datatime` attribute.

</article>

<article>

<div>

### `<code> + <var> + <samp> + <kbd> + <sub> + <sup>`:

</div>

When sharing code-snippets, make sure to use the `<code>` element. This can be done both `display: inline;`, as well as block-level:

    * {
    color: rebeccapurple;
    background: aliceblue;
    }

Variables should be surrounded by `<var>`, or `x` amount of people might be confused.

Sample or quotes output are represented with `<samp>`: `Your expression '1 + 1' equals 2`.

To represent user input, like the shortcut <span class="kbd"><span class="kbd">Cmd</span> + <span class="kbd">R</span></span> on macOS, use `<kbd>`.

If you want to <sub>subscript</sub> or <sup>superscript</sup> text, use `<sub>` or `<sup>`.

</article>

<article>

<div>

### `<bdi> + <bdo> + <ruby> + <rb> + <rt> + <rtc> + <rp>`:

</div>

Consider using `<bdi>` when working with bidirectional content, like the names <bdi>Alexander</bdi> and <bdi>علي‎</bdi>.

If you need to override the bidirectional algorithm for some content and its children, use `<bdo>`:

<span dir="rtl">Don't forget to specify the `dir` attribute!</span>

<span dir="ltr">I said, don't forget to specify the `dir` attribute!</span>

Some use of `<ruby>` and its related elements:

<ruby>
漢 <rp>(</rp><rt>Kan</rt><rp>)</rp>
字 <rp>(</rp><rt>ji</rt><rp>)</rp>
</ruby>  
<ruby><rb>旧<rb>金<rb>山<rt>jiù<rt>jīn<rt>shān<rtc>San Francisco</ruby>

More information about the explanation and usage of these can be <a href="https://www.w3.org/TR/2017/REC-html52-20171214/single-page.html#the-ruby-element" target="_blank">read here on www.w3.org</a>.

</article>

<article>

<div>

### `<span> + <br> + <wbr>`:

</div>

A `<span>` can be used to mark up inline text for various uses, <span style="font-weight: bolder;">here to make the text bolder</span>.

If you have really long text you might want to insert a  
blank line with the `<br>` element. You can also insert word breaking opportunities using `<wbr>`, to help the browser break long words like Pneumonoultramicro<wbr>scopicsilico<wbr>volcanoconiosis.

</article>

<footer>

[Back to top 👆](#body)
</footer>

</div>

<div id="edits" class="section">

<div>

## Edits

Elements: `<ins>`, `<del>`

</div>

<article>

<div>

### `<ins> + <del>`:

</div>

If you make a <s>really huge</s> mistake, you can always go back and fix it later. <u>And don't forget to learn from your mistake.</u>

<ins>

Both `<ins>` and `<del>` can be block-level, like this.

</ins>

<del>

Here's a block-level paragraph removal.

</del>

</article>

<footer>

[Back to top 👆](#body)
</footer>

</div>

<div id="embedded-content" class="section">

<div>

## Embedded content

Elements: `<picture>`, `<source>`, `<img>`, `<iframe>`, `<embed>`, `<object>`, `<param>`, `<video>`, `<audio>`, `<track>`, `<map>`, `<area>`, `<math>`, `<svg>`

</div>

<article>

<div>

### `<img> + <svg>`:

</div>

![Keanu Reeves looking fine](https://placekeanu.com/600/250/g)
<svg height="250" width="510">

<polygon points="220,10 300,210 200,245 123,234" style="fill:tomato;stroke:rebeccapurple;stroke-width:5"></polygon>
This is a fallback message. If you see this, your browser does not support inline SVG.
</svg>

</article>

<article>

<div>

### `<picture> + <source>`:

</div>

A different image will be shown depending on viewport size.

<picture>
<source srcset="https://placekeanu.com/800/400/y" media="(min-width: 1200px)">

![Keanu Reeves looking fine](https://placekeanu.com/400/300)
</picture>
</article>

<article>

<div>

### `<iframe>`:

</div>

<iframe src="https://maps.google.com/maps?width=100%&amp;height=600&amp;hl=en&amp;q=New%20york+(HTML5%20Elements%20Tester)&amp;ie=UTF8&amp;t=k&amp;z=14&amp;iwloc=B&amp;output=embed">

</iframe>

</article>

<article>

<div>

### `<embed>`:

</div>

<embed src="http://techslides.com/demos/samples/sample.webm" type="video/webm">

</article>

<article>

<div>

### `<object> + <param>`:

</div>

<object data="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" type="application/pdf">

<param name="parameter" value="example">
</object>

</article>

<article>

<div>

### `<video> + <audio> + <track>`:

</div>

<audio controls src="https://interactive-examples.mdn.mozilla.net/media/examples/t-rex-roar.mp3">

This is a fallback text. If you see this, your browser does not support embedded audio.

</audio>

Audio is from [an example on MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio).

<video controls width="400">

<source src="https://interactive-examples.mdn.mozilla.net/media/examples/friday.mp4" type="video/mp4">

<track default kind="captions" srclang="en" src="https://interactive-examples.mdn.mozilla.net/media/examples/friday.vtt">

This is a fallback text. If you see this, your browser does not support embedded videos.

</video>

Video and subtitles are from [an example on MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track).

</article>

<article>

<div>

### `<map> + <area>`:

</div>

Each side of the image below is linked to different anchors on this page. Give it a try!

<map name="image-map" id="image-map">

<area shape="circle" coords="75,75,75" href="#image-map">

<area shape="circle" coords="275,75,75" href="#body">

</map>

<img src="https://placekeanu.com/350/150/y" usemap="#image-map" alt="Keanu Reeves looking fine" />
</article>

<article>

<div>

### `<math>`:

</div>

The quadratic formula is:  
$x = \frac{- b \pm \sqrt{b^{2} - 4ac}}{2a}$

</article>

<footer>

[Back to top 👆](#body)
</footer>

</div>

<div id="tabular-data" class="section">

<div>

## Tabular data

Elements: `<table>`, `<caption>`, `<colgroup>`, `<col>`, `<tbody>`, `<thead>`, `<tfoot>`, `<tr>`, `<td>`, `<th>`

</div>

<article>

<div>

### `<table> + <caption> + <colgroup> + <col>+ <tbody> + <thead> + <tfoot> + <tr> + <td> + <th>`:

</div>

<table>
<caption>This is the table caption</caption>
<thead>
<tr>
<th><code>&lt;thead&gt;</code></th>
<th>2nd colgroup</th>
<th>2nd colgroup</th>
</tr>
</thead>
<tbody>
<tr>
<th scope="row"><code>&lt;tbody&gt;</code></th>
<td colspan="2">This is a cell spanning two columns</td>
</tr>
</tbody><tfoot>
<tr>
<td scope="row"><code>&lt;tfoot&gt;</code></td>
<td>Cell 2</td>
<td>Cell 3</td>
</tr>
</tfoot>
&#10;</table>

</article>

<footer>

[Back to top 👆](#body)
</footer>

</div>

<div id="forms" class="section">

<div>

## Forms

Elements: `<form>`, `<label>`, `<input>`, `<button>`, `<select>`, `<datalist>`, `<optgroup>`, `<option>`, `<textarea>`, `<output>`, `<progress>`, `<meter>`, `<fieldset>`, `<legend>`

</div>

<article>

<div>

### `<form> + <label> + <input> + <button> + <select> + <datalist> + <optgroup> + <option> + <textarea> + <fieldset> + <legend>`:

</div>

<form action="#forms">

<fieldset>

<legend>Welcome to the form</legend>

<label for="input-hidden">
Hidden: <input type="hidden" id="input-hidden">
</label>

<label for="input-text">
Text: <input type="text" id="input-text">
</label>

<label for="input-text-readonly">
Text (readonly): <input type="text" id="input-text-readonly" value="You can&#39;t change this" readonly>
</label>

<label for="input-text-disabled">
Text (disabled): <input type="text" id="input-text-disabled" value="This is not available" disabled>
</label>

<label for="input-search">
Search: <input type="search" id="input-search">
</label>

<label for="input-tel">
Telephone: <input type="tel" id="input-tel">
</label>

<label for="input-url">
URL: <input type="url" id="input-url">
</label>

<label for="input-email">
Email: <input type="email" id="input-email">
</label>

<label for="input-password">
Password: <input type="password" id="input-password">
</label>

<label for="input-date">
Date: <input type="date" id="input-date">
</label>

<label for="input-month">
Month: <input type="month" id="input-month">
</label>

<label for="input-week">
Week: <input type="week" id="input-week">
</label>

<label for="input-time">
Time: <input type="time" id="input-time">
</label>

<label for="input-datetime-local">
Datetime-local: <input type="datetime-local" id="input-datetime-local">
</label>

<label for="input-number">
Number: <input type="number" id="input-number">
</label>

<label for="input-range">
Range: <input type="range" id="input-range">
</label>

<label for="input-color">
Color: <input type="color" id="input-color">
</label>

<p>

<label for="input-checkbox-1">
Checkbox 1:
<input type="checkbox" id="input-checkbox-1" name="checkbox">

</label>
<label for="input-checkbox-2">
Checkbox 2:
<input type="checkbox" id="input-checkbox-2" name="checkbox">

</label>
<label for="input-checkbox-3">
Checkbox 3 (disabled):
<input type="checkbox" id="input-checkbox-3" name="checkbox" disabled>

</label>
</p>

<label for="input-radio-1">
Radio 1: <input type="radio" id="input-radio-1" name="radio">
</label>
<label for="input-radio-2">
Radio 2: <input type="radio" id="input-radio-2" name="radio">
</label>
<label for="input-radio-3">
Radio 3 (disabled): <input type="radio" id="input-radio-3" name="radio" disabled>
</label>

<label for="select">
Select: <select name="select" id="select">
<option value="1">Option 1</option>
<option value="2">Option 2</option>
<option value="3">Option 3</option>
</select>
</label>

<label for="select-size">
Select (size): <select name="select-size" id="select-size" size="5">
<option value="1">Option 1</option>
<option value="2">Option 2</option>
<option value="3">Option 3</option>
<option value="4">Option 4</option>
<option value="5">Option 5</option>
<option value="6">Option 6</option>
<option value="7">Option 7</option>
<option value="8">Option 8</option>
</select>
</label>

<label for="select-multiple">
Select (multiple): <select name="select-multiple" id="select-multiple" multiple>
<option value="1">Option 1</option>
<option value="2">Option 2</option>
<option value="3">Option 3</option>
</select>
</label>

<label for="select-optgroup">
Select with optgroup: <select name="select-optgroup" id="select-optgroup">
<optgroup label="Group 1">
<option value="1">Option 1</option>
<option value="2">Option 2</option>
</optgroup>
<optgroup label="Group 2">
<option value="3">Option 3</option>
<option value="4">Option 4</option>
<option value="5">Option 5</option>
</optgroup>
</select>
</label>

<label for="datalist">
Datalist:
<input name="datalist" list="datalist">
<datalist id="datalist">
<option value="Option 1">
<option value="Option 2">
<option value="Option 3">
<option value="Option 4">
</datalist>
</label>

<p>

<label for="textarea">
Textarea:
<textarea name="textarea" id="textarea"></textarea>

</label>
</p>

<label for="input-file">
File (single): <input type="file" id="input-file">
</label>

<label for="input-file-multiple">
File (multiple): <input type="file" id="input-file-multiple" multiple>
</label>

<label for="input-submit">
Submit: <input type="submit" id="input-submit">
</label>

<label for="input-image">
Image button: <input type="image" id="input-image" src="https://placekeanu.com/100/40">
</label>

<label for="input-reset">
Reset: <input type="reset" id="input-reset">
</label>

<label for="input-button">
Button: <input type="button" id="input-button" value="I&#39;m an input with type=button">
</label>

<button type="button">I'm a `<button>`</button>

</fieldset>

</form>

</article>

<article>

<div>

### `<output>`:

</div>

<form onsubmit="return false" oninput="o.value = a.valueAsNumber + b.valueAsNumber">

<fieldset>

<legend>Testing the `<output>` element</legend>
<input name="a" type="number" step="any"> +
<input name="b" type="number" step="any"> =
<output name="o" for="a b">

</output>

Code is taken from <a href="https://www.w3.org/TR/2017/REC-html52-20171214/single-page.html#example-5b22c23a" target="_blank">this example by W3</a>.

</fieldset>

</form>

</article>

<article>

<div>

### `<progress> + <meter>`:

</div>

<form action="#forms">

<fieldset>

<legend>Testing `<progress>` and `<meter>`</legend>

<label for="progress">
Progress: <progress id="progress" max="100" value="64">64%</progress>
</label>

<label for="meter-2">
Meter (ok): <meter id="meter-2" max="100" low="30" high="80" optimum="50" value="50">50/100</meter>
</label>

<label for="meter-1">
Meter (warning): <meter id="meter-1" max="100" low="30" high="80" optimum="50" value="20">20/100</meter>
</label>

<label for="meter-3">
Meter (critical): <meter id="meter-3" max="100" low="60" high="70" value="90">80/100</meter>
</label>

</fieldset>

</form>

</article>

<footer>

[Back to top 👆](#body)
</footer>

</div>

<div id="interactive-elements" class="section">

<div>

## Interactive elements

Elements: `<details>`, `<summary>`, `<dialog>`

</div>

<article>

<div>

### `<details> + <summary>`:

</div>

<details>

<summary>

This can be expanded
</summary>

And by doing so, more information is revealed.

</details>

</article>

<article>

<div>

### `<dialog>`:

</div>

<dialog>

This text is inside a `<dialog>` box! It should be hidden by default, and shown to the user when given an `open` attribute.

</dialog>
</article>

<footer>

[Back to top 👆](#body)
</footer>

</div>

<div id="scripting" class="section">

<div>

## Scripting

Elements: `<script>`, `<noscript>`, `<template>`, `<canvas>`

</div>

<article>

<div>

### `<script> + <noscript>`:

</div>

Dynamic scripts and data blocks are included with the `<script>` element.

<script>
          document.write('<p>This paragraph was generated with JavaScript!</p>');
        </script>

If scripting is disabled when loading the page, content inside `<noscript>` is used instead.

<noscript>

I see you disabled JavaScript!

</noscript>

</article>

<article>

<div>

### `<template>`:

</div>

Below this paragraph, there's a `<template>` element containing a HTML declaration, that can be used by scripts.

<template>

Hi! I'm a paragraph inside the `<template>` element.

</template>
</article>

<article>

<div>

### `<canvas>`:

</div>

A `<script>` is used to draw a rectangle in the `<canvas>` below.

<canvas id="canvas">

Alternative text explaining what's on display in this \<canvas\>.
</canvas>

<script>
          var canvas = document.getElementById('canvas');
          var ctx = canvas.getContext('2d');
          ctx.fillStyle = 'tomato';
          ctx.fillRect(10, 10, 100, 100);
        </script>

</article>

<footer>

[Back to top 👆](#body)
</footer>

</div>

</div>
