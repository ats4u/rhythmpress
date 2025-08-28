-- lilypond.lua — Quarto/Pandoc filter for LilyPond
-- HTML: inline SVG.  PDF: include generated PDF.
-- Caches by hashing snippet. Works when LilyPond cd’s into outdir.

local DEFAULT_VERSION = "2.24.0"
local OUTDIR = "lilypond-out"

-- Resolve lilypond binary
local function file_exists(p)
  local f = io.open(p, "rb"); if f then f:close(); return true end
  return false
end

local function resolve_lilypond()
  local env = os.getenv("LILYPOND")
  if env and env ~= "" then return env end
  local mac = "/Applications/LilyPond.app/Contents/Resources/bin/lilypond"
  if file_exists(mac) then return mac end
  return "lilypond"
end

local LILYPOND = resolve_lilypond()

-- Outdir creation (ignore “exists”)
local did_mkdir = false
local function ensure_outdir()
  if did_mkdir then return end
  local ok, err = pcall(function() pandoc.system.make_directory(OUTDIR) end)
  if not ok then
    local em = tostring(err or "")
    if not em:match("exists") then
      error("[lilypond] mkdir failed: " .. em)
    end
  end
  did_mkdir = true
end

-- Small utils
local function write_file(path, txt)
  local f, e = io.open(path, "wb")
  assert(f, "[lilypond] cannot write: " .. path .. " (" .. tostring(e) .. ")")
  f:write(txt); f:close()
end

local function read_file(path)
  local f, e = io.open(path, "rb")
  assert(f, "[lilypond] cannot read: " .. path .. " (" .. tostring(e) .. ")")
  local data = f:read("*a"); f:close(); return data
end

local function q(s) return '"' .. s .. '"' end

-- Run a shell command with CWD = OUTDIR (Pandoc 3 API if available)
local function run_in_outdir(cmd)
  if pandoc.system and pandoc.system.with_working_directory then
    local ok = pandoc.system.with_working_directory(OUTDIR, function()
      local r = os.execute(cmd)
      return (r == true or r == 0)
    end)
    return ok and true or false
  else
    local r = os.execute('cd ' .. q(OUTDIR) .. ' && ' .. cmd)
    return (r == true or r == 0)
  end
end

-- Hash (Pandoc 3+)
local sha1 = (pandoc.utils and pandoc.utils.sha1) or
             function(s) return tostring(#s) end  -- weak fallback

function CodeBlock(el)
  if not (el.classes and el.classes:includes("lilypond")) then return nil end

  ensure_outdir()

  local code = el.text or ""
  local version = (el.attributes and el.attributes["version"]) or DEFAULT_VERSION
  if not code:match("\\version") then
    code = '\\version "' .. version .. '"\n' .. code
  end

  local h = sha1(code)
  local base = "ly-" .. h           -- basename only
  local ly_path = OUTDIR .. "/" .. base .. ".ly"

  if not file_exists(ly_path) then
    write_file(ly_path, code)
  end

  local is_html = FORMAT and FORMAT:match("html")

  if is_html then
    -- Produce SVG(s)
    if not file_exists(OUTDIR .. "/" .. base .. ".svg")
       and not file_exists(OUTDIR .. "/" .. base .. "-1.svg") then
      local cmd = q(LILYPOND) .. " -dbackend=svg -o " .. q(base) .. " " .. q(base .. ".ly")
      assert(run_in_outdir(cmd), "[lilypond] SVG generation failed. Is LilyPond on PATH?")
    end
    -- Prefer single-page filename, otherwise use -1.svg
    local svg_path = OUTDIR .. "/" .. base .. ".svg"
    if not file_exists(svg_path) then
      svg_path = OUTDIR .. "/" .. base .. "-1.svg"
      assert(file_exists(svg_path), "[lilypond] SVG not found after compile")
    end
    local svg = read_file(svg_path)
    return pandoc.RawBlock("html", svg)

  else
    -- Produce PDF
    local pdf_path = OUTDIR .. "/" .. base .. ".pdf"
    if not file_exists(pdf_path) then
      local cmd = q(LILYPOND) .. " -o " .. q(base) .. " " .. q(base .. ".ly")
      assert(run_in_outdir(cmd), "[lilypond] PDF generation failed. Is LilyPond on PATH?")
    end
    return pandoc.Para{ pandoc.Image({}, pdf_path) }
  end
end

-- io.stderr:write("[lilypond] using: " .. LILYPOND .. "\n")

