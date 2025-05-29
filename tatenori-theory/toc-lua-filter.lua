
toc = {}

function Header(el)
  local level = el.level
  local text = pandoc.utils.stringify(el.content)
  local id = el.identifier
  table.insert(toc, { level = level, text = text, id = id })
  return {}
end

function Pandoc(doc)
  local blocks = {}
  local last_level = 0

  for _, item in ipairs(toc) do
    local indent = string.rep("  ", item.level - 1)
    local line = string.format("%s- [%s](#%s)", indent, item.text, item.id)
    table.insert(blocks, pandoc.RawBlock("markdown", line))
  end

  return pandoc.Pandoc(blocks)
end
