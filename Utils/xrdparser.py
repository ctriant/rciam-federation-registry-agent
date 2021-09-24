import json
from logging import raiseExceptions
from os import link
import xmltodict
import lxml.etree as etree


class XRDParser:
    def __init__(self, infile):
        self.infile = infile
        self.parser = etree.XMLParser(remove_blank_text=True)

    def _remove_namespaces(self, root):
        # Iterate through all XML elements
        for elem in root.getiterator():
            # Skip comments and processing instructions,
            # because they do not have names
            if not (
                isinstance(elem, etree._Comment)
                or isinstance(elem, etree._ProcessingInstruction)
            ):
                # Remove a namespace URI in the element's name
                elem.tag = etree.QName(elem).localname

        # Remove unused namespace declarations
        etree.cleanup_namespaces(root)
        return root

    def append(self, **kwargs):
        tree = etree.parse(self.infile, self.parser)
        root = self._remove_namespaces(tree.getroot())

        if kwargs.get("id"):
            if len(root.xpath(f".//XRD[contains(@id,'{kwargs['id']}')]")):
                raise RuntimeError(f"Metadata with ID '{kwargs['id']}' already exists")
            else:
                xrd = etree.Element("XRD")
                xrd.attrib["id"] = kwargs['id']
                subject = etree.Element("Subject")
                subject.text = kwargs['entity_id']
                link = etree.Element("Link")
                link.text = kwargs.get("text")
                if kwargs.get("rel"):
                    link.attrib["rel"] = kwargs.get("rel")
                if kwargs.get("url"):
                    link.attrib["href"] = kwargs.get("url")
                else:
                    raise RuntimeError("Missing metadata URL")
                xrd.append(subject)
                xrd.append(link)
                root.append(xrd)
                tree.write(self.infile,
                pretty_print=True, xml_declaration=True)
        else:
            raise RuntimeError("Missing metadata ID to be appended")

    def update(self, **kwargs):
        tree = etree.parse(self.infile, self.parser)
        
        root = self._remove_namespaces(tree.getroot())
        
        if kwargs.get("id"):
            for node in root.xpath(f".//XRD[contains(@id,'{kwargs['id']}')]"):
                try:
                    link = node.xpath(f".//Link")
                    if kwargs.get("url"):
                        link[0].attrib["href"] = kwargs['url']
                except:
                    raise RuntimeError("Missing metadata URL")
                try:
                    subject = node.xpath(f".//Subject")
                    if kwargs.get("entity_id"):
                        subject[0].text = kwargs['entity_id']
                except:
                    raise RuntimeError("Missing metadata EntityID")

            tree.write(self.infile,
                pretty_print=True, xml_declaration=True, encoding='UTF-8')
        else:
            raise RuntimeError("Missing metadata ID to be updated")

    def delete(self, id):
        tree = etree.parse(self.infile, self.parser)
        
        root = self._remove_namespaces(tree.getroot())
        
        nodes = root.xpath(f".//XRD[contains(@id,'{id}')]")
        for node in nodes:
            node.getparent().remove(node)

        if len(nodes) > 0:
            tree.write(self.infile,
                pretty_print=True, xml_declaration=True, encoding='UTF-8')
