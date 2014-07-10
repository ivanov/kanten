#!/usr/bin/env python
from __future__ import print_function

DEBUG = False
# debugging only
if DEBUG:
    import IPython

import os
import sys
import argparse

from collections import defaultdict

import urwid
from urwid import Padding, Text, Pile, ProgressBar

try:
    import pygments
    import pygments.lexers
    have_pygments = True
except ImportError:
    have_pygments = False

__version__ = '0.5.1'

parser = argparse.ArgumentParser(
 description='The enlightened pager: less paging. more content. read widely.')
parser.add_argument('filenames', metavar='f', nargs='*',
                   help='an integer for the accumulator')
parser.add_argument( '-w','--width', dest='width', metavar='N', type=int,
                   default=80,
                   help='the number of character in a column line')
parser.add_argument( '-l','--height', '--lines', dest='height', metavar='N', type=int,
                   default='0',
                   help='the number of lines per column (0 for auto)')
parser.add_argument( '-t','--top', dest='top', metavar='N', type=int,
                   default='4',
                   help='the number of lines to leave blank at the top')
parser.add_argument( '-b','--bottom', dest='bottom', metavar='N', type=int,
                   default='4',
                   help='the number of lines to leave blank at the bottom')
parser.add_argument( '-d','--diff', dest='diff', action='store_true',
        help='start in diff mode (same as :set ft=diff)')
parser.add_argument( '-q','--quick', dest='quick', action='store_true',
        help='quit right away (same as :quit on load)')

args = parser.parse_args()
width= args.width
height = args.height
top = args.top
bottom = args.bottom

top_margin = args.top 
if not args.filenames:
    # XXX: in the future this will be an explanation of how to use kanten
    fname = '__missing_file_name__'
else:
    fname = args.filenames[0]

kanten_default_options = dict(
    filetype='',
    number=False,
    incsearch=False,
    editor=os.environ.get('EDITOR', 'vim'),
    textwidth=width
    )

kanten_options = kanten_default_options.copy()

options_map = {
        'ft':'filetype',
        'nu':'number',
        'is':'incsearch',
        'tw':'textwidth',
        }

# crude "filetype" detection
if os.path.splitext(fname)[-1] in ('.diff', '.patch') or args.diff:
    kanten_options['filetype'] = 'diff'

def opt_name(name):
    "Translate short names to their full equivalents"
    if name in options_map:
        return options_map[name]
    else:
        return name

off_screen = []

k_debug = ('ctrl k', 'backspace')
k_next = (' ', 'f', 'z', 'l',  'ctrl f', 'ctrl v', 'right', 'down', 'page down')
k_prev = ('b', 'B', 'w', 'ctrl b', 'left', 'up', 'page up')
k_next_one = ('j', 'ctrl y')
k_prev_one = ('k', 'ctrl e')
k_top = ('g', '<', 'p', 'home')
k_end = ('G', '>', 'end')
k_info = ('ctrl g', '=')
k_search = ('/',)
k_search_bw = ('?',)
k_next_search = ('n',)
k_prev_search = ('N',)
k_toggle_pbar = ('t',)
k_command = (':',)
k_submit = ('enter',)
k_escape = ('esc',)
k_quit = ('q', 'Q')
# not sure if 'h' not being mapped to 'left' is a good idea
k_help = ('h', 'H', 'f1') 
k_version = ('V',)
k_diff = ('d',)     # enable diff highlighting
k_diff_off = ('D',) # disable diff highlighting
k_editor = ('v',) # launch the $EDITOR
m_scroll_up = (4,)   # scroll up
m_scroll_down = (5,) # launch the $EDITOR
m_paste = (2,) # launch the $EDITOR
m_click = (1,) # launch the $EDITOR

c = lambda x: cmd_line_text.set_caption(x)
#c = lambda x: cmd_line_prompt.set_text(x)
e = lambda x: cmd_line_text.set_edit_text(x)

def help_egg():
    from struct import pack
    magic_number = 0x789ced92bf4ec33010c6773fc575ea52f51d40426a25a8d83abbf125364dce51ecb40a4fcf7776a940626361608892dc9feff3fdce3beec715ed49981da538f029ba65bbdd9addd3f3eb8a0e31d3db9c325959346376a8dfd012673a4bbc7e6d8cc21bf2481b73f42c485d6dd24ae97842050d73e3efffd95ba11c9d5d8c6a5c10522568dd9cd6a98851108d406b318f732635cd9e13135a13d989a92bcefbf5806456a3c47d4b36a57962670ee5946d1087920b5303e30e36c34283062d9e38b220348f2a4d2ec6299932290d4ca12de33656aa49cbdc07e9507615f3a0b2f8243b8e1337c1662ed527d692f58469dd5da9e3acb610c874b2cd99a214c3ae961da3ac73e91e7bb60933d577e530b0296e0a00227d689100e0cf79c029fa82f9862b99970551c718ceb1340c2e3c2440a78b9590bcb6a8bdb7ef5cd8ea169662a050725da28eabb2411237208a759deb126c46ba5c8e7207f4e07d3873c55c57eab01ab06823fafe22d0ff8b5ab97ec3baf92dd7cd0f1f31fa0fb5ec843e
    # yes it is! it's a magic number! 3-6-9, 12-15-18, 21-24-27, 30!
    egg =  zip(*([iter(format(magic_number, 'x'))] * 2))
    egg = pack('B'*(len(egg)), *[int(''.join(x), 16) for x in egg])
    try:
        import zlib
    except ImportError:
        while True:
            yield "no zlib? I'm afraid no one can help you :\\"
    while True:
        for m in zlib.decompress(egg).split('\n'):
            yield m
help = help_egg()

exit_font = urwid.font.HalfBlock7x7Font

def display_version(args=None):
    ver = urwid.BigText(('ver'," kanten v" + __version__), exit_font())
    ver = urwid.Overlay(ver, loop.widget, 'center', 'pack', 'middle', 'pack',)
    loop.widget= exit
    return True

def display_help(args=None):
    c(help.next())
    #exit = urwid.BigText(('exit'," kanten v" + __version__), exit_font())
    exit = urwid.BigText(('exit'," kanten v" + str(max_height)), exit_font())
    #exit = urwid.Pile([exit, ])
    #exit = urwid.Padding(exit,('relative', 100), width, left=2, right=2 )
    exit = urwid.Overlay(exit, loop.widget, 'center', 'pack', ('relative',90), 'pack',
            min_height=15)
                #min_width=20, min_height=5)
    # TODO: maybe do some overlay later - inserting into col content is pretty
    # good for now
    #cols.contents.insert(0, exit)
    loop.widget= exit
    return True

def quit(args=None):
    if args and ('!' in args[0] or 'a' in args[0]):
        print("\nold habits die hard! ;)")
    raise urwid.ExitMainLoop()

def edit(args):
    if len(args) > 1:
        e( "NotImplemented: can't open other files yet")
    else:
        return info(args)

def info(args):
    show_or_exit('ctrl g')
    return True

def cmd_not_found(args):
    e('not a kanten command: ' + ' '.join(args))

def set_cmd(args):
    """
    Set various aspects about how kanten behaves. A lot of the syntax and
    semantics are borrowed from Vim's `:help set`

    :se[t]              Show all options that differ from their default values
    :se[t] all          Show all options that differ from their default values

    :se[t] {option}     Toggle option: set, switch it on.
                        Number option: show value.
                        String option: show value.

    :se[t] no{option}   Toggle option: Reset, switch it off.

    :se[t] {option}!    Toggle option: Invert value.
    :se[t] inv{option}  Toggle option: Invert value.
    
    :se[t] {opt}={val}  Set string or number option {opt} to {val}.
    :se[t] {opt}:{val}  Set string or number option {opt} to {val}.

    :se[t] all          Reset all options to their default kanten values
    :se[t] all&less     Reset all options to emulate `less`
    :se[t] all&more     Reset all options to emulate `more`

    The {option} arguments to ":set" may be repeated.  For example:
            :set ft=diff nu
    """
    if len(args) == 1:
        ret =''
        for key,val in kanten_options.items():
            # skip entries which are default values
            #if val == kanten_default_options[key]:
            #    continue
            if val not in (True, False):
                ret += key + '=' + str(val)
            else:
                ret += key if val else 'no' + key
            ret+="    "
        c(ret)
    for arg in args[1:]:
        invert, negate = False, False
        idx = arg.find('=')
        idx2 = arg.find(':')
        if idx < 0 and idx2 < 0 :
            if arg.startswith('inv'):
                arg = arg[3:]
                invert = True
            if arg.startswith('no'):
                arg = arg[2:]
                negate = True
            arg = opt_name(arg)
            val = kanten_options.get(arg, ' unknown option')
            if val not in (True, False):
                msg =  '  ' + arg+ '=' + str(val)
            else:
                # set it
                val = not val if invert else True
                val = False if negate else val
                kanten_options[arg] = val
                msg = arg if val else 'no' + arg
                msg = ':set ' + msg
            c(msg)
            continue
        if idx > 0 and idx2 > 0:
            chomp = min(idx, idx2)
        else: # only one of the args is non-negative
            chomp = max(idx, idx2)
        lhs,rhs = arg[:chomp],arg[chomp+1:]
        arg = opt_name(lhs)
        if kanten_options[arg] in (True, False):
            c("Cannot assign, use 'set %s', 'set no%s'" % (arg, arg))
        else:
            kanten_options[arg] = rhs
            #XXX: turning into spaghetti code here, but what can you do?
            #   - make a callback (reactive) options dictionary?
            if arg == 'filetype' and rhs == 'diff':
                rehighlight(txts, '', search=search_diff)
            elif arg == 'filetype':
                #XXX: add pygments-based highlighting here for other files
                rehighlight(txts, '', search=search_noop)
    return True # by returning True, the cmd_line_text won't get reset to ''

def search_replace(args):
    pass

# All dispatch commands should return True only if the rest of the
# show_or_exit method should be skipped after they are performed.
colon_dispatch_defaults = {
        'help'  : display_help,
        'quit'  : quit,
        'q'     : quit,
        'q!'    : quit,
        'qa'    : quit, # old habits die hard
        'qa!'   : quit, # old habits die hard
        'exit'  : quit,
        'e'     : edit,
        'edit'  : edit,
        'f'     : edit,
        'file'  : edit,
        'set'   : set_cmd,
        'se '   : set_cmd,
        's'     : search_replace,
        }
colon_dispatch = defaultdict(lambda: cmd_not_found, colon_dispatch_defaults)
        

def colon(cmd):
    #c('would have run' + cmd)
    args = cmd.split()
    if args: # :<enter> will give a blank line as a cmd
        return colon_dispatch[args[0].lower()](args)

do_cmd = colon

def page_back():
    pass


def show_or_exit(key):
    global off_screen
    global last_key
    global show
    global do_cmd
    # clear out old messages
    txt = ''

    # set the progress bar visibility, so info can set it just once
    pbh.send(show)

    if isinstance(loop.widget, urwid.Overlay):
        loop.widget = loop.widget[0] # pop off the overlay
    if key != '.':
        last_key = key
    else:
        key = last_key
    if key in k_quit:
        raise urwid.ExitMainLoop()
    elif key in k_help:
        display_help()
        return True
    elif key in k_version:
        #display_version()
        display_help()
        return True
    elif key in k_prev_one:
        #off_screen.append(cols.contents.pop())
        if off_screen:
            new_first = off_screen.pop()
            cols.contents.insert(0, new_first)
            cols.focus_position=0
    elif key in k_prev:
        #off_screen.append(cols.contents.pop())
        for x in range(displayed_columns):
            if off_screen:
                new_first = off_screen.pop()
                cols.contents.insert(0, new_first)
                cols.focus_position=0
    elif key in k_top:
        # take it from the top
        cols.contents = off_screen + cols.contents
        off_screen = []
        cols.focus_position=0
    elif key in k_end:
        # this is the end, my friends, the end, the end.
        off_screen.extend(cols.contents)
        # backfill here properly - fill the hole screen (add back as many columns as can be displayed)
        cols.contents = [off_screen.pop() for x in range(displayed_columns) ][::-1]
        txt = '(END)'
    elif key in k_next_one:
        if len(cols.contents) > displayed_columns:
            off_screen.append(cols.contents.pop(0))
        if len(cols.contents) == displayed_columns:
            txt = '(END)'
    elif key in k_next:
        for x in range(displayed_columns):
            if len(cols.contents) > displayed_columns:
                off_screen.append(cols.contents.pop(0))
        if len(cols.contents) == displayed_columns:
            txt = '(END)'
    elif key in k_search:
        #cmd_line_text.focus()
        all.set_focus('footer')
        txt = '/'
        do_cmd = lambda x: rehighlight(txts, x)
        cmd_line_text.set_edit_text('')
    elif key in k_search_bw:
        #cmd_line_text.focus()
        all.set_focus('footer')
        txt = '?'
        do_cmd = lambda x: rehighlight(txts, x)
        cmd_line_text.set_edit_text('')
    elif key in k_command:
        #txt = ':'
        c(':')
        all.set_focus('footer')
        #cmd_line_text.set_edit_text('')
        do_cmd = colon
        return
    elif key in k_submit:
        if all.get_focus() == 'footer':
            input = cmd_line_text.get_edit_text()
            cmd_line_text.set_edit_text('');
            all.set_focus('body')
            if do_cmd(input):
                # colon_dispatch methods return true if the rest of the method
                # should be skipped (because colon_dispatch method also calls
                # it, for example) 
                return
    elif key in k_escape:
        if all.get_focus() == 'footer':
            txt = ''
            all.set_focus('body')
    elif key in k_next_search:
        # focus pane with a next result only if found
        # pseudocode:
        #   if current pane contains a matched element:
        #       go to the next pane that contains an element (or highlight the
        #       next match?)
        #
        pass
    elif key in k_prev_search:
        # focus last result only if found
        pass
    elif key in k_diff:
        rehighlight(txts, '', search=search_diff)
    elif key in k_diff_off:
        rehighlight(txts, '', search=search_noop)
    elif key in k_info:
        txt = fname
        if kanten_options['filetype']:
            txt += " (ft=" + kanten_options['filetype'] + ")"
        txt += " (%d / %d)" % (total_cols-len(cols.contents) +
                displayed_columns , total_cols)
        if len(cols.contents) == displayed_columns:
            txt += ' (END)'
        pbh.send(True)
    elif key in k_toggle_pbar:
        show = not show
        pbh.send(show)
    elif key in k_editor:
        editor = kanten_options['editor']
        os.spawnvp(os.P_WAIT, editor, [editor, fname])
    elif isinstance(key, tuple) and key[0] == "mouse press":
        if key[1] in  m_scroll_up:
            show_or_exit(k_next[0])
        elif key[1] in m_scroll_down: 
            show_or_exit(k_prev[0])
        elif key[1] in m_click: 
            column = xpos_to_col(key[-2])


            txt = "click in column %d, line %d" % (column, key[-1])
        elif key[1] in m_paste:
            txt = "we would paste X11 clipboard contents here"
        else:
            txt = "unhandled key " + str(key)
    elif key in k_debug:
        if DEBUG:
            IPython.embed_kernel()
    elif isinstance(key, tuple):
        txt = "unhandled key " + str(key)
    else:
        txt = "unhandled key " + str(key)
    cmd_line_text.set_caption(txt)
    #cmd_line_text.set_edit_text(txt)
    pbar.set_completion(len(off_screen)+displayed_columns)
    cmd_line_text.set_edit_text('') 

show = True
def progress_bar_handler():
    """Progress bar coroutine. Send it whether or not you want to show the
    progress bar. 

    XXX: despite good intentions, I think I overengineered this bit. It could
    probably just be a function - I originally was trying to do some timing
    stuff in here, but ended up ripping out before making the commit
    """
    show = (yield)
    while True:
        if not len(p.body):
            p.body.append(pbar)
        if not show:
            if len(p.body):
                p.body.pop()
        show = (yield)

pbh = progress_bar_handler()
pbh.next()

# XXX: implement buffering here, don't read the whole file / piped message
if not sys.stdin.isatty():
    # read from a pipe
    text = sys.stdin.read()
    import os
    sys.stdin.close()
    # reopen stdin now that we've read from the pipe
    sys.__stdin__ = sys.stdin = open('/dev/tty')
    os.dup2(sys.stdin.fileno(), 0)
    fname = 'STDIN'
    # XXX: try to guess about the input using pygments
    if have_pygments:
        # since pygments' detection can be terrible, no point in giving it the
        # whole file.
        lexer = pygments.lexers.guess_lexer(text[:80])
        # the lexer guesser sucks and will say anything it's confused about is
        # Prolog? No.
        if lexer.name == "Prolog":
            lexer = pygments.lexers.TextLexer # null / noop lexer

else:
    if fname == "__missing_file_name__":
        sys.stderr.write('Missing filename ("kanten --help" for help)\n')
        sys.exit(1)
    with open(fname) as f:
        text = f.read()

    if have_pygments:
        try:
            lexer = pygments.lexers.get_lexer_for_filename(fname)
        except pygments.util.ClassNotFound:
            # TODO: if ipynb, treat it as json
            # lexer = pygments.lexers.web.JsonLexer #XXX placeholder
            lexer = pygments.lexers.TextLexer # null / noop lexer

screen =  screen = urwid.raw_display.Screen()
max_width, max_height = screen.get_cols_rows()

max_height = max_height- top - bottom
height = min(max_height, height) if height > 0 else max_height

def make_text(t):
    result = Padding(Text(t, align='left'), ('relative', 100), width, left=2,
            right=2)
    if DEBUG:
        return urwid.LineBox(result)
    return result

#txt = urwid.Text(text)
#text =  text.replace("\n","\n\n")
def search(text, word):
    txts = text.split(word)
    f = lambda x: ('important', word)
    res = list(f((yield t)) for t in txts)
    
    #res = [t for stub in txts for t in (stub, ('important', word))]
    # N. B. this approach adds a superflous trailing match
    return res[:-1]

def search_diff(text, word=None):
    if text and text[0] == '+':
        return [('diff new', text)]
    elif text and text[0] == '-':
        return [('diff old', text)]
    else:
        return text

def search_noop(text, word):
    return text

def rehighlight(txts, s, search=search):
    [t.original_widget.set_text(search(t.original_widget.text, s)) for t in txts]


#text = [
txts = [make_text(t) for t in text.split('\n')]
#s = search(text, 'all')
#txts = [make_text(list(t)) for t in zip(s[::3], s[1::3], s[2::3])]
#[t.original_widget.set_text(search(t.original_widget.text, 'all')) for t in txts]
#rehighlight(txts,'all')
#if DEBUG:
#    # my brain finds it easier to deal with boxes
#    txts = [urwid.LineBox(t) for t in txts]


def trim(t, d, w=width):
    """Trim the text in `t` to only `d` lines, assuming a width of `w`"""
    if DEBUG:
        pre_rendered_text = t.original_widget.original_widget.text
        lines = t.original_widget.original_widget.render((width-2,)).text
        # now make a new text widget to hold the remaining lines. It will
        # be added to the next pile, which we will also initialize here
        if d >= len(lines):
            # happens because we clip the text, and not the linebox
            next_start = 0
        else:
            next_start = pre_rendered_text.find(lines[d].strip())
        t.original_widget.original_widget.set_text(pre_rendered_text[:next_start])
        return make_text(pre_rendered_text[next_start:])

    pre_rendered_text = t.original_widget.text
    lines = t.render((w,)).text

    # now make a new text widget to hold the remaining lines. It will
    # be added to the next pile, which we will also initialize here
    next_start = pre_rendered_text.find(lines[d].strip())
    t.original_widget.set_text(pre_rendered_text[:next_start])
    return make_text(pre_rendered_text[next_start:])

def h(e):
    return e.rows((width,))

piles = []
p = Pile([])
for t in txts[:]:
    #if 'What emerges' in t.text: pu.db
    p.contents.append((t, p.options()))
    t_size = t.rows((width,))
    #if piles and h(piles[-1]) > height: pu.db
    while h(p) > height:
        # Add a new pile, and send the trimmings in there
        piles.append(p)
        d = h(t) - (h(p) - height)
        
        #if d <= 0: pu.db
        
        # start the next column
        p_new = Pile([])
        t_extra = trim(t, d, width)
        # TODO: include diff status in here, and line numbers
        p_new.contents.append((t_extra, p.options()))
        p = p_new
        t = t_extra


    #if piles and h(piles[-1]) > height:
    #    # ACK!
    #    break
    if h(p) == height:
        piles.append(p)
        # start the next column
        p = Pile([])

# all done, don't forget the last pile which we haven't added to the list yet
piles.append(p)

palette = [
    (None,  'light gray', 'black'),
    ('heading', 'black', 'light gray'),
    ('important', 'black', 'light cyan'),
    ('line', 'black', 'light gray'),
    ('options', 'dark gray', 'black'),
    ('focus heading', 'white', 'dark red'),
    ('focus line', 'black', 'dark red'),
    ('diff old', 'dark red', 'black'),
    ('diff new', 'dark green', 'black'),
    ('focus options', 'black', 'light gray'),
    ('pg normal',    'white',      'black', 'standout'),
    ('pg complete',  'white',      'dark magenta'),
    ('selected', 'white', 'dark blue')]

#piles = urwid.ListBox(urwid.SimpleFocusListWalker(piles))
#cols = piles
#fill = cols
cols = urwid.Columns(piles, dividechars=1, min_width=width)

# XXX: I need to subclass columns, and make it so the keypress function
# "rolls" the piles under the hood, and re-renders all the widgets.
#
# self.contents.append(self.contents.pop(0))
#
#cols.box_columns.extend(cols.widget_list)


#grid = urwid.GridFlow(txts, cell_width=20, h_sep=4, v_sep=0, align='left')
fill = urwid.Filler(cols, 'top', top=top_margin)
total_cols = len(cols.contents)
col_widths = cols.column_widths(screen.get_cols_rows())
displayed_columns = len( col_widths )

# XXX: this is not the full story, it ignores the borders between columns
c_columns = map(lambda i: sum(col_widths[:i+1]), range(displayed_columns))
border = (max_width - c_columns[-1]) /  displayed_columns
def xpos_to_col(pos):
    for i,c in enumerate(c_columns):
        if pos < (c + i * border):
            return i

pbar = ProgressBar('pg normal', 'pg complete', displayed_columns, total_cols)


p = urwid.ListBox(urwid.SimpleListWalker([pbar]))

all = Pile([ fill, (1, p), ]) 
cmd_line_text = urwid.Edit(fname)
#cmd_line_prompt = urwid.Text('hi there')
#cmd_line_combined = urwid.Filler([cmd_line_prompt, cmd_line_text])
#all = urwid.Frame(body=all, footer=cmd_line_combined)
all = urwid.Frame(body=all, footer=cmd_line_text)
loop = urwid.MainLoop(all, palette, screen, unhandled_input=show_or_exit)
loop.exit = urwid.Text(" Help? ")

#IPython.embed()
if args.diff:
    set_cmd("set ft=diff".split())
elif have_pygments:
    set_cmd(("set ft=" + lexer.name.split()[0].lower()).split())

if args.quick:
    loop.set_alarm_in(0, lambda x,y:  quit())

loop.run()

import IPython
too_high = 0
for p in piles:
    if h(p) > max_height:
        too_high += 1

#if too_high:
#    IPython.embed(header="There were %d violations of max_height" % too_high)

if DEBUG:
    for p in piles:
        print(h(p))
        for c in p.contents:
            print("\t" , h(c[0]))

#print [type(t.original_widget.text) for t in txts]
#print [(t.original_widget.get_text()[1]) for t in txts[0:100]]
f = lambda t:t.original_widget.get_text()[1]
g = lambda t:len(f(t))
#print [f(t) for t in txts[:] if g(t)>0]


#IPython.embed()
#pu.db
