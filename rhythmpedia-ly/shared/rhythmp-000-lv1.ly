
\score {
  <<
    \new RhythmicStaff = "rhythm"  <<
      \new Voice = "v" {
        \voiceOne
        \time 9/8
        \partial 8
                                        do8 |
        do8 do8 do8 do8 do8 do8 do8 do8 do8 |
        do8 do8 do8 do8 do8 do8 do8 do8 do8 |
        do8 do8 do8 do8 do8 do8 do8 do8 do8 |
        do8 do8 do8
      }
      \new NullVoice = "aligner" {
        \relative do' {
          \voiceOne
          \partial 8
          do8

          do4. do4. do4.
          do4. do4. do4.
          do4. do4. do4.
          do4.
        }
      }
    >>

    \new Lyrics \with { instrumentName = "" } \lyricsto "aligner" {
       _
       \markup { |1  }
       \markup { |2  }
       \markup { |3  }
       \markup { |4  }
       \markup { |5  }
       \markup { |6  }
       \markup { |7  }
       \markup { |8  }
       \markup { |9  }
       \markup { |1  }
       _
    }

    \new Lyrics \lyricsto "v" {
                          \markup { -    }
        \markup { | o   } \markup { -    }  ne
        \markup { | t   } \markup { -    }  wo
        \markup { | thr } \markup { -    }  ee
        \markup { | f   } \markup { -    }  our
        \markup { | f   } \markup { -i   }  ve
        \markup { | s   } \markup { -i   }  x
        \markup { | se  } \markup { -ve  }  n
        \markup { | ʔ   } \markup { eigh }  t
        \markup { | n   } \markup { -i   }  ne
        \markup { | o   } \markup { -    }  ne
        _ _
    }

    \new Lyrics \lyricsto "v" {
        \markup { w   } \markup { | ʌ  } n
        \markup { t   } \markup { | uː} \markup { _ }
        \markup { θɹ } \markup { | iː} \markup { _ }
        \markup { f   } \markup { | ɔ  } ɹ
        \markup { f   } \markup { | aɪ } v
        \markup { s   } \markup { | ɪ  } ks
        \markup { ˈs  } \markup { | ɛ  } vən
        \markup { ʔ   } \markup { | eɪ } t
        \markup { n   } \markup { | aɪ } n
        \markup { w   } \markup { | ʌ  } n
        _ _
    }
  >>
}
