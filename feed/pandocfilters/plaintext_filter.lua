local function wrap(content, wrap)
    if type(content) == "string" then
        return wrap .. content .. wrap
    end

    if type(content) == "table" then
        content:insert(1, pandoc.Str(wrap))
        content:extend({pandoc.Str(wrap)})
        return content
    end
    
    return content
end

return {
    Header = function(header)
        for i = 1, #header.content,1
        do
            if header.content[i].tag == "Str" then
                header.content[i].text = string.rep("#", header.level) .. " " .. header.content[i].text
                break
            end
        end

        return header
    end,
    Emph = function(emph)
        return wrap(emph.content, "_")
    end,
    Strong = function(strong)
        return wrap(strong.content, "*")
    end,
    RawBlock = function(raw)
        return {pandoc.Str(raw.t), pandoc.Str(raw.format), pandoc.Str(raw.text)}
    end,
    RawInline = function(raw)
        return {pandoc.Str(raw.t), pandoc.Str(raw.format), pandoc.Str(raw.text)}
        --return handle_html_inline(raw)
    end,
    Link = function(link)
        if link.target == "" then
            return link.content
        end

        if link.target == pandoc.utils.stringify(link.content) then
            return link.content
        end
        return link.content:extend({pandoc.Str(" ("), pandoc.Str(link.target), pandoc.Str(")")})
    end,
    Image = function(image)   
        output = pandoc.List({"[Image:", "", ""," (" .. image.src .. ")]"})
        
        if image.caption[1] ~= nil then
            output[2] = " " .. pandoc.utils.stringify(image.caption)
        end

        if image.title ~= "" then
            output[3] = " “" .. image.title .. "”"
        end

        return output
    end,
    Code = function(code)
        return wrap(code.text,"`")
    end,
    Underline = function(underline)
        return wrap(underline.content, "_")
    end
}