#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import sys, getopt
import glob
import os


def process_files(inputdir, outputdir):
    os.chdir(inputdir)
    enex_notes = []
    output_filename = 'Tomboy2Evernote.enex'
    i = 0
    for file in glob.glob("*.note"):
        note_file_path = inputdir + '/' + file
        note_body = open(note_file_path, 'r').read()
        tag = get_tag(note_body)
        print(tag)
        title = get_title(note_body)
        html_note_body = get_html_body(note_body)
        created_date = tomboy_to_enex_date(get_created_date(note_body))
        updated_date = tomboy_to_enex_date(get_updated_date(note_body))
        enex_notes.append(make_enex(title, html_note_body, created_date, updated_date, tag))
        i += 1
    multi_enex_body = make_multi_enex(enex_notes)
    save_to_file(outputdir, output_filename, multi_enex_body)
    print("Exported notes count: ",i)
    print("Evernote file location: " + outputdir + "/" + output_filename)


def get_title(note_body):
    title_regex = re.compile("<title>(.+?)</title>")
    matches = title_regex.search(note_body);
    if matches:
        return matches.group(1)
    else:
       return "No Title"


def get_created_date(note_body):
    created_date_regex = re.compile("<create-date>(.+?)</create-date>")
    matches = created_date_regex.search(note_body);
    if matches:
        return matches.group(1)
    else:
       return "No Created Date"

def get_updated_date(note_body):
    updated_date_regex = re.compile("<last-change-date>(.+?)</last-change-date>")
    matches = updated_date_regex.search(note_body);
    if matches:
        return matches.group(1)
    else:
       return "No Updated Date"


def tomboy_to_enex_date(tomboy_date):
    return re.sub(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2}).*", r"\1\2\3T\4\5\6Z",
                  tomboy_date)

def get_tag(note_body):
    created_date_regex = re.compile("<tag>(.+?)</tag>")
    matches = created_date_regex.search(note_body);
    if matches:
        parts = matches.group(1).split(':')
        if(len(parts) == 3):
            return parts[2]
        else:
            return "NA"
    else:
       return "NA"


def get_html_body(note_body):
    new_line = '<BR/>'
    xml_tag = r"<(\/?)[a-zA-Z0-9_\-:]+>"
    start_xml_tag = r"<[a-zA-Z0-9_\-:]+>"

    # make note body a one liner
    note_body = note_body.replace('\n', new_line)

    # get content
    note_body = re.sub(r".*<note-content.+?>(.+?)</note-content>.*", r"\1", note_body)

    # strip title until new_line or start_xml_tag
    note_body = re.sub(r"^(.+?)(" + start_xml_tag + "|" + new_line + ")", r"\2", note_body)

    # strip first two new lines, even if prefixed with an xml tag
    tag = re.match("^" + start_xml_tag, note_body)
    if tag != None:
        note_body = re.sub(r"^" + start_xml_tag, r"", note_body)
    note_body = re.sub(r"^(" + new_line + "){1,2}", r"", note_body)
    if tag != None:
        note_body = tag.group(0) + note_body

    # links
    note_body = re.sub(r"<link:internal>(.+?)</link:internal>", r"\1", note_body)
    note_body = re.sub(r"<link:broken>(.+?)</link:broken>", r"\1", note_body)

    p = re.compile(r"(<link:url>(.+?)</link:url>)")
    for m in p.finditer(note_body):
        if re.search(r"^([a-zA-Z0-9\._%+\-]+@(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,10}|https?://.+)$", m.group(2)):
            note_body = note_body.replace(m.group(1), '<a href="' + m.group(2) + '">' + m.group(2) + "</a>")
        else:
            note_body = note_body.replace(m.group(1), m.group(2))

    # lists
    note_body = re.sub(r"<(\/?)list>", r"<\1ul>", note_body)
    note_body = re.sub(r'<list-item dir="ltr">', r"<li>", note_body)
    note_body = re.sub(r"<(\/?)list-item>", r"<\1li>", note_body)

    # higlight
    note_body = re.sub(r"<highlight>(.+?)</highlight>", r'<span style="background:yellow">\1</span>', note_body)

    # font size
    note_body = re.sub(r"<size:small>(.+?)</size:small>", r'<span style="font-size:small">\1</span>', note_body)
    note_body = re.sub(r"<size:large>(.+?)</size:large>", r'<span style="font-size:large">\1</span>', note_body)
    note_body = re.sub(r"<size:huge>(.+?)</size:huge>", r'<span style="font-size:xx-large">\1</span>', note_body)

    # text style
    note_body = re.sub(r"<(\/?)monospace>", r"<\1code>", note_body)
    note_body = re.sub(r"<(\/?)bold>", r"<\1b>", note_body)
    note_body = re.sub(r"<(\/?)italic>", r"<\1i>", note_body)
    note_body = re.sub(r"<(\/?)strikethrough>", r"<\1strike>", note_body)

    # identation
    note_body = re.sub(r"\t", r"&nbsp; &nbsp; &nbsp; &nbsp; ", note_body)
    while re.search(new_line + " ", note_body) != None:
        note_body = re.sub("(" + new_line + " *) ", r"\1&nbsp;", note_body)

    # set new lines
    note_body = note_body.replace(new_line, '<br/>\n')

    return note_body


def make_enex(title, body, created_date, updated_date, tag):
    return '''<note><title>''' + title + '''</title><content><![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">

<en-note style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;">
''' + body + '''
</en-note>]]></content><created>''' + created_date + '''</created><updated>''' + updated_date + '''</updated><tag>''' + tag + '''</tag></note>'''


def make_multi_enex(multi_enex_body):
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export2.dtd">
<en-export export-date="20150412T153431Z" application="Evernote/Windows" version="5.x">
''' + ''.join(multi_enex_body) + '''</en-export>'''


def save_to_file(outputdir, filename, body):
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    text_file = open(outputdir + '/' + filename, "w")
    text_file.write(body)
    text_file.close()


def get_help_line():
    print('Usage: ', sys.argv[0], ' -i <inputdir> -o <outputdir>')


def get_input_params(argv):
    inputdir = ''
    outputdir = ''
    printhelpline = 0
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["idir=", "odir="])
    except getopt.GetoptError:
        exit_with_error()
    for opt, arg in opts:
        print(opt + ':' + arg)
        if opt == '-h':
            get_help_line()
            sys.exit()
        elif opt in ("-i", "--idir"):
            inputdir = arg
        elif opt in ("-o", "--odir"):
            outputdir = arg
    if (inputdir == ""):
        print("Error: Missing input folder")
        printhelpline = 1
    if (outputdir == ""):
        print("Error: Missing output folder")
        printhelpline = 1
    if printhelpline == 1:
        exit_with_error()
    return (inputdir, outputdir)


def exit_with_error():
    get_help_line()
    sys.exit(2)


def main(argv):
    inputdir, outputdir = get_input_params(argv)
    process_files(inputdir, outputdir)


if __name__ == "__main__":
    main(sys.argv[1:])
