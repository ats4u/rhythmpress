---
title: 音韻学とオフビートカウント
created: 2025-05-29T03:42
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

この節ではオフビートカウントと音韻学の関係を説明し、オフビートカウントを行う上での適切な発音方法について学びます。 リズムに合わせて英語で数字の数えるときのその発音とリズムだけに絞って完璧に習得すると、英語全体の話す能力と聞き取る能力が完璧になります。またこの練習方法はジャズなどの音楽でのグルーヴ能力を大幅に向上させます。

```{python}
#| output: asis
from pathlib import Path
import sys

# Go one directory up from the current working dir
parent = Path.cwd().parent.parent

if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))

# now imports from project root work

from lib.groovespace import *
```

## リズム認識型とリズム感

８分音符１つ分はやくカウントするオフビートカウントを練習すると、すぐにできようになる人と、長期間に渡ってなかなかできないままの人の二手にはっきりと分かれます。「リズム感がある」「リズム感がない」と言ってしまえばそれまでですが、出来る様になる人はすぐ出来る様になるのに対して、出来る様にならない人は数年単位の時間を掛けてもあまり変化が表れません。

この様な違いが生まれる原因は、その人がもともと持っていた**リズム認識型** の種類の違いによると考えられます。 人間が持っているリズム認識型には様々な種類のものがあります。このリズム認識型は、あたかもポケモンカードの様に様々な種類があり、人によってそれらのカードを持っている数も異なります。

この中でオフビートカウントに必要なリズム認識型を全て持っている人は、直ぐにオフビートカウントが出来るようになり、必要なリズム認識型を持っていなければ、なかなか出来るようになりません。

つまりオフビートカウントに必要なリズム認識型を訓練によって順番に習得することによって、順序立ててオフビートカウントの習得することが出来ます。そしてオフビートカウントに習熟することで、更に様々なリズム認識型を身に付けて様々なグルーヴを演奏出来る様になります。

では、リズム認識型とは一体どのようなものでしょうか。

### リズム認識型とは

主だったリズム認識型にはいくつかの種類があります。

* 弱拍先行リズム認識型
    * １次元＝シラブル拍リズム弱拍先行リズム認識型
    * ２次元=ストレス拍リズム弱拍先行リズム認識型
    * ３次元=アフリカ型リズム弱拍先行リズム認識型
* 強拍先行リズム認識型
* 強拍先行弱拍先行切り替えリズム認識型
* 尻合わせリズム認識型
    * ※ 尻合わせリズム認識の最大長 １６分音符〜８小節まで
* 頭合わせリズム認識型
* 頭合わせ尻合わせ切り替えリズム認識型
* 強拍基軸リズム認識型
* 弱拍基軸リズム認識型


オフビートカウントに必要なリズム認識型のなかで最も重要で、最も習得が難しいものは **弱拍先行** です。

#### シラブル拍リズム弱拍先行リズム認識型

シラブル拍リズムには、**頭音節最大化原則(MPOP=Maximal Prosodic Onset Principle)** という発音規則があります。全ての末子音は、隣接する頭子音にまとめて発音するという規則です。 これはリンキングとも呼ばれます。これは音楽的に見ると弱拍先行と等しいと考えられます。 ここでは**シラブル拍リズム弱拍先行** と呼びます。 そしてこの**シラブル拍弱拍先行**を認識する能力をここでは **シラブル拍リズム弱拍先行リズム認識型**と呼びます。

#### ストレス拍リズム弱拍先行リズム認識型

ストレス拍リズムには **頭音節最大化原則(MPOP=Maximal Prosodic Onset Principle)** という発音規則があります。全ての末音節は、隣接する頭音節にまとめて発音するという規則です。これも音楽的に見ると弱拍先行と等しいと考えられます。 このことをここでは **ストレス拍リズム弱拍先行** と呼びます。そしてこの **ストレス拍リズム弱拍先行** を認識する能力をここでは**ストレス拍リズム弱拍先行リズム認識型**と呼びます。

#### アフリカ型リズム弱拍先行リズム認識型

これは音韻学としては存在しない拍リズムです。またアフリカの音楽には存在しないリズムでもあります。音楽には、音韻学で説明できる単層の拍リズム、複層の拍リズムだけでなく、３重４重の層になった拍リズムが存在します。 これらは７０年代以降にファンクというジャンルで発展し、その後の時代の音楽に影響を与えました。  ─── この３重以上の多層になった弱拍先行のことを、ここでは**アフリカ拍リズム弱拍先行**と呼びます。

アフリカ拍リズム弱拍先行は、言語のリズムを越えた領域にあると考えられており、発音練習では取り扱いません。メタディヴィジョン以降での練習で取り扱います。

#### シラブル拍リズム等時性リズム認識型

シラブル拍リズムには、子音の数が増減しても母音が現れるタイミングは必ず等しいという規則です。 このことを**等時性( Isochrony )** と呼びます。 特にここでは、次で説明するストレス拍の等時性と区別し **シラブル拍リズム等時性** と呼びます。 これを認識するリズム認識型が **シラブル拍リズム等時性リズム認識型** です。

#### アフリカ拍リズム等時性リズム認識型

ストレス拍リズムには、前後に付属するシラブルが増減してもストレスを持ったシラブルの間隔は必ず等しいという規則があります。このことを等時性と呼びます。特にここでは、前で説明したシラブル拍の等時性と区別し **ストレス拍リズム等時性** と呼びます。 これを認識するリズム認識型が **ストレス拍リズム等時性リズム認識型** です。

### オフビートカウントで英語リスニング能力向上のは何故か

オフビートカウントを練習すると英語のリスニング能力が向上します。これはオフビートカウントを行うと、英語を聴き取る事に必要なリズム認識型を習得することの助けになっているからだと考えられます。オフビートカウントは、これまでがむしゃらに練習する以外に何の指針もなかった英語等々の発音聴き取り練習に、一定の指針を与えてくれます。

#### オフビートカウントと音韻学の一致

オフビートカウントは、我々が音楽活動をする上でぶつかる様々なリズム上の問題を合理的に説明してくれる非常に良いツールです。 オフビートカウントは、グルーヴという得体の知れない音楽的現象を感覚的に理解する大きな手がかりを与えてくれるでしょう。

まず、どんなにオフビートカウントで悪戦苦闘している人でも、カウントに必要な全ての発音を順番にひとつひとつ練習し、頭子音・末子音のリンキングに注目して特に**侵襲的末子音(Intrusive Consonant)** を含めて丁寧にリンキングを練習すると、即座にオフビートカウントが出来るようになります。 これは音韻学的に見ると、シラブル拍の発音練習に当たります。  ─── これが１つ目の弱拍先行です。ここでは**シラブル拍弱拍先行** と呼びます。

そして同時にオフビートカウントは、音韻学的に言語発音上のストレス拍リズムを数字上で体現したものになっています。単層オフビートカウントの上で、多層弱拍先行オフビートカウントを練習することで、グルーヴ能力を身につけることができます。多層弱拍先行は音韻学的に見ると、ストレス拍の発音練習に相当しています。

#### ２つの等時性(Isochrony) をオフビートカウントによって鍛錬する

**ストレス拍リズム等時性リズム認識** と**シラブル拍リズム等時性リズム認識**を同時の２つの等時性は、しばしば**同時に持っていることが求められ**ます。英語の方言を聴き取る為には、この２つの等時性を同時に持っていることが求められますし、またジャズなどのアメリカ伝統音楽を演奏する為にもこの２つの等時性を同時に持っている事が求められます。

漠然とリスニング練習や耳コピ練習を行ってもこれらのリズム認識型を習得する事は、とても困難です。しかしオフビートカウントを理論的に分析すると、この２つのリズム認識型を同時に働かせる作用があることがわかります。 オフビートカウントを行う作業の行程には、この２つの等時性リズム認識型にはっきりと意識を向ける必要が生じる為、オフビートカウントがこの２つを身につける為の練習法としての応用できることが期待されます。

オフビートカウントは、その他のシラブル拍言語 ─── フランス語やスペイン語のリスニング能力が向上することが期待されます。 オフビートカウントには **頭子音最大化原則(MOP=Maximize Onset Principle)**  に意識を向ける作用があるからです。 

同時に英語のリスニング練習の効果を持っていることも期待されます。それは **頭音節最大化原則(MPOP=Maximal Prosodic Onset Principle)** を働かせる作用があると考えられるからです。 

## モーラ拍リズム言語話者の為のエチュード

この章では、岡敦が経験的に効果があることに気付いた音韻学に基づいた訓練方法を説明致します。

### モーラ拍リズムから見たストレス拍リズム

次のビデオは２０１０年ごろに米国ヒップホップシーンで流行したヒット曲 Swag Surfin' です。この曲はアフリカ系アメリカ人発音≒米国南部方言を色濃く反映した音楽です。 この曲をモーラ拍リズム言語話者が聴くと、全ての音節をひとつずれた形で認識してしまい正しい英語の発音として聴き取れないという現象がおこります。

この曲ではシラブル拍の{{< var MOP >}}、及びストレス拍リズムの{{< var MPOP >}}によって、全ての単語のリズム配置が弱拍が先になるように配置されています。 しかし{{< var MiOP>}}をもつモーラ拍言語話者は、この弱拍先行が理解できずに強拍先行として認識する為、全ての音節を半分ずれて解釈してしまうという現象が起こります。


<iframe class="rhythmpedia-iframe" src="https://www.youtube.com/embed/7iTsbnr8e_8?si=uR5wPuBM63tA8ldU" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<iframe class="rhythmpedia-iframe" src="https://www.youtube.com/embed/gM8TdGIf8Uk?si=Shy9bTB_4kvCkjyz" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### ストレス拍リズム発音のモーラ拍リズムでの解釈

この音楽の歌詞の最初の部分をモーラ拍リズムで解釈すると『メナガテｯｽウェーッグ』と言っている様に聴こえます。これはストレス拍リズムでは『 man, I got that swag 』と解釈されます。この解釈の違いを図として表すと次の様になります。

![](/offbeat-count-phonetics/attachments/man-i-got-that-swag.png)

ここで起こっている相違の対応表を作ると次の様になります。

<style>

  /* 1) Let tables scroll horizontally instead of breaking layout */
  .quarto-container table.table {
    display: block;          /* enables overflow on the element itself */
    max-width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-gutter: stable both-edges;
  }

  table.pron {
    width:100%;
    height:auto;
  }
  .pron :is( th, td ) {
    font-size: 0.8em;
    min-height:40px;
    margin : 10px;
    padding : 1px;
    text-align : center; 
    vertical-align: center;
    white-space:nowrap;
  }

  body.quarto-light table.pron {
    background-color : auto;
  }
  body.quarto-dark table.pron {
    background-color : auto;
  }
  body.quarto-light .pron :is( th, td ) {
    border: solid 1px black;
    background-color:auto;
  }
  body.quarto-dark .pron :is( th, td ) {
    border: solid 1px lightgreen;
    background-color:auto;
  }
  body.quarto-light .pron th  {
    background-color: yellow;
  }
  body.quarto-dark  .pron th  {
    background-color: #330;
  }

  .header-center th {
    text-align : center !important;
  }
  .pron2 col {
    width: auto !important;
  }
  .pron2 :is( th, td ) {
    font-size: 0.8em;
    min-height:40px;
    margin : 10px;
    padding : 1px;
    vertical-align: center;
    white-space:nowrap;
  }
  body.quarto-light .pron2 :is( th, td ) {
    border: solid 1px black;
    background-color:auto;
  }
  body.quarto-dark .pron2 :is( th, td ) {
    border: solid 1px lightgreen;
    background-color:auto;
  }

/*
  table.pron3 { 
    table-layout: fixed; /* prevents auto expansion */
  }
*/
  .pron3 :is( th, td ) {
    font-size: 0.8em;
    min-height:40px;
    margin : 10px;
    padding : 1px;
    vertical-align: center;
    white-space:nowrap;
  }
  table.pron3 thead :is( td, th ) {
  }
  table.pron3 tbody :is( td ) {
  }

</style>
<table class="pron">
    <tbody>
      <tr>
        <th colspan="1">英語の音節解釈</th>
        <td colspan="3">音節</td>
        <td colspan="3">音節</td>
        <td colspan="3">音節</td>
        <td colspan="3">音節</td>
      </tr>
      <tr>
        <th colspan="1">英語の発音</th>
    
        <td colspan="1">子音</td>
        <td colspan="1">母音</td>
        <td colspan="1">子音</td>
    
        <td colspan="1">子音</td>
        <td colspan="1">母音</td>
        <td colspan="1">子音</td>
    
        <td colspan="1">子音</td>
        <td colspan="1">母音</td>
        <td colspan="1">子音</td>
    
        <td colspan="1">子音</td>
        <td colspan="1">母音</td>
        <td colspan="1">子音</td>
      </tr>
      <tr>
        <th colspan="1">日本語の発音解釈</th>
        <td colspan="1">子音</td>
        <td colspan="1">母音</td>
        <td colspan="2">子音</td>
        <td colspan="1">母音</td>
        <td colspan="2">子音</td>
        <td colspan="1">母音</td>
        <td colspan="2">子音</td>
        <td colspan="1">母音</td>
        <td colspan="1">-</td>
      </tr>
        <tr>
        <th>日本語で解釈された音節</th>
        <td colspan="2">音節</td>
        <td colspan="3">音節</td>
        <td colspan="3">音節</td>
        <td colspan="3">音節</td>
        <td colspan="1">-</td>
      </tr>
    </tbody>
</table>

この様にモーラ拍リズムに末子音がないことにより、次の音節の頭子音との混同が起こり、ストレス拍リズムから見ると、モーラ拍リズムの解釈は１音節当たり 1/3 ずれた形で音声を認識していることがわかります。

### 末子音のないモーラ拍の末子音矯正法

モーラ拍リズム言語話者がストレス拍リズム言語を聴き取るために必要なことは、末子音を適切に区別してこの 1/3 のずれが起こらない様に矯正することです。つまり各シラブルの末子音を分離する練習をすることが有効だと考えられます。 それは日本語のそれぞれのモーラ拍の発音上を３つに分割し、モーラ拍の中に潜む末子音の存在をはっきり意識して次の音節の頭子音と結びついていることを意識する練習です。

例）七夕花火にカンパーイ『タナバタ・ハナビニ・カンパーイ』  

　　↓↓↓

- ターン
- ナーブ
- バート
- ターハ
- ナーブ
- イーン
- イーク
- アーン
- パーイ

ここで起こったていることを具体的に説明すると次のようになります。タナバタをローマ字で表すと TA NA BA TA になります。ここで各文字の母音とその次の文字の子音を繋げると TAN/NAB/BAT/TAH になります。つまり「ターン」「ナーブ」「バート」「ター」です。 この様にして各モーラ拍を３分割し末子音を分離していく作業を行います。このようにすることでストレス拍/シラブル拍リズムに必要な末子音認識に対して慣れる訓練を行います。

次のモーラの頭子音をスムーズに発音する為に、当該モーラの後端部分に暗黙の末子音が表れます。この無意識化で作っている暗黙の末子音をはっきり意識することが重要なポイントです。英語では次に現れる頭子音によって末子音が変化することはありません。しかし日本語では意識していない為に変化します。この違いに慣れることが重要といえます。

なお上記例では「ターハ」になっている最後の文字が「ター」になってしまいましたが、これは上記例のタナバタの次はハナビとハから始まっているのに、タナバタのみの場合は後続の文字がないためターのみになってしまったことによるものです。

別の例を見てみます。  

例）かささぎの わたせる橋におく霜の 白きを見れば夜ぞふけにける  

『カササギノ・ワタセルハシニ・オクシモノ・シロキヲミレバ・ヨルゾフケニケル』  

　↓↓↓  

- カース
- サース
- サーグ
- ギーン
- ノーウ
- ワーッﾄ
- タース
- セール
- ルーフ
- ハース
- シーン
- イーオ
- オーク
- クース
- シーム

## 英語の発音の基礎

日本の英語教育で教わる英語の発音の知識は、明らかに不足しています。 ここでは不足している知識に絞って重点的に説明致します。

英語には標準語がありません。ロシア語・フランス語・ドイツ語は、政府機関が国の標準語を定めています。しかし英語にはこの様な公式な標準語制定機関が存在しません。その代わりに、いくつかの「標準英語の提案」を行っている有力な機関がありますが、強制力までは持っていません。

つまり英語は、沢山の方言があります。つまり、英語の正しい発音を学べば学ぶほど、英語は聴き取れなくなっていきます ─── これは初学者にとって、最初にぶつかる最大の関門です。


これに対処するためには「英語を学び始めた最初から訛りに対する知識を身につける」しかありません。こういうととても難しいことのように思えますが、実は英語の訛りの規則は、とてもよく研究されており、コンパクトにまとまっています。

ジャズのリズムと米国南部方言には強い関連性があります。そしてAAVEと呼ばれる『黒人英語』は、ジャズのリズムとは切っても切り離せない深い関連性があります。ジャズを学ぶためには英語の発音を学ぶ事が大切ですが、特にこの米国南部方言と黒人英語の２つの英語の方言を学ぶことはとても重要です。

ここでは標準的な英語と数多く存在する英語の方言の理解に必要な発音を順に学んでいきます。

### 凡例

#### 音韻規則を表す用語

音韻学で使われる発音規則を書き表す表記法に SPE表記法(SPE notation) というものがあります。

SPE表記法は音韻学の研究が立ち遅れている我が国日本では全く使われていません。[^spe3]

そこでここではSPE表記法を避け、漢語の訳語を当てて表現します。

| SPE表記法       | 日本語の呼び方          | 英語の呼び方                     | 説明                                          |
|-----------------|-------------------------|----------------------------------|-----------------------------------------------|
| `_`             | 規則適用位置            | **Site of Application**          | 規則が適用される位置（X _ Y）※１             |
| `#`             | 語界                    | **Word Boundary**                | 単語と単語の境界を表す                        |
| `C`             | 任意の子音              | **Consonant**                    | 包括記号( **Cover Symbols** ) のひとつ ※2    |
| `V`             | 任意の母音              | **Vowel**                        | 包括記号( **Cover Symbols** ) のひとつ ※2    |
| `{ … }`        | 特定のセグメントの集合  | **Set of Specific Segments**     | ※ 例：{t, d, n} の **segments**              |
| `[ … ]`        | 特徴束                  | **Feature Bundle**               | 例：`[+syllabic]`、`[-voice]`                 |
| `( … )`        | 省略可能                | **Optional**                     | 任意要素の括弧                                |
| `+`             | 形態素境界              | **Morpheme Boundary**            | 語内部                                        |
| `##`            | 発話境界                | **Utterance Boundary**           | 発話全体の端                                  |
| `V́`             | 強勢母音                | **Stressed  Vowel**              |                                               |
| `V̆`             | 無強勢母音              | **Unstressed Vowel**             |                                               |
| `N̩`             | 音節的子音              | **Syllabic Consonant**           |                                               |
| `O`             | 音節頭                  | **Onset**                        | `σ` **sigma**(後述)の構成要素のひとつ。      |
| `N`             | 音節核                  | **Nucleus**                      | `σ` **sigma**(後述)の構成要素のひとつ。      |
| `Co`            | 音節末                  | **Coda**                         | `σ` **sigma**(後述)の構成要素のひとつ。      |
| `σ` **sigma**  | 音節                    | **Syllable**                     |                                               |
| `ω` **omega**  | 韻律語                  | **Prosodic Word**                |                                               |
| `φ` **phi**    | 音韻句                  | **Phonological Phrase**          |                                               |
| `ι` **iota**   | イントネーション句      | **Intonational Phrase**          |                                               |
| `μ` **mu**     | モーラ                  | **Mora**                         | 日本語発音分析で必須                          |
| `∅`             | 空列（ゼロ音）          | **Null** / **Zero**              | 挿入・脱落規則に使う（例：`∅ → t / V _ V`）  |
| `α`（変数）    | アルファ変数            | **Alpha Notation**               | 同値特徴（例：C → [αvoice] / _ [αvoice]）  |
| `.`             | 音節境界                | **Syllable Boundary**            | 転写や環境に用いることがある                  |
| `R` / `ρ`      | ライム(核＋末)          | **Rime**                         | `R = N + Coda`                                |
| `Ft`            | フット                  | **Foot**                         | `σ`の上位単位                                |
| `U`             | 発話                    | **Utterance**                    | `ι`の上位；`##`の実体                        |

:  {.pron2}

- 🗣️ 1 `A → B / X _ Y` は「X と Y のあいだ（**between**）で A が B に変わる（**becomes**）」と読む。
- ※1 挿入・脱落にも用いる。
- ※2 CとVは、CV用語の**タイミング・スロット (timing slots)**とは異なる概念。混同に注意。

[^spe3]: Some specialist generative-phonology works do use SPE-style rules, but this guide targets general readers.



#### 発音変化の位置に関する用語

##### 単語 - Word level (ω / `#`)

* **語頭** = **word-initial** → `# _` or `ω[ _`
* **語末** = **word-final** → `_ #` or `_ ]ω`
* **語中** = **word-medial (non-edge)** → no `#` on either side

##### 音節 - Syllable level (σ)

* **音節頭** = **syllable onset** → `σ[ _` or `O _`
* **音節末** = **syllable coda** → `_ ]σ` or `_ Co`

##### 要素間 - Segmental neighbors

* **母音間** = **intervocalic** → `V _ V`
* **子音間** = **interconsonantal** → `C _ C`
* **母音前** = **before a vowel** → `_ V`
* **子音前** = **before a consonant** → `_ C`
* **母音後** = **after a vowel** → `V _`
* **子音後** = **after a consonant** → `C _`

##### 形態素間 - Morphology & larger prosody

* **語素界** = **morpheme boundary** → `+`
* **話語界** = **utterance boundary** → `##`
* **短語頭** = **phonological-phrase initial** → `φ[ _`
* **短語末** = **phonological-phrase final** → `_ ]φ`
* **語調短語頭** = **intonational-phrase initial** → `ι[ _`
* **語調短語末** = **intonational-phrase final** → `_ ]ι`

##### ストレス拍とシラブル拍 Stress & syllabicity

* **重音後・非重音前** = **after stressed, before unstressed** → `V́ _ V̆`
  (classic flapping environment)
* **成音節子音前** = **before a syllabic consonant** → `_ N̩`

##### 集合と類 - Sets & classes

* **音集** = **set of segments** → `{…}` (e.g., `{t,d,n,s,z,l}`)
* **子音 / 母音** = **consonant / vowel** → `C / V` (natural class shorthands)

#### Quick crosswalk

* **“Word-initial”** → **語頭** (`# _` / `ω[ _`)
* **“Word-final”** → **語末** (`_ #` / `_ ]ω`)
* **“Syllable onset”** → **音節頭** (`σ[ _` / `O _`)
* **“Syllable coda”** → **音節末** (`_ ]σ` / `_ Co`)
* **“Between vowels”** → **母音間** (`V _ V`)
* **“Before a consonant”** → **子音前** (`_ C`)
* **“After a vowel”** → **母音後** (`V _`)
* **“Across V#V”** (e.g., linking) → **語末 + 語頭** across words (`_ # V`)
* **“After alveolars {t,d,n,s,z,l}”** → **音集後** (`{t,d,n,s,z,l} _`)
* **“After stressed, before unstressed”** → **重音後・非重音前** (`V́ _ V̆`)
* **“Before syllabic N”** → **成音節子音前** (`_ N̩`)
* **“At a morpheme boundary”** → **語素界** (`+`)
* **“At phrase edge”** → **短語頭 / 短語末** (`φ[ _` / `_ ]φ`)
* **“At intonational-phrase edge”** → **語調短語頭 / 語調短語末** (`ι[ _` / `_ ]ι`)


* 🗣️ When you want **syllable-initial** in prosodic notation, write **`σ[ _`** (not `[σ _`).
* 🗣️ **C/V here are class shorthands**, not CV-skeleton timing slots. If you switch to true CV-skeleton talk, use **O/N/Co** or **C/V-slots** explicitly.
* 🗣️ For **linking/intrusive r** in non-rhotic accents, the context is **V # V** (i.e., **語末 + 語頭** with vowels on both sides).
* 🗣️ Use **`_ ]σ`** (or `_ Co`) for “in coda,” and **`σ[ _`** (or `O _`) for “in onset.”

#### 方言の略称

|    英語     |  日本語  | 日本語名                    | 英語名                              | 解説                                   |
| :---------: | :------: | --------------------------- | ----------------------------------- | -------------------------------------- |
|   **GA**    |  **米**  | アメリカ英語                | General American                    |                                        |
|   **GA**    | **米南** | アメリカ南部方言            | South American                      |                                        |
|  **AAVE**   | **ア米** | アフリカ系米国英語/黒人英語 | African American Vernacular English |                                        |
|   **RP**    |  **英**  | 容認発音英語                | Received Pronunciation              | イギリス英語の伝統的な事実上の標準発音 |
|   **MLE**   | **多英** | 多文化ロンドン英語          | Multicultural London English        |                                        |
| **Cockney** |  **コ**  | コックニー英語              | Cockney                             | 東ロンドンの労働者階級英語             |
| **Estuary** |  **エ**  | 河口域英語/エスチュアリ英語 | Estuary English                     | イギリス西南部テムズ川流域の英語       |

:  {.pron2 .header-center tbl-colwidths=[1,1,1,1,1]}

Here’s a **dialect–change cross-table**: rows are phonological/phonetic changes, columns are dialects (GA, MLE, AAVE, Cockney, Estuary, Southern AmE). I marked **●** where the change is attested/characteristic, and left blank otherwise. Notes are condensed so it fits as a quick comparative overview.

---

#### 方言別 子音変化マトリクス

| 発音変化名                 | 発音変化           |      米       |    米南    |    ア米    |   コ    |  エ   | 多英  |
| :------------------------- | :----------------- | :-----------: | :--------: | :--------: | :-----: | :---: | :---: |
| TH-fronting                | `/θ/->[f]`        |               | (語末一部) | (語末一部) |   ●    |       |  ●   |
| TH-stopping                | `/ð/->[d]`        |               |            |  ●(初頭)  |         |       |       |
| TH-frontingvoiced          | `/ð/->[v]`        |               |            |            |   ●    |       |  ●   |
| T-glottalization           | `/t/->[ʔ]`         | (語末/限局的) |            |   (語末)   |   ●    |  ●   |       |
| Flapping                   | `/t,d/->[ɾ]`       |      ●       |     ●     |     ●     |         |       |       |
| -ing->-in’                | `/ŋ/->[n]`        |               |     ●     |     ●     |   ●    |       |       |
| L-vocalization             | `/l/->[w,o]`       |               |            |            |   ●    |  ●   |       |
| h-dropping                 | `/h/->∅`           |               |            |            |   ●    |       |       |
| Yod-coalescence            | `/tj,dj/->[tʃ,dʒ]` |               |            |            |   ●    |       |  ●   |
| Yod-dropping               | `/juː/->[uː]`    |      ●       |     ●     |   (一部)   |         |       |       |
| wh–wcontrast              | `/hw/->[ʍ]`        |               |  ●(保存)  |   (一部)   |         |       |       |
| Finalclustersimplification |                    |      ●       |     ●     |            |         |       |       |
| t-deletion                 | /nt/->[n]          |   ●(口語)    |            |     ●     |         |       |       |
| Linkingr                   | `∅->[ɹ]`           |               |            |            | ●(非r) |  ●   |       |
| Intrusiver                 |                    |               |            |            |   ●    |  ●   |       |
| Non-rhoticity              | `/ɹ/->∅`           |               |            |            |   ●    |  ●   |       |
| Retroflex/bunchedr         |                    |      ●       |     ●     |     ●     |         |       |       |
| Dentalization              | `t,d,n->[t̪,d̪,n̪]`   |      ●       |            |            |   ●    |  ●   |  ●   |

:  {.pron2 .pron3 .header-center }

* **●** = strong/characteristic
* ( ) = limited / environment-restricted presence

hello world foo bar ^[あああああ] 

aaa [^spe22]

[^spe22]: いいいいいいいいいいい


### 母音

#### 単母音

|   IPA    |    実例     |    舌の位置    | 説明                                                               |
| :------: | :---------: | :------------: | :----------------------------------------------------------------- |
| **/i/**  |  (_beat_)   |     高・前     | 日本語「イー」より前で緊張、口は横に。                             |
| **/ɪ/**  |   (_bit_)   |     高・前     | 「イ」だが力を抜く。「イ」と「エ」の間、短い。                     |
| **/ɛ/**  |   (_bet_)   |     中・前     | 日本語「エ」より低く開く、横に広げる。                             |
| **/æ/** |   (_bat_)   |     低・前     | 大きく開く。「アとエの間」。日本語に無い。                         |
| **/ɑ/** | (_father_)  |     低・後     | 唇広め、喉奥で「ア」。                                             |
| **/ɔ/**  | (_thought_) |     中・後     | 軽く丸めた「オー」。※多くの米語で /ɑ/ と合流。                   |
| **/ʊ/**  |  (_book_)   |     高・後     | 力を抜く。「ウとオの間」、軽く丸める。                             |
| **/u/**  |  (_boot_)   |     高・後     | 緊張。「ウー」より強く丸め後方。                                   |
| **/ʌ/**  |  (_strut_)  | 中央・短く平ら | 「アとオの間」。日本語に無い。                                     |
| **/ə/**  |  (_sofa_)   |                | 弱勢の中央母音＝『**シュワ**』と呼ばれる。短く弱い曖昧な母音。     |
| **/ɝ/**  |  (_bird_)   |                | **強勢**の r 化母音。舌を後方やや反り気味に /r/ 的発音に変化。     |
| **/ɚ/**  | (_butter_)  |                | **弱勢**の r 化母音。日本語「ア」と全く違う。flap と連動しやすい。 |

:  {.pron2}

#### 二重母音（滑り音）

|   IPA    |    実例    |   動き   | 説明                                   |
| :------: | :--------: | :------: | -------------------------------------- |
| **/eɪ/** |  (_bait_)  | /e/→/ɪ/ | 短く滑る。日本語「エイ」より後半短い。 |
| **/oʊ/** |  (_goat_)  | /o/→/ʊ/ | 日本語「オウ」より後半短く、丸め維持。 |
| **/aɪ/** | (_price_)  | /a/→/ɪ/ | 開始を低く大きく開く。                 |
| **/aʊ/** | (_mouth_)  | /a/→/ʊ/ | 後半で丸める。                         |
| **/ɔɪ/** | (_choice_) | /ɔ/→/ɪ/ | 開始は丸め気味の「オ」。               |
: {.pron2}

#### r 付き（r-colored）複合

|    IPA    |    実例    |        動き         | 説明                                                              |
| :-------: | :--------: | :-----------------: | :---------------------------------------------------------------- |
| **/ɪɚ/**  |  (_near_)  | **/ɪ/** → **/ɚ/**  | **母音＋\[ɚ]**の一まとまり。**終端でr化**（舌端は**触れない**）。 |
| **/ɛɚ/**  | (_square_) | **/ɛ/** → **/ɚ/**  | 開始母音の**質を保ち**、**末尾でr色**。                           |
| **/ʊɚ/**  |  (_cure_)  | **/ʊ/** → **/ɚ/**  | **短いウ**から**r化**へ。語により **/kjʊr/** など変異。           |
| **/ɔɚ/**  | (_north_)  | **/ɔ/** → **/ɚ/**  | **丸めたオ**始まり→**r化**。方言差大。                           |
| **/ɑɚ/** | (_start_)  | **/ɑ/** → **/ɚ/** | **広いア**始まり→**r化**。                                       |

:  {.pron2}

### 子音

#### 破裂音 (Plosives)

|   IPA    |      Examples        | 分類                 | 説明                                       | 地方                                                                              |
| :------: | :-----------------:  | :------------------- | :----------------------------------------- | :-------------------------------------------------------------------------------- |
| **/p/**  |     _pin, cap_       | **無声両唇破裂音**   | 両唇を閉じて破裂；語頭は**強い息（帯気）** | 全般                                                                              |
| **/b/**  |     _bin, cab_       | **有声両唇破裂音**   | /p/ と同動作だが**声帯振動**               | 全般                                                                              |
| **/t/**  |     _two, cat_       | **無声歯茎破裂音**   | 語頭は帯気；**/s/** の後は無帯気（_spin_） | 全般                                                                              |
| **/d/**  |      _do, ad_        | **有声歯茎破裂音**   | /t/ の有声版                               | 全般                                                                              |
| **/k/**  |     _key, back_      | **無声軟口蓋破裂音** | 語頭は帯気；/s/ の後は無帯気（_ski_）      | 全般                                                                              |
| **/g/**  |      _go, bag_       | **有声軟口蓋破裂音** | /k/ の有声版                               | 全般                                                                              |
| **\[ʔ]** | _bo\[ʔ]le ≈ bottle_ | **無声音声門破裂音** | **T-glottalization**：/t/ が \[ʔ] に置換   | Cockney, Estuary, MLE, 米国 では<br/> /t/ が子音前・音節末で可変<br/>AAVE/GA 一部 |

: {.pron2}

#### 破擦音 (Affricates)

|        IPA         |     Examples       | 分類                 | 説明                                  | 地方                 |
| :----------------: | :---------------:  | :------------------- | :-----------------------------------  | :------------------- |
|      **/tʃ/**      |   _chin, match_    | **無声後部歯茎破擦** | 「**ch**」＝**/t/ + /ʃ/** の一体化。  | 全般                 |
|      **/dʒ/**      |   _jam, badge_     | **有声後部歯茎破擦** | 「**j**」＝**/d/ + /ʒ/** の一体化。   | 全般                 |
| **\[t͡ʃ] (< /tj/)** | _tune → \[t͡ʃ]une_ | **派生破擦**         | **Yod-coalescence**（/tj/→\[t͡ʃ]）    | **英 (特にCockney)** |
| **\[d͡ʒ] (< /dj/)** | _duty → \[d͡ʒ]uty_ | **派生破擦**         | **/dj/→\[d͡ʒ]**                       | **英 (特にCockney)** |

#### 歯摩擦音 (Fricatives)

|   IPA    |  Examples   | 分類                   | 説明                               | 地方                                |
| :-----:  | :---------: | :--------------------- | :--------------------------------- | :---------------------------------- |
| **/f/**  |  (_fine_)   | **無声唇歯摩擦**       | 上歯を下唇に軽く当てる。           | 全般                                |
| **/v/**  |  (_vine_)   | **有声唇歯摩擦**       | /f/ に**声帯振動**を加える。       | 全般                                |
| **/θ/** |  (_thin_)   | **無声（舌端）歯摩擦** | 日本語に無い。                     | 全般（※方言交替は下表）             |
| **/ð/** |  (_this_)   | **有声（舌端）歯摩擦** | /θ/ と同形で**声帯振動**。        | 全般（※方言交替は下表）             |
| **/s/**  |   (_see_)   | **無声歯茎摩擦**       | 唇は**平ら**。                     | 全般                                |
| **/z/**  |   (_zoo_)   | **有声歯茎摩擦**       | /s/ の有声版。                     | 全般                                |
| **/ʃ/**  |   (_she_)   | **無声後部歯茎摩擦**   | 舌をやや後ろ，**唇を軽く丸める**。 | 全般                                |
| **/ʒ/**  | (_measure_) | **有声後部歯茎摩擦**   | 外来語中心；語頭は稀。             | 全般                                |
| **/h/**  |   (_hat_)   | **無声声門摩擦**       | **次の母音の口形**で息だけ通す。   | 全般（※Cockney等で**h脱落**が頻発） |

: {.pron2}

#### 鼻音 (Nasals)

|   IPA   | Examples | 分類           | 説明                                       | 地方                                                                    |
| :-----: | :------: | :------------- | :----------------------------------------- | :---------------------------------------------------------------------- |
| **/m/** |  (_me_)  | **両唇鼻音**   | 口を閉じて**鼻へ**共鳴。                   | 全般                                                                    |
| **/n/** |  (_no_)  | **歯茎鼻音**   | 舌先を歯茎に当てる。                       | 全般                                                                    |
| **/ŋ/**| (_sing_) | **軟口蓋鼻音** | 上顎に舌の奥を当てる。<br>先頭に表れない。 | 全般<br>※AAVE/南部/Cockney で<br>-ing → in’ の様に\[ŋ]→\[n] に変化 |

: {.pron2}

#### 接近音 (Approximants)

|   IPA    |      Examples       | 分類                       | 説明                                                            | 地方                                                       |
| :------: | :-----------------: | :------------------------- | :-------------------------------------------------------------- | :--------------------------------------------------------- |
| **/ɹ/**  |       (_run_)       | **歯茎接近音**             | **舌先は触れない**（日本語ら行\[ɾ]と別）。                      | 全般<br>**Cockney は語末・子音前で非R**                    |
| **/j/**  |       (_yes_)       | **硬口蓋近接**             | 「**y**」音；舌前部を上げる。                                   | 全般<br>英の一部で<br>/tj,dj/ と合流→Yod合流              |
| **/w/**  |       (_we_)        | **両唇・軟口蓋近接**       | **丸唇＋後舌**の協調。                                          | 全般                                                       |
| **\[ʍ]** | (_which_ ≠ _witch_)| **無声両唇‐軟口蓋近接**   | **/hw/** 由来の「息混じりの w」。<br>**whine–wine**対立を保持。| 米南部の一部<br>スコットランド<br>アイルランド<br>一部AAVE |
| **\[ɻ]** |          —         | **後舌巻き舌的 ɹ**（異音） | **retroflex/bunched r**。                                       | 北米英<br>GA<br>AAVE など                                  |

: {.pron2}

#### 側面接近音 (Lateral)

|                IPA                |        Examples        | 分類              | 説明                                                               | 地方                 |
| :---------------------------------: | :----------------------: | :----------------- | :------------------------------------------------------------------ | :-------------------- |
|              **/l/**              |    (*light, fill*)     | **側面接近音**    | 語末・子音前は **暗い L \[ɫ]**<br>（舌後部を上げる）になりやすい。 | 全般                 |
|             **\[ɫ]**              |           —           | **暗いL（異音）** | とくに語末/子音前で顕著。                                          | **英米全般**         |
| **L-vocalization \[w \~ ʊ̯ \~ o]** | (*people → peop\[ʊ̯]*) | **交替**          | /l/ が後舌化・半母音化し<br>**母音/半母音に近づく**。              | **Cockney, Estuary** |
: {.pron2}

### 使い分けの要点（最小セット）

- **Cockney 系**：**\[ʔ]**（T-グロッタル化）、**TH-fronting**（/θ, ð/ → \[f, v]）、**h-dropping**、**L-vocalization**、**Yod-coalescence**、**非R（linking/intrusive r）**。
- **Southern American English（米南部）**：**\[ʍ]**（whine–wine対立の保持）、語末 **-in’**、クラスター簡略化（子音脱落）など。
- **AAVE**：語末 **-in’**、**TH-stopping/fronting**の分布、クラスター簡略化、**flap \[ɾ]**は北米一般同様に出現（/t,d/間）。基本は**R音声（rhotic）**。



### 方言別子音入れ替わりまとめ

- THの唇歯化 (TH-fronting)
  - Exchange (Input → Output)
    - /θ/ → **\[f]**
  - Typical Environment
    - Coda > elsewhere
  - Examples
    - *three → free*, *mouth → mouf*
  - 地方 (Dialects)
    - **Cockney, MLE**；（語末のみ）**AAVE/米南部/カリブ系都市**
  - Notes
    - Cockneyは広範、他方言は語末中心
- 有声THの破裂化 (TH-stopping (voiced))
  - Exchange (Input → Output)
    - /ð/ → **\[d]**
  - Typical Environment
    - Word-initial
  - Examples
    - *this → dis*, *them → dem*
  - 地方 (Dialects)
    - **AAVE**、**Irish/Caribbean英**、都市変種
  - Notes
    - 語中・語末では \[d]/\[v] 可変
- 有声THの唇歯化 (TH-fronting (voiced))
  - Exchange (Input → Output)
    - /ð/ → **\[v]**
  - Typical Environment
    - Medial/Final
  - Examples
    - *brother → bruvva*
  - 地方 (Dialects)
    - **Cockney, MLE**
  - Notes
    - Cockneyで顕著
- Tの声門化（グロッタル化） (T-glottalization)
  - Exchange (Input → Output)
    - /t/ → **\[ʔ]**
  - Typical Environment
    - Coda / 子音前 / 弱勢音節
  - Examples
    - *bottle → boʔ(ɫ)*, *kitten → kɪʔn̩*
  - 地方 (Dialects)
    - **Cockney, Estuary**；（限定的に）**GA/AAVE**
  - Notes
    - 英で強勢、米は語末・子音前可変
- T/Dのフラッピング (Flapping)
  - Exchange (Input → Output)
    - /t, d/ → **\[ɾ]**
  - Typical Environment
    - Vowel\_V́ \_\_ V̆
  - Examples
    - *water → waɾer*, *city → sɪɾi*
  - 地方 (Dialects)
    - **GA 全般**, **AAVE**
  - Notes
    - 強勢母音後＋弱勢母音前
- -ing弱化 (g-dropping)
  - Exchange (Input → Output)
    - /ŋ/ → **\[n]**
  - Typical Environment
    - -ing coda
  - Examples
    - *walking → walkin’*
  - 地方 (Dialects)
    - **AAVE**、**米南部**、**Cockney**（口語）
  - Notes
    - スタイル依存で広範
- Lの母音化 (L-vocalization)
  - Exchange (Input → Output)
    - /l/ → **\[w \~ ʊ̯ \~ o]**
  - Typical Environment
    - Coda
  - Examples
    - *ball → baw*, *people → peopʊ̯*
  - 地方 (Dialects)
    - **Cockney, Estuary**
  - Notes
    - ロンドン周辺で顕著
- h脱落 (h-dropping)
  - Exchange (Input → Output)
    - /h/ → **∅**
  - Typical Environment
    - Word-initial
  - Examples
    - *house → ’ouse*, *have → ’ave*
  - 地方 (Dialects)
    - **Cockney**、都市英の一部
  - Notes
    - 機能語で頻度↑
- ヨッド合流 (Yod-coalescence)
  - Exchange (Input → Output)
    - /tj, dj/ → **\[t͡ʃ, d͡ʒ]**
  - Typical Environment
    - t/d + /j/
  - Examples
    - *tune → choon*, *duty → jooty*
  - 地方 (Dialects)
    - **Cockney、都市英（MLE等）**
  - Notes
    - 連続音化（破擦化）
- ヨッド脱落 (Yod-dropping)
  - Exchange (Input → Output)
    - /juː/ → **\[uː]**
  - Typical Environment
    - After alveolars (t, d, n, s, z, l)
  - Examples
    - *tune → toon*, *news → nooz*
  - 地方 (Dialects)
    - **GA**、**米南部**、一部 **AAVE**
  - Notes
    - 北米で一般的
- /hw/と/w/の対立保持 (wh–w contrast maintained)
  - Exchange (Input → Output)
    - /hw/ → **\[ʍ]** (≠ /w/)
  - Typical Environment
    - Word-initial
  - Examples
    - *which \[ʍɪtʃ]* vs *witch \[wɪtʃ]*
  - 地方 (Dialects)
    - **米南部の一部**、**Scots**、**Irish**，一部 **AAVE**
  - Notes
    - “息混じりの w”
- 語末子音群の単純化 (Final cluster simplification)
  - Exchange (Input → Output)
    - Coda clusters → simplified
  - Typical Environment
    - Word-final（次語子音で強化）
  - Examples
    - *hand → han*, *cold → col’*
  - 地方 (Dialects)
    - **AAVE**、**米南部**（口語）
  - Notes
    - 有声阻害音で顕著
- /t/ 省略（NTクラスタ） (t-deletion (NT cluster))
  - Exchange (Input → Output)
    - /nt/ → **\[n]**（しばしば鼻母音化/延長）
  - Typical Environment
    - Intervocalic / 早口
  - Examples
    - *internet → innernet*
  - 地方 (Dialects)
    - **GA**、**AAVE**（口語）
  - Notes
    - flap共存も
- リンキングr (Linking r)
  - Exchange (Input → Output)
    - ∅ → **\[ɹ]**
  - Typical Environment
    - Vowel#Vowel
  - Examples
    - *law(r) and*, *idea(r) of*
  - 地方 (Dialects)
    - **非r方言**：**Cockney/Estuary/RP系**
  - Notes
    - 語彙的 r 連結
- イントルーシブr (Intrusive r)
  - Exchange (Input → Output)
    - ∅ → **\[ɹ]**
  - Typical Environment
    - Vowel#Vowel（無語源 r）
  - Examples
    - *saw(r) it*
  - 地方 (Dialects)
    - **非r方言**：**Cockney/Estuary/RP系**
  - Notes
    - 語源に r 無しでも挿入
- 非r音性（r脱落） (Non-rhoticity (R-loss))
  - Exchange (Input → Output)
    - /ɹ/ → **∅**
  - Typical Environment
    - Coda
  - Examples
    - *car → caː*
  - 地方 (Dialects)
    - **Cockney/Estuary/RP系**
  - Notes
    - r は母音前のみ発音
- 反り舌/バンチドr (Retroflex/bunched r)
  - Exchange (Input → Output)
    - /ɹ/ → **\[ɻ \~ ɚ]**
  - Typical Environment
    - General
  - Examples
    - *right, bird*
  - 地方 (Dialects)
    - **GA**, **AAVE**
  - Notes
    - 後舌/巻き舌傾向
- 歯音化 (Dentalization)
  - Exchange (Input → Output)
    - /t, d, n/ → **\[t̪, d̪, n̪]**
  - Typical Environment
    - before /θ, ð/
  - Examples
    - *eighth \[eɪt̪θ]*
  - 地方 (Dialects)
    - **英全般**, **GA**
  - Notes
    - 接触同化（学術的補足）


## オフビートカウントでの正しい発音の為の基礎


```{.lilypond}
\version "2.24.0"
\include "lilypond-book-preamble.ly"

\layout {
  \context {
    \Lyrics
    \override LyricText.font-name = "Charis SIL Bold Italic"
  }
}

\score {
  <<
    \new RhythmicStaff = "rhythm"  <<
      \new Voice = "v" {
        \voiceOne
        \time 9/8
        \partial 8
        c8 |
        c8 c8 c8 
        c8 c8 c8 
        c8 c8 c8 
        c8 c8 c8 
      }
    >>
    \new Lyrics \lyricsto "v" {
        ʔ -- | ɔɚ -- n tw | o o thr | ee
    }
    \new Lyrics \lyricsto "v" {
        ʔ -- | a -- n tw | o o thr | ee
    }
  >>
}
```

```{mermaid}
flowchart LR
  A[Hard edge] --> B(Round edge)
  B --> C{Decision}
  C --> D[Result one]
  C --> E[Result two]
```





オフビートカウントは、数字と簡単な単語と記号を使って数えるだけの作業です。必要な単語を最小限にとどめることでストレス拍リズム・シラブル拍リズムのリズム構造を集中して練習することが可能になります。

* 数字
    * 1,2,3,4,5,6,7,8,9
* 記号
    * & ( and )
* アルファベット
    * E (イー) 
    * A (アー)

## 三連符オフビートカウントの発音


![](/offbeat-count-phonetics/attachments/triplet-offbeat-count.png)


* 1 & A 
* 2 & A 
* 3 & A 
* 4 & A 
* 5 & A 
* 6 & A 
* 7 & A
* 8 & A

## 九連符オフビートカウントの発音

九連符オフビートカウントとは、三連符オフビートカウントを 3ⁿ 理論にしたがって三連符で二重の弱拍先行を構築したものです。 次の様に１拍３連符を先頭の音を変えながら３回読むことで９を表現します。

| 1   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

このように「横に読んでも」 1 & a 「縦に読んでも」 1 & a になっています。

これを８拍単位で数えると次のようになります。


![](/offbeat-count-phonetics/attachments-src/nonuplets-offbeat-count.png)


```{bash}
#| output: asis
echo "hello"
echo "hello"
echo "hello"
echo "hello"
```


| 1   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

| 2   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

| 3   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

| 4   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

| 5   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

| 6   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

| 7   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

| 8   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

| 1   | &   | a   |
| --- | --- | --- |
| &   | &   | a   |
| a   | &   | a   |

