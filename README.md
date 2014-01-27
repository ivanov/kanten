kanten
======
Japanese for word for agar, a gelatinous substance derived from seaweed.

This program was inspired by a similar one called [Tofu][] for OS X, a
column-based reader application, where the columns are arranged horizontally.
Given the aspect ratio of computer monitors, I decided to create kanten to be a
unix pager replacement (more and less) that is not limited to 80 columns.


TODO
----
[x] horizontal progress bar indicator
[ ] figure out how many columns are displayed, and adjust pbar accordingly
[ ] don't make the last displayed columns dissappear at the end?
[ ] (n / m) total pages (columns) indicator
[x] some vertical empty space at the top
[x] space bar should move one column over (or whole screen?)
[ ] reading from stdin
[ ] configurable number of columns
[x] reflow of text
[ ] (maybe) reading cursor (like dictator?)
[x] 'g' to go to the beginning 
[x] 'G' to go to the end
[x] split boxes so that they partially fit
[x] clip off lines that are too long even in one go
[x] last line of text being cut-off
[x] fix formatting (spacing) for cells which were cut
[x] columns currently allowed to expand: don't let them 
    - boxadapter?
    - options('given', width) ?
    - use padding!!
[ ] (alignment) 'the less is' line currently getting screwed up :\
[ ] (refactor) start off with one Padding(text) and keep splitting in
    - don't pre-split
    - such an approach will be a reasonable way to go with searching, anyway
        - i.e. highlight the word in every instance, and reflow?
        - or at least to find the location of the word, and then index into the
          right / approximate column
[ ] search using / (to seek around)
[ ] wrap-around optionally
[x] going forward 4 times and then going back 4 doesn't work :(
    maybe related:
        File "/usr/lib/python2.7/dist-packages/urwid/widget.py", line 142, in cached_render validate_size(self, size, canv)
        File "/usr/lib/python2.7/dist-packages/urwid/widget.py", line 112, in validate_size canv.rows(), size))
        urwid.widget.WidgetError: Widget <Filler box widget <Columns box/flow widget> valign='top'> rendered (193 x 45) canvas when passed size (193, 51
    [x] (maybe) try cache invalidation? nope, _invalidate doesn't hel
    [x] [cols.focus_position=0 seems to have done the trick!
