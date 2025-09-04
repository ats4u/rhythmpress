-- Expand {{var}} / {{var|default}} in ATX headers (and optionally anywhere)
-- Usage (Quarto _quarto.yml or doc front matter):
-- filters: [filters/expand-vars.lua]

local META = pandoc.Meta({})

-- Lookup meta value by dotted path (e.g., params.title2)
local function lookup_meta(path, meta)
  local cur = meta
  for key in path:gmatch("[^%.]+") do
    if type(cur) == "table" then cur = cur[key] else cur = nil end
    if not cur then break end
  end
  if type(cur) == "table" then
    return pandoc.utils.stringify(cur)
  end
  return cur
end

local function expand_template(s, meta)
  -- {{ key }} or {{ key|default text }}
  return (s:gsub("{{%s*([^}|]+)%s*(|([^}]*))?}}", function(key, _dbar, def)
    key = key:gsub("%s+$", "")
    local val

    -- env:NAME support
    local envname = key:match("^env:(.+)$")
    if envname then
      val = os.getenv(envname)
    else
      val = lookup_meta(key, meta)
    end

    if (not val or val == "") and def then
      val = def
    end
    return val or ""
  end))
end

-- Optional: lines like "?var:NAME value" to set/override variables from body text.
-- Example: "?var:section_label Rhythm 101"
local function parse_var_assignment(inlines)
  local text = pandoc.utils.stringify(inlines)
  local name, value = text:match("^%?var:([%w_%.:-]+)%s+(.+)$")
  if name and value then
    -- store under params.* to avoid colliding with top keys
    if not META.params then META.params = pandoc.MetaMap({}) end
    META.params[name] = pandoc.MetaString(value)
    return true
  end
  return false
end

-- Re-parse a plain Markdown inline string back into Pandoc inlines
local function parse_inlines(md)
  local doc = pandoc.read(md, "markdown")
  local b = doc.blocks[1]
  if b and b.t == "Para" then
    return b.content
  end
  -- Fallback: single Str
  return { pandoc.Str(md) }
end

return {
  {
    Meta = function(m) META = m; return nil end,

    -- If you want expansion everywhere, add Para, Plain, etc. (kept minimal per ask)
    Header = function(h)
      local before = pandoc.utils.stringify(h.content)
      local after  = expand_template(before, META)
      if after ~= before then
        h.content = parse_inlines(after)
        return h
      end
    end,

    -- Optional: consume ?var:NAME value lines (they won’t appear in output)
    Para = function(p)
      if parse_var_assignment(p.content) then
        return pandoc.Null()
      else
        return nil
      end
    end,
    Plain = function(p)
      if parse_var_assignment(p.content) then
        return pandoc.Null()
      else
        return nil
      end
    end,
  }
}

