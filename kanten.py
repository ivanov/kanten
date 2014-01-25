import urwid

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    #txt.set_text(repr(key))

fname = '/home/pi/fortunes/antoine_de_saintexupery'
with open(fname) as f:
    text = f.read()

txt = urwid.Text(text)
pile  = urwid.Pile([txt])

cols = urwid.Columns([pile, pile, pile])
fill = urwid.Filler(cols, 'top')
loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)
loop.run()


