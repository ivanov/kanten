import urwid
import IPython
import pudb
DEBUG = True

off_screen = []
def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    elif key in ('b', 'B'):
        #off_screen.append(cols.contents.pop())
        if off_screen:
            new_first = off_screen.pop()
            cols.contents.insert(0, new_first)
            cols.focus_position=0
    elif key in ('g'):
        # take it from the top
        cols.contents = off_screen + cols.contents
        cols.focus_position=0
    elif key in ('G'):
        # this is the end, my friends, the end, the end.
        off_screen.extend(cols.contents)
        # XXX: backfill here properly - fill the hole screen
        cols.contents = [ off_screen.pop() ]
    elif key in (' '):
        if cols.contents:
            off_screen.append(cols.contents.pop(0))
    #txt.set_text(repr(key))

fname = '/home/pi/fortunes/antoine_de_saintexupery'
fname = '/home/pi/cur/das.txt'
fname = '/home/pi/cur/eb.txt'
with open(fname) as f:
    text = f.read()

txt = urwid.Text(text)
txts = [urwid.Text(t) for t in text.split('\n')]
if DEBUG:
    # my brain finds it easier to deal with boxes
    txts = [urwid.LineBox(t) for t in txts]
pile  = urwid.Pile(txts)

# what I really want here is a transpose of the GridFlow widget
# GridFlow widgets arrange their cells like so:
#
# [  cell[0]  cell[3] ]
# [  cell[1]  cell[4] ]
# [  cell[2]  cell[5] ]
#

width=40
height=10
piles = []
p = urwid.Pile([])
for t in txts:
    t_size = t.rows((width,))
    p_size = p.rows((width,))
    if p_size >= height:
        # shortcut this one, just add a new pile and toss ourselves in there
        piles.append(p)
        # start the next column
        p = urwid.Pile([])
        p_size = p.rows((width,))
    if t_size + p_size > height:
        # need to cut t_size so that it fits within height
        #p = urwid.AttrMap(p, None, focus_map='reversed') 
        #p = urwid.Padding(p, width=('relative', 30))
        d = height - p_size
        t0 = t
        if DEBUG:
            pre_rendered_text = t.original_widget.text
            lines = t.original_widget.render((width,)).text
            t.original_widget.set_text(''.join(lines[:d]))
            # now make a new text widget to hold the remaining lines. It will
            # be added to the next pile, which we will also initialize here
            if d >= len(lines):
                # happens because we clip the text, and not the linebox 
                next_start = 0
            else:
                next_start = pre_rendered_text.find(lines[d].strip())
            t = urwid.LineBox(urwid.Text(pre_rendered_text[next_start:]))
        else:
            pre_rendered_text = t.text
            lines = t.render((width,)).text
            t.set_text(''.join(lines[:d]))
            # now make a new text widget to hold the remaining lines. It will
            # be added to the next pile, which we will also initialize here
            next_start = pre_rendered_text.find(lines[d].strip())
            t = urwid.Text(pre_rendered_text[next_start:])
        
        p.contents.append((t0, p.options()))
        
        piles.append(p)
        # start the next column
        p = urwid.Pile([])
    p.contents.append((t, p.options()))

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
cols = urwid.Columns(piles, dividechars=10, min_width=width)

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

#IPython.embed()
#pu.db
