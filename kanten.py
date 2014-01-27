import urwid
import IPython
import pudb
DEBUG = False

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

width=40
height=10

def trim(t, d, w=width):
    """Trim the text in `t` to only `d` lines, assuming a width of `w`"""
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
        return urwid.LineBox(urwid.Text(pre_rendered_text[next_start:]))

    print "trimming to '%d' lines", d
    pre_rendered_text = t.text
    lines = t.render((w,)).text
    t.set_text(''.join(lines[:d]))
    # now make a new text widget to hold the remaining lines. It will
    # be added to the next pile, which we will also initialize here
    next_start = pre_rendered_text.find(lines[d].strip())
    return urwid.Text(pre_rendered_text[next_start:])

def h(e):
    return e.rows((width,))

piles = []
p = urwid.Pile([])
for t in txts[:]:
    #if 'she would not qualify' in t.text: pu.db
    p.contents.append((t, p.options()))
    t_size = t.rows((width,))
    if piles:
        #pu.db
        aaa = h(piles[-1])
        #if aaa > height: pu.db
    while h(p) > height:
        # Add a new pile, and send the trimmings in there
        piles.append(p)
        d = h(t) - (h(p) - height)

        #if d <= 0: pu.db
        # start the next column
        p_new = urwid.Pile([])
        print "t is ", h(t)
        t_extra = trim(t, d, width)
        print "now we got ", p.rows((width,))
        print "t_extra is", h(t_extra)
        p_new.contents.append((t_extra, p.options()))
        p = p_new
        t = t_extra


    #if piles and h(piles[-1]) > height:
    #    # ACK!
    #    break
    if h(p) == height:
        piles.append(p)
        # start the next column
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

for p in piles:
    print h(p)
    for c in p.contents:
        print "\t" , h(c[0])

#IPython.embed()
#pu.db
