#!/usr/bin/env lua


local CFG = {
  outdir = "lilypond-out",
  utc = true,
  compile_opts = "--svg", -- included in cache hash (fixed in v1)
}


function CFG.hello()
  print( self.outdir )
end

print( CFG:hello() )
