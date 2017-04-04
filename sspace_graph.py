from graphviz import Digraph
from xml.dom import minidom
from bokeh.plotting import figure, output_file, show
import sys


# parse the scaffold evidence file.
path = sys.argv[1]
with open(path, 'r') as scaffold_evidence:
    scaffolds = {}
    for line in scaffold_evidence:
        if line[0] == '>':
            cur_scaffold = line.split("|")[0][1:]
            scaffolds[cur_scaffold] = []
        elif line[0] != '\n':
            contig = line.split("|")
            scaffolds[cur_scaffold].append(contig)

#Plot each scaffold in seperate svg files
for key in scaffolds:
    print(key)
    print(len(scaffolds[key]))
    if len(scaffolds[key]) == 1:
        continue
    dot = Digraph(comment="SSPACE assembly", format='svg')
    dot.body.extend(['rankdir=LR', 'size="6,6"'])
    dot.engine = 'neato'
    dot.attr('node', shape='circle')
    edge_list = []
    links_list = []
    label_list = []
    prev_node = None
    i = 0
    for contigs in scaffolds[key]:
        
        dot.node(contigs[0]+str(i), label = contigs[0] + '\n' + contigs[1][4:])
        label_list.append(contigs[0])
        cur_node = contigs[0] + str(i)
        if prev_node is None:
            prev_node = contigs[0] + str(i)
            links = contigs[2][5:]
            links_list.append(links)
        else:
            dot.edge(prev_node, cur_node, label=links, len='2.00')
            prev_node = contigs[0] + str(i)
            if len(contigs) >= 3:
                links = contigs[2][5:]
                links_list.append(links)
        i += 1
    print(dot.source)

    dot.render(key, view=False)
    doc = minidom.parse(key + '.svg')
    print(doc)
    x_pos = [float(ellipse.getAttribute("cx")) for ellipse in doc.getElementsByTagName('ellipse')]
    y_pos = [float(ellipse.getAttribute("cy")) * -1 for ellipse in doc.getElementsByTagName('ellipse')]
    node_strings = [str(text.firstChild.nodeValue) for text in doc.getElementsByTagName('text')]
    x_text = [float(text.getAttribute('x')) - 10 for text in doc.getElementsByTagName('text')]
    y_text = [(float(text.getAttribute('y')) - 10) * -1 for text in doc.getElementsByTagName('text')]
    polygon = [pts.getAttribute('points') for pts in doc.getElementsByTagName('polygon')]


    output_file(key + '.html')
    print(polygon)
