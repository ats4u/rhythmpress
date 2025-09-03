\include "lilypond-book-preamble.ly"
\paper {
  left-margin   = 3\mm
  right-margin  = 3\mm
  top-margin    = 10\mm
  bottom-margin = 10\mm
  indent = 0
  tagline = ##f
}
\layout {
  \context {
    \Lyrics
    \override LyricText.font-name = "Charis SIL Bold Italic"
  }
}
