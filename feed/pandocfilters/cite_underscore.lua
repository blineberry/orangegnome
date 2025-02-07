local function starts_with(str, start)
    return string.sub(str, 1, string.len(start)) == start
end

return {
    {
      Cite = function (elem)
        return pandoc.Str "Hiya"
      end,
      RawInline = function(raw)
        if raw.format ~= "html" then
            return raw
        end

        if starts_with(raw.text, "<cite") then
            return pandoc.Str("_")
        end

        if starts_with(raw.text, "</cite") then
            return pandoc.Str("_")
        end

        return raw        
      end,
    }
  }