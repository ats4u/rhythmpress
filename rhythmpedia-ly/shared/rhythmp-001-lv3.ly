\include "rhythmpedia-ly/lilypond-preamble.ly"

gone = { \tuplet 3/2 {  do16   do16_~ do16] }  }
gtwo = { \tuplet 3/2 {  do16_~ do16   do16] }  }
gthr = { \tuplet 3/2 {  do16[  do16   do16] }  }
gdot = { \tuplet 3/2 {  do8[          do16] }  }
gura = { \tuplet 3/2 {   r8[          do16] }  }
gsco = { \tuplet 3/2 {  do16 do8            }  }
gnin = {
  \tuplet 3/2 { do16[  do16  do16] } \tuplet 3/2 { do16[   do16  do16] } \tuplet 3/2 { do16[   do16  do16] }
}
sp = "-"
bl = " "

id = #(define-music-function (m) (ly:music?)
  (begin
    (display m)
    m))
rv = #(define-music-function (mus) (ly:music?)
    (make-sequential-music
     (reverse (ly:music-property mus 'elements))))

sw = #(define-music-function (a b) (ly:music? ly:music?)
      (make-sequential-music (list b a)))

idMarkup = #(define-scheme-function (x) (markup?) x)   % identity for markup
idNum    = #(define-scheme-function (x) (number?) x)   % identity for numbers

\score {
  <<
    \new RhythmicStaff = "rhythm"  <<
      \new Voice = "counting" {
        \voiceOne
        \time 3/8

          r8     \gdot \gthr              % 1
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gthr              % a
        | \gsco  \gdot \gthr              % 2
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gthr              % a
        | \gsco  \gdot \gthr              % 3
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gthr              % a

        | \gsco  \gdot \gthr              % 4
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gthr              % a

        | \gsco  \gdot \gthr              % 5
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gthr              % a

        | \gsco  \gdot \gthr              % 6
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gthr              % a

        \break

        | \gsco  \gdot \gthr              % 7
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gthr              % a

        | \gsco  \gdot \gthr              % 8
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gthr              % a

        | \gsco  \gdot \gthr              % 1
        | \gsco  \gdot \gthr              % 1

      }

      \new NullVoice = "aligner" {
        \relative do' {
          \voiceOne
                    s4.
          do4. do4. do4.
          do4. do4. do4.
          do4. do4. do4.
          do4. do4. do4.
          do4. do4. do4.
          do4. do4. do4.
          do4. do4. do4.
          do4. do4. do4.
          do4.
        }
      }

      \new Lyrics \with { instrumentName = "" } \lyricsto "aligner" {
          "1" "|&" "a"
          "2" "|&" "a"
          "3" "|&" "a"
          "4" "|&" "a"
          "5" "|&" "a"
          "6" "|&" "a"
          "7" "|&" "a"
          "8" "|&" "a"
          "1"
      }

      \new NullVoice = "aligner2" {
        \relative do' {
          \voiceOne

          \gnin \gnin \gnin
          \gnin \gnin \gnin
          \gnin \gnin \gnin
          \gnin \gnin \gnin
          \gnin \gnin \gnin
          \gnin \gnin \gnin
          \gnin \gnin \gnin
          \gnin \gnin \gnin
          \gnin \gnin \gnin
        }
      }

      \new Lyrics \with { instrumentName = "" } \lyricsto "aligner2" {
        \sp  \sp  \sp      \sp      \sp

        "w"   \sp \sp      \sw   "|a"    \sp   \sp     \sp  \sp  \sp
        "n"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp   \sp \sp
        "n"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp   \sp \sp

        "t"   \sp  \sp     \sw   "|uː"  \sp   \sp     \sp   \sp \sp
        "(w)" \sp  \sp     \sw   "|ə"    \sp   \sp     \sp  \sp  \sp
        "n"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp   \sp \sp

        "θ"  "ɹ"  \sp     \sw   "|iː"  \sp   \sp     \sp   \sp \sp
        (j)   \sp  \sp     \sw   "|ə"    \sp   \sp     \sp   \sp \sp
        "n"   \sp  \sp     \sw   "|ə"    \sp   \sp     \sp   \sp \sp

        "f"   \sp  \sp     \sw   "| ɔ"   \sp   \sp     \sp  \sp  \sp
        "ɹ"   \sp  \sp     \sw   "|ə"    \sp   \sp     \sp  \sp  \sp
        "n"   \sp  \sp     \sw   "|ə"    \sp   \sp     \sp  \sp  \sp

        "f"   \sp \sp      \sw { "|a"    "ɪ" } \sp     \sp  \sp  \sp
        "v"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp  \sp  \sp
        "n"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp   \sp \sp

        "s"   \sp \sp      \sw   "|ɪ"    \sp   \sp     \sp  \sp  \sp
        "k"   "s" \sp      \sw   "|ə"    \sp   \sp     \sp  \sp  \sp
        "n"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp  \sp  \sp

        "s"   \sp \sp      \sw   "|ɛ"    \sp   \sp     \sp  \sp  \sp
        "v"   "ə" "n"      \sw   "|ə"    \sp   \sp     \sp  \sp  \sp
        "n"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp  \sp  \sp

        "(ɹ)" \sp \sp      \sw  {"|e"    "ɪ"}  \sp     \sp  \sp  \sp
        "t"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp  \sp  \sp
        "n"   \sp \sp      \sw   "|ə"    \sp   \sp     \sp  \sp  \sp

        "w"   \sp \sp      \sw   "|a"    \sp   \sp     "n"   \sp \sp
      }

      \new Lyrics \with { instrumentName = "" } \lyricsto "aligner2" {
        \bl   \bl \bl      \bl     \bl 

        \bl   \bl \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl   \bl \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl   \bl \bl

        \bl   \bl  \bl     \bl   \bl \bl     \bl   \bl \bl
        \bl   \bl  \bl     \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl   \bl \bl

        \bl   \bl  \bl      \bl   \bl \bl     \bl   \bl \bl
        \bl   \bl  \bl      \bl     \bl \bl     \bl   \bl \bl
        \bl   \bl  \bl      \bl     \bl \bl     \bl   \bl \bl

        \bl   \bl  \bl      \bl    \bl \bl     \bl  \bl  \bl
        \bl   \bl  \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl  \bl      \bl     \bl \bl     \bl   \bl \bl

        \bl   \bl  \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl   \bl \bl

        \bl   \bl  \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl  \bl  \bl

        \bl   \bl  \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl  \bl  \bl

        \bl   \bl  \bl    \bl     \bl \bl     \bl  \bl  \bl
        "l"   \bl \bl      \bl     \bl \bl     \bl  \bl  \bl
        \bl   \bl \bl      \bl     \bl \bl     \bl  \bl  \bl

        \bl    \bl \bl       \bl     \bl \bl     \bl   \bl \bl
      }
    >>
  >>
}
