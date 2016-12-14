from lxml import etree

parser = etree.XMLParser(recover=True)
tree = etree.parse('output.txt',parser)

root = tree.xpath('//cli')[0]
print ("HEllo{0}".format(root))
print(etree.tostring(root))
