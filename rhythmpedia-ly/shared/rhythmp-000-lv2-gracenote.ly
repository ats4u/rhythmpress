
gone = { \stemDown \acciaccatura do16           \stemUp do8] }
gtwo = { \stemDown \acciaccatura { do16  do16 } \stemUp do8] }

\score {
  <<
    \new RhythmicStaff = "rhythm"  <<
      \new Voice = "counting" {
        \voiceOne
        \time 3/8
        \partial 8

         do8]  | do8[  do8   \gone    do8[  do8   \gone  do8[  do8
         do8]  | do8[  do8   \gone    do8[  do8   \gone  do8[  do8
        \gtwo  | do8[  do8   \gone    do8[  do8   \gone  do8[  do8
        \gone  | do8[  do8   \gone
      }
    >>

    \new Lyrics \with { instrumentName = "" } \lyricsto "counting" {
        \markup   { "-" } \markup { | 1  } "-"
        \markup   { "-" } \markup { | 2  } "-"
        \markup   { "-" } \markup { | 3  } "-"
        \markup   { "-" } \markup { | 4  } "-"
        \markup   { "-" } \markup { | 5  } "-"
        \markup   { "-" } \markup { | 6  } "-"
        \markup   { "-" } \markup { | 7  } "-"
        \markup   { "-" } \markup { | 8  } "-"
        \markup   { "-" } \markup { | 9  } "-"
        \markup   { "-" } \markup { | 1  } "-"
        \markup   { "-" }
    }

    \new Lyrics \with { instrumentName = "" } \lyricsto "counting" {
        \markup {      o   } \markup { | -     } "-"
        \markup {  ne  t   } \markup { | wo    } "-"
        \markup {     thr  } \markup { | ee    } "-"
        \markup {      f   } \markup { | ou    } "-"
        \markup {  r   f   } \markup { | -i    } "-"
        \markup {  ve  s   } \markup { | -i    } "-"
        \markup {  x   s   } \markup { | e     } \markup{ -ve }
        \markup {  n       } \markup { | ei    } gh
        \markup {  t   n   } \markup { | -i    } "-"
        \markup {  ne  o   } \markup { | -     } "-"
        \markup {  ne      }
    }

    \new Lyrics \with { instrumentName = "" } \lyricsto "counting" {
        \markup {     w   }   \markup { | ʌ  } "-"
        \markup {  n  t   }   \markup { | uː} "-"
        \markup {     θɹ }   \markup { | iː} "-"

        \markup {     f   }   \markup { | ɔ  } "-"
        \markup {  ɹ  f   }   \markup { | aɪ } "-"
        \markup {  v  s   }   \markup { | ɪ  } "-"

        \markup { ks ˈs   }   \markup { | ɛ  } "və"
        \markup {     n   }   \markup { | eɪ } "-"
        \markup { t   n   }   \markup { | aɪ } "-"

        \markup { n   w   }   \markup { | ʌ  } n
        _ _
    }
  >>
}
