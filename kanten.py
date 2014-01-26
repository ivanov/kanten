import urwid
import IPython
#import pudb

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    #txt.set_text(repr(key))

fname = '/home/pi/fortunes/antoine_de_saintexupery'
fname = '/home/pi/cur/das.txt'
with open(fname) as f:
    text = f.read()

#txt = urwid.Text(text)
txts = [urwid.Text(t) for t in text.split('\n')]
pile  = urwid.Pile(txts)

# what I really want here is a transpose of the GridFlow widget
# GridFlow widgets arrange their cells like so:
#
# [  cell[0]  cell[3] ]
# [  cell[1]  cell[4] ]
# [  cell[2]  cell[5] ]
#

width=40
height=60
piles = []
p = urwid.Pile([])
for t in txts:
    p.contents.append((t, p.options()))
    if p.rows((width,)) > height:
        piles.append(p)
        p = urwid.Pile([])


cols = urwid.Columns(piles, dividechars=10, min_width=width)

# On second thought, this looks like too much internals. All we need to do is
# maintain the window height, and how far down a pile goes. If it's too high,
# go to the next column. The thing is, the GridFlow implementation makes all
# boxes in a row the same height, and that's not what I'm looking for.
#

def pile_height(p):
    pass


#grid = urwid.GridFlow(txts, cell_width=20, h_sep=4, v_sep=0, align='left')
fill = urwid.Filler(cols, 'top')
loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)

loop.run()

IPython.embed()
#pu.db
