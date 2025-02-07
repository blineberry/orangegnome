import pypandoc
from pathlib import Path

writer = './feed/pandocfilters/plaintext_writer.lua'
extra_args = ['--wrap=preserve']
input = Path("./feed/pandocfilters/test.md")

# pypandoc.convert_file("./feed/pandocfilters/source.html", './feed/pandocfilters/plaintext_writer.lua', format='html+raw_html', outputfile="./feed/pandocfilters/test.txt", filters=[], extra_args=["--verbose"])
# pypandoc.convert_file("./feed/pandocfilters/source.html", 'plain', format='html+raw_html', outputfile="./feed/pandocfilters/test.txt", filters=['./feed/pandocfilters/plaintext_filter.lua'], extra_args=["--verbose"])
pypandoc.convert_file("./feed/pandocfilters/source.html", 'native', format='html+raw_html', outputfile="./feed/pandocfilters/test.native.txt", extra_args=extra_args)
pypandoc.convert_file("./feed/pandocfilters/source.html", 'commonmark+raw_html', format='html+raw_html', outputfile="./feed/pandocfilters/source.md", extra_args=extra_args)
pypandoc.convert_file("./feed/pandocfilters/source.md", writer, format='commonmark+raw_html', outputfile="./feed/pandocfilters/test.txt", extra_args=extra_args)
pypandoc.convert_file("./feed/pandocfilters/source.md", 'html', format='commonmark+autolink_bare_uris', outputfile="./feed/pandocfilters/test.html", extra_args=extra_args)
#html = pypandoc.convert_file("./feed/pandocfilters/source.html", 'html+raw_html', format='commonmark+raw_html', extra_args=extra_args)
#pypandoc.convert_text(html, 'plain', format='html+raw_html', outputfile="./feed/pandocfilters/test.txt", extra_args=extra_args)

# html = pypandoc.convert_file(input, 'html+raw_html', format='commonmark+raw_html', extra_args=extra_args)

# output = input.with_suffix('.txt')
# pypandoc.convert_text(html, writer, format='html+raw_html', extra_args=extra_args, outputfile=output)

# output = input.with_suffix('.native.txt')
# pypandoc.convert_file(input, 'native', format='commonmark', extra_args=extra_args, outputfile=output)

# output = input.with_suffix('.html')
# pypandoc.convert_file(input, 'html', format='commonmark', extra_args=extra_args, outputfile=output)

# output = input.with_suffix('.html.native.txt')
# pypandoc.convert_file(input.with_suffix('.html'), 'native', format='html', extra_args=extra_args, outputfile=output)

# output = input.with_suffix('.html.txt')
# pypandoc.convert_file(input.with_suffix('.html'), writer, format='html', extra_args=extra_args, outputfile=output)