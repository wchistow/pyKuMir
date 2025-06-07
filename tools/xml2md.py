"""Инструмент для преобразования документации оригинального КуМира из формата XML в MarkDown."""
import sys
from pathlib import Path
import os
import re
import xml.etree.ElementTree as ET


def handle_file(file):
    with (open(file) as f):
        s = f.read().replace('&nbsp;', ' '
                   ).replace('&times;', '*'
                   ).replace('&alpha;', 'α'
                   ).replace('&rarr;', '->'
                   ).replace('&le;', 'меньше, чем'
                   ).replace('&ge;', 'больше, чем'
                   ).replace('&hellip;', '...'
                   ).replace('&beta;', 'β'
                   ).replace('&gamma;', 'γ')
        print(f'Opening {file}...')
        root = ET.fromstring(s)

    with open(''.join(file.split('.')[:-1]) + '.md', 'w') as f:
        f.write(handle_elem(root, 0))


def handle_elem(elem, indent: int, in_list=None, list_indent=-1):
    res = ''
    for ch in elem:
        ch.tag = re.sub(r'{.*}', '', ch.tag)
        match ch.tag:
            case 'title':
                res += f'\n\n{"#"*(indent+1)} {ch.text.strip()}\n\n'
            case 'titleabbrev' | 'subtitle':
                res += f'\n\n#{"#"*(indent+1)} {ch.text.strip()}\n\n'
            case 'caption':
                res += ch.text.strip()
            case 'para':
                lists = []
                for c in ch:
                    if c.tag in ('orderedlist', 'itemizedlist'):
                        lists.append(c)

                if lists:
                    res += ch.text + '\n'
                    for lst in lists:
                        match lst.tag:
                            case 'orderedlist':
                                res += handle_elem(lst, indent+1, 'order', list_indent+1)
                            case 'itemizedlist':
                                res += handle_elem(lst, indent+1, 'item1', list_indent+1)
                else:
                    res += ' '.join(map(lambda s: s.strip(), ch.itertext())) + '\n'
            case 'section' | 'funcsynopsis' | 'funcsynopsisinfo' | 'funcprototype' | 'example' | 'sectioninfo':
                res += handle_elem(ch, indent+1, in_list)
            case 'package':
                res += f'Пакет: {ch.text.strip()}\n\n'
            case 'parameter':
                res += f'`{ch.text.strip()}`'
            case 'funcdef':
                res +=  f'`{ch.text.strip()} {ch[0].text.strip()}`\n\nАргументы:\n\n'
            case 'paramdef':
                res +=  f' + `{(ch.text or "").strip()} {ch[0].text.strip()}`\n\n'
            case 'orderedlist' | 'itemizedlist':
                res += handle_elem(ch, indent+1, 'order' if ch.tag == 'orderedlist' else 'item1', list_indent+1)
            case 'keywordset':
                res += '\nКлючевые слова:\n' + handle_elem(ch, indent+1, 'order', list_indent+1)
            case 'emphasis':
                res += ch.text
            case 'remark':
                res += 'Замечание:\n' + handle_elem(ch, indent, in_list, list_indent)
            case 'table':
                res += '\n\n' + ET.tostring(ch, encoding='utf-8').decode('utf-8') + '\n\n'
            case 'listitem' | 'keyword':
                if in_list == 'order':
                    res += '   '*list_indent + f' + {handle_elem(ch, indent+1, in_list, list_indent+1)}\n'
                else:
                    res += '   '*list_indent + f'{in_list[4:]}. {handle_elem(ch, indent+1, in_list, list_indent+1)}\n'
                    in_list = 'item' + str(int(in_list[4:]) + 1)
            case 'code':
                res += f'`{ch.text.strip()}`'
            case 'programlisting':
                res += f'\n```{ch.attrib.get("role", "")}\n{ch.text.strip()}\n```\n'
            case 'include':
                res += f'[{ch.attrib["href"]}](./{ch.attrib["href"]})\n'
            case 'abstract':
                res += handle_elem(ch, indent, in_list, list_indent)
            case 'mediaobject':
                res += handle_elem(ch, indent, in_list, list_indent)
            case 'imageobject':
                res += f'\n![](./{ ch[0].attrib["fileref"]})\n'
            case _:
                print('!', ch.tag)
                res += str(ch)
    return res


def get_all_xml_files(path):
    res = []
    for root, _, files in path.walk():
        for file in files:
            if file.startswith('./'):
                file = file[2:]
            if file.endswith('.xml'):
                res.append(os.path.join(root, file))
    return res


if __name__ == '__main__':
    path = sys.argv[-1]
    pathable = Path(path)
    if pathable.is_file() and path.endswith('.xml'):
        handle_file(os.path.abspath(path))
    elif pathable.is_dir():
        for file in get_all_xml_files(pathable):
            handle_file(file)
    else:
        print('Something wrong with arguments...')
