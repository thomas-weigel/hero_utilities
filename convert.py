#!/usr/bin/env python3

'''
Intended for use with HeroDesigner.

This script takes in an XML file and converts any non-TAIL text, attributes, and nodes and converts
them into another format, with the ability to restore it to valid XML; and vice versa.

It ignores pretty much everything about XML that isn't currently being used by HeroDesigner, so
TAIL text, namespaces, and so on will all be lost. Do not use this with production data.
'''

import argparse
import sys

import lxml.etree
import yaml

__VERSION__ = "0.1.1"


def main():
    '''
    Checks for command-line arguments and then performs the requested conversion,
    returning the result as a string (which can then be piped into a file if desired,
    or just looked at.
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("--input-format", "-i", default="hdt", help="hdt|yaml|xml")
    parser.add_argument("--output-format", "-o", default="yaml", help="hdt|yaml|xml")
    parser.add_argument("filename", help="the file to be used as input")
    args = parser.parse_args()

    data = {
        "hdt": hdt_parse,
        "yaml": yaml_parse,
        "xml": xml_parse,
        }[args.input_format](args.filename)

    output = {
        "hdt": hdt_output,
        "yaml": yaml_output,
        "xml": xml_output,
        }[args.output_format](data)

    print(output)


def yaml_parse(filename):
    'Turns a YAML file into a data object.'
    data = yaml.load(open(filename, 'r'), Loader=yaml.Loader)
    if len(data.keys())>1:
        data = {"TEMPLATE": data}
    return data


def yaml_output(data):
    'Turns a data object into YAML and returns that as a string.'
    return yaml.dump(data)


def xml_parse(filename):
    'Turns an XML file into a nested dictionary.'

    root = lxml.etree.parse(open(filename, 'rb')).getroot()
    data = { root.tag: xml_parsechild(root) }
    return data


def xml_output(data):
    'Turns a nested dictionary into XML and returns that as a string.'
    tag = list(data.keys())[0]
    root = xml_createnode(tag, data[tag])

    return lxml.etree.tostring(root, pretty_print=True).decode()


def xml_createnode(tag, data):
    'Recursively creates a node and any subnodes from a tagname and dictionary.'
    node = lxml.etree.Element(tag)
    if type(data) is str:
        node.text = data
    else:
        for category in data:
            if category == 'attributes':
                for key in data[category]:
                    node.attrib[key] = data[category][key]
            elif category == 'nodes':
                for subdata in data[category]:
                    tag = list(subdata.keys())[0]
                    subnode = xml_createnode(tag, subdata[tag])
                    node.append(subnode)
            else:
                raise ValueError(
                    f"Unexpected key '{category}', containing {data[category]}"
                    )

    return node


def xml_parsechild(node):
    'Recursively converts an XML node into a dictionary.'
    data = {}

    # HDT nodes with text in them are rare and are always text-only
    if node.text is not None and str(node.text).strip():  # has actual text
        data = ' '.join(str(node.text).split())
        if len(node.attrib.keys()) or len(node):
            raise ValueError(
                f"unexpected text in {node.tag}:\n  attrib: {node.attrib}\n  children: {len(node)}"
                )
    else:  # without text, we look at other things.
        if len(node.attrib.keys()):  # has attributes
            data['attributes'] = {key:str(node.attrib[key]) for key in node.attrib}

        if len(node):  # has children
            children = []
            for child in node:
                children.append({child.tag: xml_parsechild(child)})

            data['nodes'] = children

    return data


def hdt_parse(filename):
    'Turns an HDT XML file into a data object with a cleaner output.'

    root = lxml.etree.parse(open(filename, 'rb')).getroot()
    data = { root.tag: hdt_parsechild(root) }
    return data


def hdt_output(data):
    'Turns a data object into HDT XML and returns that as a string.'
    tag = list(data.keys())[0]
    root = hdt_createnode(tag, data[tag])

    return lxml.etree.tostring(root, pretty_print=True).decode()


def hdt_createnode(tag, data):
    'Recursively creates a node and any subnodes from a tagname and data object.'
    node = lxml.etree.Element(tag)
    if type(data) is str:
        node.text = data
    else:
        node.attrib.update(data.pop(0)['attributes'])

        for child in data:
            tag = list(child.keys())[0]
            subnode = hdt_createnode(tag, child[tag])
            node.append(subnode)

    return node


def hdt_parsechild(node):
    'Recursively converts an HDT XML node into a data object.'
    data = [{'attributes': {}}]

    # HDT nodes with text in them are rare and are always text-only
    if node.text is not None and str(node.text).strip():  # has actual text
        data = ' '.join(str(node.text).split())
        if len(node.attrib.keys()) or len(node):
            raise ValueError(
                f"unexpected text in {node.tag}:\n  attrib: {node.attrib}\n  children: {len(node)}"
                )
    else:  # without text, we look at other things.
        data[0]['attributes'].update(node.attrib)
        for child in node:
            tag = child.tag
            data.append({tag: hdt_parsechild(child)})

    return data


if __name__=='__main__':
    main()
