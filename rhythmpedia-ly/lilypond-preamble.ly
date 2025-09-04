\include "lilypond-book-preamble.ly"
\include "rhythmpedia-ly/chromatic-solfege.ly"
\language "chromatic-solfege"
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
    \override InstrumentName.font-size = #2
    \override InstrumentName.font-series = #'bold
    \override InstrumentName.font-name = "Charis SIL Bold Italic"
  }
}

