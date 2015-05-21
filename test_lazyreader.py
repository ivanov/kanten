import nose.tools as nt

def long_generator():
    for x in range(200):
        yield "Repetition is the death of the soul"

def test_lazyload():
    # for this to work, read and read_from_pipe need to return a proxy object
    # which will yield lines on demand
  
    from kanten import LazyReader

    text = LazyReader(long_generator())

    assert text[1]== "Repetition is the death of the soul"
    assert text[2]== "Repetition is the death of the soul"
    #nt.assert_raises(IndexError, lambda: text[200])
    text[-1]
    text[1:2]
    assert len(text) == 200

def test_first_paint():
    # also, lazy reading requires the front-end code to not ask for more lines
    # than it needs to paint the first bit of text

    from kanten import first_paint


    # let's do a file-reading proxy first
