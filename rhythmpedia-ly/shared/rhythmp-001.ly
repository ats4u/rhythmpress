\include "rhythmpedia-ly/lilypond-preamble.ly"

gone = { \tuplet 3/2 {  do16   do16_~ do16] }  }
gtwo = { \tuplet 3/2 {  do16_~ do16   do16] }  }
gthr = { \tuplet 3/2 {  do16[  do16   do16] }  }
gdot = { \tuplet 3/2 {  do8[          do16] }  }
gura = { \tuplet 3/2 {   r8[          do16] }  }
gsco = { \tuplet 3/2 {  do16 do8            }  }

% gnin = {
%   | do8 \gdot \tuplet 3/2 {  do16   do16   do16] }             % 1
%     do8 \gdot \tuplet 3/2 {  do16   do16   do16] }             %
%     do8 \gdot \tuplet 3/2 {  do16   do16   do16] }             %
% }

gnin = {
  \tuplet 3/2 { do16[  do16  do16] } \tuplet 3/2 { do16[   do16  do16] } \tuplet 3/2 { do16[   do16  do16] }
}
sp = "-"


\score {
  <<
    \new RhythmicStaff = "rhythm"  <<
      \new Voice = "counting" {
        \voiceOne
        \time 3/8

          s8    s8   \gthr              % 1
        | \gsco  \gdot \gone              % &
        | \gsco  \gdot \gthr              % a
        | \gsco  \gdot \gone              % 2
        | \gsco  \gdot \gone              % &
        | \gsco  \gdot \gone              % a
        | \gsco  \gdot \gthr              % 3
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gone              % a

        \break

        | \gsco  \gdot \gthr              % 4
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gone              % a

        | \gsco  \gdot \gthr              % 5
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gone              % a

        | \gsco  \gdot \gthr              % 6
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gone              % a

        \break

        | \gsco  \gdot \gthr              % 7
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gone              % a

        | \gsco  \gdot \gthr              % 8
        | \gsco  \gdot \gthr              % &
        | \gsco  \gdot \gone              % a

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
        \sp  \sp  \sp      \sp     \sp \sp
        "w"  \sp  \sp      "a"     \sp \sp     "n"   \sp \sp

        \sp  \sp  \sp      "ə"     \sp \sp     "n"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     \sp   \sp \sp

        "t"  \sp  \sp      "|uː"  \sp \sp     \sp   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     "n"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     \sp   \sp \sp

        "θ" "ɹ"  \sp      "|iː"  \sp \sp     \sp   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     "n"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     \sp   \sp \sp

        "f"  \sp  \sp      "| ɔ"   \sp \sp     \sp   \sp "ɹ"
        \sp  \sp  \sp      "ə"     \sp \sp     "n"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     \sp   \sp \sp

        "f"  \sp  \sp      "|a"    "ɪ" \sp     "v"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     "n"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     \sp   \sp \sp

        "s"  \sp  \sp      "|ɪ"    \sp \sp     "k"   "s" \sp
        \sp  \sp  \sp      "ə"     \sp \sp     "n"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     \sp   \sp \sp

        "s"  \sp  \sp      "|ɛ"    \sp \sp     "v"   "ə" "n"
        \sp  \sp  \sp      "ə"     \sp \sp     "n"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     \sp   \sp \sp

        \sp  \sp  \sp      "|e"    "ɪ" \sp     "t"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     "n"   \sp \sp
        \sp  \sp  \sp      "ə"     \sp \sp     \sp   \sp \sp

        "w"  \sp \sp       "|a"    \sp \sp      "n"   \sp \sp
      }
    >>
  >>
}
