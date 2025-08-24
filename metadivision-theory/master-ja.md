---
title: 多次元グルーヴ空間理論
created: 2025-05-27T11:07
format: html
execute:
  enabled: true
  echo: false
  output: true
  eval: true
  cache: false
title-block: false
tags:
  - foo
---

リズムを明確かつ精密に認識するための基礎的な技術──それが「グルーヴ空間理論」です。この理論は、オフビートカウント理論を土台として作られたもので、様々なジャンルの音楽のグルーヴを解析できる様に拡張されたものです。世界中のリズムが持っている **分裂拍(Schizorythymos)** の本質を様々な方法を使って把握する為に汎用可能な理論を提供します。

## 多次元グルーヴ空間理論とは

グルーヴ空間理論とは、拍の数え方を拡張する為の理論です。 これまで  **ディヴィジョン（拍 =４分音符）** と **サブディヴィジョン（分拍＝連符）**  に対して数を数える方法を御説明致しました。このディヴィジョンを**多次元化** を使って４つの **グルーヴ空間**に拡張することにより、幅広いグルーヴの理解を行うことができる様にする理論がグルーヴ空間理論です。

グルーヴ空間理論では、ディヴィジョン・サブディヴィジョンを1つの **グルーヴ空間**として扱います。

そしてこのグルーヴ空間を**多次元化**を使って拡張し**マクロディヴィジョン(小節)** と **マイクロディヴィジョン(ずれニュアンス)** という２つの新しい **グルーヴ空間**を定義します。

一般的にグルーヴと言われているリズムは、小節自体も拍とみなし小節にも弱拍先行を適用することによって説明出来るという **マクロディヴィジョン・グルーヴ空間** という概念を御紹介致します。

次に、一般的にレイドバック・ラッシュ・ドラッグ等々と呼ばれている音符のずれによるニュアンスの表現は、譜面上に表される **サブディヴィジョン(分拍)** よりも更に細かい音符 **マイクロディヴィジョン(微分拍)**空間 が存在すると仮定し、これらに弱拍先行を適用することで合理的に説明できる ─── という理論を御紹介致します。

音符のずれによるニュアンスの表現は、**ディヴィジョン（拍）**  を **マクロディヴィジョン（小節＝合拍）** とみなし **サブディヴィジョン（連符＝分拍）**をディヴィジョンとみなした時のサブディヴィジョンによる弱拍先行リズムとして表現が可能になる ─── **グルーヴ空間転送** という理論を御説明致します。

これらの理論を使うことで、グルーヴ習得の為の具体的な練習方法を考案したり、DAW上で機械的にグルーヴを再現することが出来るようになります。

<!--
<div class="ats4u-twitter-video">https://x.com/ats4u/status/1754113170548175104</div>
<div class="ats4u-twitter-video" >https://x.com/ats4u/status/1741136150394458596</div>
-->
   

## ４つのグルーヴ空間
これまでオフビートカウントで拍を数えるにあたって、４分音符１つを１拍とする単位（ディヴィジョン）で数えて来ました。

そして４分音符を分割して出来る８分音符や３連符などの拍（サブ・ディヴィジョン）については、数字ではなく **＆** **Ｅ** **Ａ** の３つの 記号/アルファベット を割り当てることで数えてきました。

このディヴィジョン・サブディヴィジョンのことをここでは**グルーヴ空間** と呼びます。 通常のリズム理論ではこのグルーヴ空間は、**ディヴィジョン** と **サブディヴィジョン** の２つが存在します。

グルーヴ空間理論では、この２つのグルーヴ空間を**多次元化**という処理を加えることにおって拡張し４つのグルーヴ空間を定義します。

* ４つのグルーヴ空間
  * マクロ・ディヴィジョン(小節=合拍=Macrodivision)
  * ディヴィジョン (4分音符=拍=Division )
  * サブ・ディヴィジョン (８分音符等々の分音符=分拍=Subdivision )
  * マイクロ・ディヴィジョン(音符では書き表せない拍＝微分拍=Microdivision)

そしてこの４つのグルーヴ空間の特徴を説明致します。

<style>
  .divisions {
    border : 1px silver solid;
  }
  .divisions td {
    border : 1px silver solid;
    padding: 10px;
  }
  .divisions td.one {
    border-left : 5px silver double;
  }

  .divisions tr.r1 td,
  .divisions tr.r2 td,
  .divisions tr.r3 td,
  .divisions tr.r4 td {
    border-top : 5px silver double;
  }

  .divisions td.l1,
  .divisions td.l2,
  .divisions td.l3,
  .divisions td.l4,

  .divisions td.m1,
  .divisions td.m2,
  .divisions td.m3,
  .divisions td.m4,

  .divisions td.n1,
  .divisions td.n2,
  .divisions td.n3,
  .divisions td.n4
  {
    color : white;
    font-weight: 1000;
    text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
  }

  .divisions td.l1 {
    background-color : #DFD;
  }
  .divisions td.l2 {
    background-color : #9F9;
  }
  .divisions td.l3 {
    background-color : #5F5;
  }
  .divisions td.l4 {
    background-color : #1F1;
  }
  .divisions td.m1 {
    background-color : #DDF;
  }
  .divisions td.m2 {
    background-color : #99F;
  }
  .divisions td.m3 {
    background-color : #55F;
  }
  .divisions td.m4 {
    background-color : #11F;
  }
  .divisions td.n1 {
    background-color : #FDD;
  }
  .divisions td.n2 {
    background-color : #FAA;
  }
  .divisions td.n3 {
    background-color : #F66;
  }
  .divisions td.n4 {
    background-color : #F22;
  }

  .perspwrap{
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;   /* center horizontally in the column */
    perspective: var(--persp, 600px);
    perspective-origin: 50% 0%;
  }

  .perspinner{
    position: absolute;
    transform-origin: top center;
  }

  .perspinner > table{
    border-collapse: collapse;
  }

  .persptable {
    /*transform: perspective(600px) rotateX(70deg);*/
    transform-origin: top center;
    border-collapse: collapse;
  }
  .persptable th, 
  .persptable td {
    border: 1px solid #666;
    padding: 0.4em 0.6em;
    background: white;
  }
</style>
<script>
(function(){
  function fitPerspective(wrap){
    const tilt  = parseFloat(wrap.dataset.tilt  || 70);
    const persp = parseFloat(wrap.dataset.persp || 600);

    // ensure wrapper has the camera + origin centered
    wrap.style.setProperty('--persp', `${persp}px`);
    wrap.style.perspectiveOrigin = '50% 0%';

    let inner = wrap.querySelector(':scope > .perspinner');
    if(!inner){
      inner = document.createElement('div');
      inner.className = 'perspinner';
      const child = wrap.firstElementChild;
      wrap.appendChild(inner);
      inner.appendChild(child);
    }

    inner.style.transform = 'none';
    wrap.style.height = 'auto';
    const h = inner.getBoundingClientRect().height;
    const rad = tilt * Math.PI / 180;
    wrap.style.height = (h * Math.cos(rad)) + 'px';
    inner.style.transform = ` rotateY(15deg) rotateX(${tilt}deg) `; // camera on wrapper
  }

  function init(){ document.querySelectorAll('.perspwrap').forEach(fitPerspective); }
  addEventListener('load', init);
  addEventListener('resize', init);
})();


</script>
```{python}
#| output: asis

from html import escape
from typing import Any, Iterable, Sequence

def show_beat(beats: Sequence[Sequence[Any]],
              col_classes : Sequence[Sequence[Any]] | None = None,
              row_classes : Sequence[Any]           | None = None,
              table_class : str = "divisions" ) -> str:
    """
    Render a 2D HTML table from `beats`, using `col_classes` for per-cell CSS classes.

    - beats[y][x]: cell text (any type; converted to string).
    - col_classes[y][x]: CSS class string (used if truthy and not None).
      If col_classes is None or missing indices, no class attribute is added.

    Returns a complete <table class="divisions">…</table> string.
    """

    col_classes and interpolate2d(col_classes)
    row_classes and interpolate2d(row_classes)

    # Determine max columns across all beat rows (supports ragged input)
    max_cols = max((len(row) for row in beats), default=0)

    html_parts: list[str] = []
    html_parts.append( f'<table class="{table_class}">' )

    for y, row in enumerate(beats):
        if row_classes is not None and y < len(row_classes):
            crow = row_classes[y]
            html_parts.append( f"<tr class=\"{crow}\">")
        else:
            html_parts.append("<tr>")

        for x in range(max_cols):
            # Cell content
            if x < len(row):
                cell_text = escape(str(row[x]))
            else:
                cell_text = ""  # pad short rows with empty cells

            # Resolve class from col_classes if present/valid
            klass_attr = ""
            if col_classes is not None and y < len(col_classes):
                krow = col_classes[y]
                if x < len(krow):
                    k = krow[x]
                    if k is not None:
                        k_str = str(k).strip()
                        if k_str:
                            klass_attr = f' class="{escape(k_str)}"'

            html_parts.append(f"<td{klass_attr}>{cell_text}</td>")
        html_parts.append("</tr>")

    html_parts.append("</table>")

    return "".join(html_parts)

def interpolate2d(array2d):
    # Replace matching variable names with their values, but skip None
    for i, row in enumerate(array2d):
        if row is None:
            continue
        for j, val in enumerate(row):
            if val is None:
                continue
            if val in globals():           # variable name exists
                value = globals()[val]
                if value is not None:      # skip replacing with None
                    array2d[i][j] = value

def split2d(text):
    return [ line.split() for line in text.strip().split("\n") ]

R1="one r1"
R2="one r2"
R3="one r3"
R4="one r4"

L1="one l1"
L2="one l2"
L3="one l3"
L4="one l4"
M1="one m1"
M2="one m2"
M3="one m3"
M4="one m4"
N1="one n1"
N2="one n2"
N3="one n3"
N4="one n4"

l1="l1"
l2="l2"
l3="l3"
l4="l4"
m1="m1"
m2="m2"
m3="m3"
m4="m4"
n1="n1"
n2="n2"
n3="n3"
n4="n4"

N0="one"
N=None
n=None

```

### ディヴィジョンとは

これまで拍を数えるときは**１２３４、１２３４**と小節を繰り返しながら、その各小節内の拍数を数えて来ました。 この小節を分割して出来る数を **ディヴィジョン** と呼びます。

次の表は、ディヴィジョンの例です。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4 ] *4
        ],
        [
            [M1, N, N, N ] *4
        ]
    )
)
```

### 多次元化とは

多次元化とは、次の様に数を数えるときの**桁数** を増やすことをいいます。前章の例で挙げた様にディヴィジョン（拍数）を数える際、次の様に小節数を同時に数えると次のようになります。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ]
        ],
        [
            [N1, N, N, N ] *4
        ]
    )
)
```

この様に拍数を一定の周期で数える時に、その周期の先頭拍で周期が来た回数（小節数）を数えることを **多次元化**と呼びます。又は、これまでのオフビートカウントが発展してきた歴史的経緯から **小節数入りカウント**  呼ばれることもあります。

### マクロディヴィジョンとは

マクロディヴィジョンについて説明します。

#### ディヴィジョンを多次元化する

ここでディヴィジョン自体を多次元化すること考えてみます。次の図は前章で見た図と全く同じディヴィジョンの図です。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4 ] *4
        ],
        [
            [M1, N, N, N ] *4
        ]
    )
)
```

このディヴィジョンを多次元化すると次の図になります。これも前章で見た図と全く同じ図です。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ]
        ],
        [
            [N1, N, N, N ] *4
        ]
    )
)
```

このように多次元化されたディヴィジョンのことを **マクロディヴィジョン (Macrodivision)** と呼びます。

#### マクロディヴィジョンを多次元化する

このように、小節数入りで数えている時、ある数の小節のまとまりに対して更にもうひとつ次元を増やして数えると次の様になります。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
        ],
        [
            [N1, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
        ]
    )
)
```

このように数えることを**マクロディヴィジョンの多次元化** と呼びます。また多次元化されたマクロディヴィジョンを **二次元マクロディヴィジョン(Double-Layered Macrodivision)** と呼びます。

#### 多次元化したマクロディヴィジョンをもう一度多次元化する

既に多次元化したマクロディヴィジョンを更に多次元化することも可能です。 次の様に更にもう一次元増やすことで**三次元マクロディヴィジョン(Triple-Layered Macrodivision)** を構築できます。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
        ],
        [
            [L1, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
            [L2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
            [L3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
            [L4, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
        ],
        [
            N,
            N,
            N,
            N,
            R1,
            N,
            N,
            N,
            R1,
            N,
            N,
            N,
            R1,
            N,
            N,
            N,
        ]
    )
)
```

#### 多次元化したマクロディヴィジョンの呼び方

多次元化したマクロディヴィジョンの次元の呼び方を説明します。 

##### 一次元マクロディヴィジョン＝第一次元
次の様に数えることを**一次元マクロディヴィジョン(One-Dimensional Macrodivision)**と呼びます。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
        ],
        [
            [M1, N, N, N ] + [ M1, N, N, N ] * 3,
            [M1, N, N, N ] + [ M1, N, N, N ] * 3,
            [M1, N, N, N ] + [ M1, N, N, N ] * 3,
            [M1, N, N, N ] + [ M1, N, N, N ] * 3,
        ]
    )
)
```
そしてここでは、この次元を **第一次元** と呼びます。

##### 二次元マクロディヴィジョン＝第二次元
次の様に数えることを**二次元マクロディヴィジョン(Two-Dimensional Macrodivision)** と呼びます。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
        ],
        [
            [N1, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
        ]
    )
)
```
そしてここでは、この次元を **第二次元** と呼びます。

##### 三次元マクロディヴィジョン＝第三次元
次の様に数えることを**三次元マクロディヴィジョン(Three-Dimensional Macrodivision)** と呼びます。

```{python}
#| output: asis
print(
    show_beat(
        [
            [ 1, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 2, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 3, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
            [ 4, 2, 3, 4, 2, 2, 3, 4, 3, 2, 3, 4, 4, 2, 3, 4 ],
        ],
        [
            [L1, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
            [L2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
            [L3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
            [L4, N, N, N ] + [ M1, N, N, N ] * 3,
            [N2, N, N, N ] + [ M1, N, N, N ] * 3,
            [N3, N, N, N ] + [ M1, N, N, N ] * 3,
            [N4, N, N, N ] + [ M1, N, N, N ] * 3,
        ],
        [
            N,
            N,
            N,
            N,
            R1,
            N,
            N,
            N,
            R1,
            N,
            N,
            N,
            R1,
            N,
            N,
            N,
        ]
    )
)
```

この３つ目の次元を**第三次元**と呼びます。

### サブディヴィジョンとは

サブディヴィジョンとは、声出しカウントを行う時に数字の間にいれるアルファベットと記号のことです。

```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a 2 e & a 3 e & a 4 e & a
        """),
        split2d("""
            N0 m1 m1 m1 N0 m1 m1 m1 N0 m1 m1 m1 N0 m1 m1 m1
        """)
    )
)
```

サブディヴィジョンをカウントする時は数字ではなく、記号（＆）とアルファベットを使います。ここで使われる記号アルファベットは次の通りです。

* a ( アー )
* & ( アンド )
* e (イー)

ここではこのサブディヴィジョンを多次元化します。

#### サブディヴィジョンの多次元化する

サブディヴィジョンの多次元化は、これまで数字に対して行っていた多次元化を、記号アルファベットに対して行うことを言います。

次のようにサブディヴィジョンがあったとします。

```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a 
        """),
        split2d("""
            M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 
        """)
    )
)
```

この通常のサブディヴィジョンはいわば一次元のサブディヴィジョンということができます。

#### 一次元サブディヴィジョンの多次元化

この 1 e & a を 4回繰り返して読み、更に先頭の記号アルファベットを 1 e & a の順番で入れ替えることにより、あたかも一次元に並んでいる記号アルファベットを、二次元化した上で再度一次元に投影展開するのと同じ処理を行うことが出来ます。

```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a
            e e & a
            & e & a
            a e & a
        """),
        split2d("""
            M1 n0 n0 n0
            M1 n0 n0 n0
            M1 n0 n0 n0
            M1 n0 n0 n0
        """)
    )
)
```

横に並べると次の様になります。

```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a e e & a & e & a a e & a
        """),
        split2d("""
            M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
        """)
    )
)
```

この様にサブディヴィジョンの記号アルファベットを多次元化することを**サブディヴィジョンの多次元化** と呼びます。

#### 多次元化したサブディヴィジョンをもう一度多次元化する

既に多次元化したサブディヴィジョンを更に多次元化することも可能です。 次の様に更にもう一次元増やすことで**三次元マクロディヴィジョン(Triple-Layered Macrodivision)** を構築できます。

```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a e e & a & e & a a e & a
            e e & a e e & a & e & a a e & a
            & e & a e e & a & e & a a e & a
            a e & a e e & a & e & a a e & a
        """),
        split2d("""
            M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
            M2 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
            M3 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
            M4 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
        """)
    )
)
```

この表を立体的に並べてみると次の様になります。

<div class="perspwrap" style="z-index:40"><div class="perspinner">
```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a
            e e & a
            & e & a
            a e & a
        """),
        split2d("""
            M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
        """),
        [],
        "persptable divisions"
      )
    )
```
</div></div>

<div class="perspwrap" style="z-index:30"><div class="perspinner">
```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            e e & a
            e e & a
            & e & a
            a e & a
        """),
        split2d("""
            M2 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
        """),
        [],
        "persptable divisions"
      )
)
```
</div></div>

<div class="perspwrap" style="z-index:20"><div class="perspinner">
```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            & e & a
            e e & a
            & e & a
            a e & a
        """),
        split2d("""
            M3 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
        """),
        [],
        "persptable divisions"
    )
)
```
</div></div>

<div class="perspwrap" style="z-index:10"><div class="perspinner">
```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            a e & a
            e e & a
            & e & a
            a e & a
        """),
        split2d("""
            M4 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
        """),
        [],
        "persptable divisions"
    )
)
```
</div></div>

### 多次元化したサブディヴィジョンの呼び方

#### 一次元サブディヴィジョン＝第一次元

次の様に数えることを**一次元サブディヴィジョン(One-Dimensional Subdivision)**と呼びます。
```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a 
        """),
        split2d("""
            M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 
        """)
    )
)
```

#### 二次元サブディヴィジョン＝第二次元

次の様に数えることを**二次元サブディヴィジョン(Two-Dimensional Subdivision)**と呼びます。

```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a e e & a & e & a a e & a
        """),
        split2d("""
            M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
        """)
    )
)
```

#### 三次元サブディヴィジョン＝第三次元

次の様に数えることを**三次元サブディヴィジョン(Three-Dimensional Subdivision)**と呼びます。


```{python}
#| output: asis
print(
    show_beat(
        split2d( """
            1 e & a e e & a & e & a a e & a
            e e & a e e & a & e & a a e & a
            & e & a e e & a & e & a a e & a
            a e & a e e & a & e & a a e & a
        """),
        split2d("""
            M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
            M2 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
            M3 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
            M4 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0 M1 n0 n0 n0
        """)
    )
)
```

### メタディヴィジョンとは

**メタディヴィジョン**とは、サブディヴィジョンよりも細かい音符の音価領域を表す**グルーヴ空間**のひとつです。譜面に書き表すことができない細かなタイミングニュアンスをメタディヴィジョンという仮想のグルーヴ空間として表します。

メタディヴィジョンは、しばしば **ポケット** ・ **レイドバック** ・ **ラッシング** ・**ドラッギング** ・ **プッシュ** 等々と呼ばれるものと同じものです。 メタディヴィジョンは細かすぎる為、意識的に数えることが出来ません。 しかしこのメタディヴィジョンが音楽が持つ全てのニュアンスの鍵を握っていると言って過言でなく、音楽で最も重要な位置にあるリズム要素と言えます。 メタディヴィジョンは、プレーヤー及びリスナー双方の無意識の動きを制御する本質といえます。 メタディヴィジョンの制御の良し悪しひとつで、音楽はこの世のものとは思えない美しさを持って響くこともあれば、どんなに高度な作曲技法を持って作られた曲であろうと無関係に、無惨にも人の心に墨汁を流しこんだような不快感をもたらすこともあります。  ─── メタディヴィジョンは、音楽の全てと言って過言ではありません。

### メタディヴィジョンの定義

メタディヴィジョンは細かすぎる為にはっきりと数えることが出来ません。しかしここで仮説としてメタディヴィジョンを以下の通りに定義します。

* **メタディヴィジョンは、サブディヴィジョンを多次元化する事で定義できる。**

## グルーヴ空間次元転送について

ディヴィジョンを多次元化したものがサブディヴィジョンであり、かつメタディヴィジョンがサブディヴィジョンを多次元化したものであるならば、それぞれを入れ替えてもリズムは成立する筈です。

* ディヴィジョン → マクロディヴィジョン
* サブディヴィジョン → ディヴィジョン
* メタディヴィジョン→ サブディヴィジョン  （❗❗❗）

つまり

* ゆっくり演奏すると、メタディヴィジョンはサブディヴィジョンになり、サブディヴィジョンはディヴィジョンになり、ディヴィジョンはマクロディヴィジョンに入れ替わるので、メタディヴィジョンも数えることができる。
* マクロディヴィジョン・サブディヴィジョンでの多次元化での様々な複雑なパターンに慣れ親しむことで得られた感覚は、そのままメタディヴィジョンでも応用することが出来る。
* **特にポケットは、メタディヴィジョンでのスコッチスナップである。**
    * → その他の遅れることで生まれるニュアンスは全てここに含まれる。
* **特にプッシュは、メタディヴィジョンでの弱起である。**
    * → その他の早いまることで生まれるニュアンスは全てここに含まれる。

この**グルーヴ空間次元転送**がこの**ハイパーグルーヴ理論の最も重要な理論**と言って過言ではありません。



<!--

#### サブディヴィジョンの多次元化

####多次元化したサブディヴィジョンの多次元化

### マイクロディヴィジョンとは

<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">この曲は3拍子だが、4分音符1つのなかに aid と3つの音素( phoneme )があるので、4分音符を3分割しないと音符を適切に読むことが出来ない。日本語は音符1つに1モーラを割り当てるだけで、モーラには末子音がなく子音が短いので2分割するという感覚を持っていない。ここに根本的感覚の違いがある。 <a href="https://t.co/CcroJRy6yu">https://t.co/CcroJRy6yu</a></p>&mdash; 岡敦/Ats🇯🇵 (@ats4u) <a href="https://twitter.com/ats4u/status/1953003571047489764?ref_src=twsrc%5Etfw">August 6, 2025</a></blockquote>

## オフビートカウントの一般化


## グルーヴ空間とオフビートカウントの組み合わせ

## グルーヴ空間ワープ

次に、一般的にレイドバック・ラッシュ・ドラッグ等々と呼ばれている音符のずれによるニュアンスの表現は、譜面上に表される **サブディヴィジョン(分拍)** よりも更に細かい音符 **マイクロディヴィジョン(微分拍)**空間 が存在すると仮定し、これらに弱拍先行を適用することで合理的に説明できる ─── という理論を御紹介致します。

音符のずれによるニュアンスの表現は、**ディヴィジョン（拍）**  を **マクロディヴィジョン（小節＝合拍）** とみなし **サブディヴィジョン（連符＝分拍）**をディヴィジョンとみなした時のサブディヴィジョンによる弱拍先行リズムとして表現が可能になる ─── **グルーヴ空間ワープ** という理論を御説明致します。

## 拍のレイヤー

これまで「拍 (ディヴィジョン=４分音符）」と、ディヴィジョンを更に分割して出来る「サブディヴィジョン」に対して弱拍先行と多次元を適用するとどうなるかを見てきました。

グルーヴ空間理論とは、拍以外の要素も拍とみなし、再帰的に弱拍先行と多次元を適用できると考える理論です。

グルーヴ空間理論は、まず小節を拍とみなすことが出来るという**マクロディヴィジョン理論**という視点を提示します。そして小節に関しても弱拍先行と多次元を適用することが出来ることを示します。

グルーヴ空間理論は更に、一般的にレイドバック・ラッシュ・ドラッグ等々と表現される音符のずれによるニュアンスの表現について、譜面上に表されるサブディヴィジョンよりも更に細かい音符が存在するという**マクロディヴィジョン理論**を提示します。 この音符のずれはディヴィジョン（拍）を小節としてみなした時の弱拍先行リズムとして表現が可能という仮説を提唱します。

このグルーヴ空間理論については、別章のグルーヴ空間理論とはで更に詳しく見ていきたいと思います。

マイクロディヴィジョンについて説明する文章案
<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">この曲は3拍子だが、4分音符1つのなかに aid と3つの音素( phoneme )があるので、4分音符を3分割しないと音符を適切に読むことが出来ない。日本語は音符1つに1モーラを割り当てるだけで、モーラには末子音がなく子音が短いので2分割するという感覚を持っていない。ここに根本的感覚の違いがある。 <a href="https://t.co/CcroJRy6yu">https://t.co/CcroJRy6yu</a></p>&mdash; 岡敦/Ats🇯🇵 (@ats4u) <a href="https://twitter.com/ats4u/status/1953003571047489764?ref_src=twsrc%5Etfw">August 6, 2025</a></blockquote>

-->

