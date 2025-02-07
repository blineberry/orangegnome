local rawhtml_replacement_map = {
    ["cite"] = "_",
    ["em"] = "_"
}

local function starts_with(str, start)
    return string.sub(str, 1, string.len(start)) == start
end

local function rawhtml_tag_replace(raw,tag,replacement)
    
    if starts_with(raw.text, "<" .. tag .. ">") then
        return pandoc.Str(replacement)
    end

    if starts_with(raw.text, "<" .. tag .. " ") then
        return pandoc.Str(replacement)
    end
    
    if starts_with(raw.text, "</" .. tag .. ">") then
        return pandoc.Str(replacement)
    end

    return raw    
end

-- Writer = pandoc.scaffolding.Writer

-- Writer.Block.RawBlock = function(rawBlock) 
--     return Writer.Blocks(rawBlock.text)
-- end

-- Template = pandoc.template.default 'commonmark'

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

local function raw_tag_is(tag, raw)
    
    if starts_with(raw.text:lower(), "<" .. tag:lower() .. ">") then
        return true
    end

    if starts_with(raw.text:lower(), "<" .. tag:lower() .. " ") then
        return true
    end

    if starts_with(raw.text:lower(), "</" .. tag:lower() .. ">") then
        return true
    end

    return false
end

local function handle_html_inline(rawInline)
    -- only handle raw html
    if rawInline.format ~= "html" then
        return rawInline
    end

    if raw_tag_is("cite", rawInline) then
        return "_"
    end

    -- strip unknown html
    return ""
end

local blockQuoteFilters = {
    Blocks = function(str) 

    end
}

function Writer (doc, opts)
    local filter = {
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
            return raw.format:match 'html'
                and pandoc.read(raw.text, 'html').blocks
                or raw
        end,
        RawInline = function(raw)
            return handle_html_inline(raw)
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

    --html = pandoc.write(doc:walk(), 'html', opts)
    --doc = pandoc.Pandoc(html)
    return pandoc.write(doc:walk(filter), 'plain', opts)
    --print(type(html))
    --return "done"
end