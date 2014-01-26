import urwid
import IPython
#import pudb

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    elif key in ('b', 'B'):
        cols.contents.insert(0, cols.contents.pop())
    else:
        cols.contents.append(cols.contents.pop(0))
    #txt.set_text(repr(key))

fname = '/home/pi/fortunes/antoine_de_saintexupery'
fname = '/home/pi/cur/das.txt'
with open(fname) as f:
    text = f.read()

txt = urwid.Text(text)
txts = [urwid.Text(t) for t in text.split('\n')]
#txts = [urwid.LineBox(t) for t in txts]
pile  = urwid.Pile(txts)

# what I really want here is a transpose of the GridFlow widget
# GridFlow widgets arrange their cells like so:
#
# [  cell[0]  cell[3] ]
# [  cell[1]  cell[4] ]
# [  cell[2]  cell[5] ]
#

width=40
height=40
piles = []
p = urwid.Pile([])
for t in txts:
    p.contents.append((t, p.options()))
    if p.rows((width,)) > height:
        #p = urwid.AttrMap(p, None, focus_map='reversed') 
        #p = urwid.Padding(p, width=('relative', 30))
        piles.append(p)
        p = urwid.Pile([])

#palette = [
#    (None,  'light gray', 'white'),
#    ('heading', 'black', 'light gray'),
#    ('line', 'black', 'light gray'),
#    ('options', 'dark gray', 'black'),
#    ('focus heading', 'white', 'dark red'),
#    ('focus line', 'black', 'dark red'),
#    ('focus options', 'black', 'light gray'),
#    ('selected', 'white', 'dark blue')]

#piles = urwid.ListBox(urwid.SimpleFocusListWalker(piles))
#cols = piles
#fill = cols
cols = urwid.Columns(piles, focus_column=2,   dividechars=10, min_width=width)

# XXX: I need to subclass columns, and make it so the keypress function
# "rolls" the piles under the hood, and re-renders all the widgets.
#
# self.contents.append(self.contents.pop(0))
#
#cols.box_columns.extend(cols.widget_list)


#grid = urwid.GridFlow(txts, cell_width=20, h_sep=4, v_sep=0, align='left')
fill = urwid.Filler(cols, 'top')
loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)

loop.run()

IPython.embed()
#pu.db
