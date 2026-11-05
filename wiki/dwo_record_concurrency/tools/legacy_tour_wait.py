"""usage: legacy_tour_wait.py <module dir> -- deterministic wait for the legacy tours (a step trigger may be a function)"""
import sys
p = sys.argv[1] + '/static/tests/tours/concurrency_tour.js'
s = open(p).read()
old_start = s.index("function openAndEdit(value) {")
old_end = s.index("tour.register('dwo_concurrency_conflict'") if "tour.register('dwo_concurrency_conflict'" in s else None
new = '''// the snapshot of the loaded record is fetched in two round trips: wait for it before the "other user" writes.
// (a promise returned by a step is not waited for, so the wait is a visible marker added after a delay)
function openAndEdit(value) {
    return [
        {trigger: ".o_form_button_edit", run: "click"},
        {trigger: NAME, run: function () {
            $('.dwo_wait_done').remove();
            setTimeout(function () { $('body').append('<div class="dwo_wait_done" style="width:2px;height:2px;overflow:hidden">.</div>'); }, 2000);
        }},
        {trigger: ".dwo_wait_done"},
        {trigger: NAME, run: "text " + value},
    ];
}

'''
s = s[:old_start] + new + s[old_end:]
open(p, 'w').write(s)
