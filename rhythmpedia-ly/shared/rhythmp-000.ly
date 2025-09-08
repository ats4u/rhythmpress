\score {
  <<
    \new RhythmicStaff = "rhythm"  <<
      \new Voice = "v" {
        \voiceOne
        \time 3/4
        do4 do4 do4
        do4 do4 do4
        do4 do4 do4
        do4 s2
      }
    >>

    \new Lyrics \lyricsto "v" {
      "1" "2" "3" "4" "5" "6" "7" "8" "9" "1"
    }
    \new Lyrics \lyricsto "v" {
        \markup{ | one   }
        \markup{ | two   }
        \markup{ | three }
        \markup{ | four  }
        \markup{ | five  }
        \markup{ | six   }
        \markup{ | seven }
        \markup{ | eight }
        \markup{ | nine  }
        \markup{ | one   }
    }

    \new Lyrics \lyricsto "v" {
      \markup { | wʌn   }
      \markup { | tuː  }
      \markup { | θɹiː}
      \markup { | fɔɹ   }
      \markup { | faɪv  }
      \markup { | sɪks  }
      \markup { | sɛvən }
      \markup { | eɪt   }
      \markup { | naɪn  }
      \markup { | tɛn   }
      \markup { | wʌn   }
    }
  >>
}
