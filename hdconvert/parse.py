#!/usr/bin/env python3

from lxml import etree
import yaml


def parse(fileobj, input_format="hd"):
    '''
    Accepts a file or file-like object such as StringIO, and parses it according to the
    input_format to produce structured data.

    Currently accepts the HeroDesigner HDT XML format and YAML.
    '''

    if input_format == "hd":
        root = etree.parse(fileobj).getroot()
        return { root.tag: hdt_parsenode(root) }
    elif input_format == "yaml":
        return yaml.load(fileobj, Loader=yaml.Loader)


def serialize(data, output_format="yaml"):
    '''
    Accepts a structured data object, and serializes it into a string according to the
    output_format.

    Can currently produce YAML and the HeroDesigner HDT XML format.
    '''

    if output_format == "hd":
        tag = list(data.keys())[0]
        root = hdt_createnode(tag, data[tag])
        return etree.tostring(root, pretty_print=True).decode()
    elif output_format == "yaml":
        return yaml.dump(data)


def hdt_createnode(tag, data):
    '''Recursively creates a node and any subnodes from a tagname and data object.'''
    tag = tag.upper()
    node = etree.Element(tag)
    if type(data) is str:
        node.text = data
    else:
        if data is None:
            print(f"ERROR: {etree.tostring(node, pretty_print=True).decode()}")
        if len(data):
            attributes = data.pop(0)['attributes']
            for key in attributes:
                if tag=='TEMPLATE' and key in ['version', 'extends']:
                    node.attrib[key] = attributes[key]
                else:
                    node.attrib[key.upper()] = attributes[key]

        if tag == 'LANGUAGE':
            try:
                similar = data.pop(0)['similar']
                for key in similar:
                    degree = key.upper() + 'POINTSIMILARITY'
                    for language in similar[key]:
                        subnode = etree.Element(degree)
                        subnode.text = language
                        node.append(subnode)
            except IndexError:  # No similar languages
                pass

        for child in data:
            tag = list(child.keys())[0]
            subnode = hdt_createnode(tag, child[tag])
            node.append(subnode)

    return node


def hdt_parsenode(node):
    '''Recursively converts an HDT XML node into a data object.'''
    data = []

    # HDT nodes with text in them are rare and are always text-only
    if node.text is not None and str(node.text).strip():  # has actual text
        data = ' '.join(str(node.text).split())
        if len(node.attrib.keys()) or len(node):
            raise ValueError(
                f"unexpected text in {node.tag}:\n" + \
                f"  text: {data}" + \
                f"  attrib: {node.attrib}\n" + \
                f"  children: {len(node)}"
                )
    else:  # without text, we look at other things.
        if len(list(node.attrib.keys())) or len(node):
            data.append({'attributes': {}})
            data[0]['attributes'].update(node.attrib)

            if node.tag == 'LANGUAGE':
                data.append({'similar': {}})

            for child in node:
                tag = child.tag

                # language similarity profile
                if tag == 'ONEPOINTSIMILARITY':
                    if 'one' not in data[1]['similar']:
                        data[1]['similar']['one'] = [child.text,]
                    else:
                        data[1]['similar']['one'].append(child.text)
                elif tag == 'TWOPOINTSIMILARITY':
                    if 'two' not in data[1]['similar']:
                        data[1]['similar']['two'] = [child.text,]
                    else:
                        data[1]['similar']['two'].append(child.text)
                elif tag == 'THREEPOINTSIMILARITY':
                    if 'three' not in data[1]['similar']:
                        data[1]['similar']['three'] = [child.text,]
                    else:
                        data[1]['similar']['three'].append(child.text)
                elif tag == 'FOURPOINTSIMILARITY':
                    if 'four' not in data[1]['similar']:
                        data[1]['similar']['four'] = [child.text,]
                    else:
                        data[1]['similar']['four'].append(child.text)
                else:
                    data.append({tag: hdt_parsenode(child)})

    return data

