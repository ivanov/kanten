from kanten import LazyReader


def long_generator():
    for x in range(200):
        yield x # "Repetition is the death of the soul"


def test_lazyload():
    # for this to work, read and read_from_pipe need to return a proxy object
    # which will yield lines on demand
  
    text = LazyReader(long_generator())

    assert text[1] == 1
    assert text[2] == 2

    assert len(text.cached) == 3

    assert text[-1] == 2
    assert text[1:2] == [1]
    assert text[5:10] == [5, 6, 7, 8, 9]

    text.exhaust()

    assert len(text) == 200

def test_first_paint():
    # also, lazy reading requires the front-end code to not ask for more lines
    # than it needs to paint the first bit of text

    from kanten import first_paint

    first_paint # hush pyflakes


    # let's do a file-reading proxy first
