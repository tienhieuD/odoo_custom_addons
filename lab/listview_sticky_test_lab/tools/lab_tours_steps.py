# Tour steps shared by all versions: (trigger, run) with `run` as JavaScript source.
NOOP = "() => { void 0; }"

WIDE = r'''async function () {
            try {
                var root = document.querySelector(".o_list_view");
                var cols = root.querySelectorAll("thead th[data-name]").length;
                check(cols >= 50, "expected >= 50 columns, got " + cols);
                await pinAndScroll(root, "category_id", "wide(cat)");
                // pin a column further right, then unpin by clicking again
                await pinAndScroll(root, "amount", "wide(amount)");
                root.querySelector("thead th[data-name=amount] .js_pin_this_column").click();
                await sleep(400);
                check(!document.head.querySelector(STYLE), "wide: style not removed on unpin");
                // pin again, then change the search panel (when the version has one): the pin must survive the reload
                root.querySelector("thead th[data-name=state] .js_pin_this_column").click();
                await sleep(700);
                var values = document.querySelectorAll(".o_search_panel_category_value header");
                var box = document.querySelector(".o_search_panel_filter_value input");
                var target = values.length > 1 ? values[1] : box;
                if (target) {
                    target.click();
                    await sleep(1500);
                    var root2 = document.querySelector(".o_list_view");
                    check(document.head.querySelector(STYLE), "wide: pin lost after search panel reload");
                    check(getComputedStyle(root2.querySelector("thead th:nth-child(3)")).position === "sticky", "wide: col not sticky after reload");
                }
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        }'''

EDITABLE = r'''async function () {
            try {
                var root = document.querySelector(".o_list_view");
                await pinAndScroll(root, "partner_id", "editable(partner)");
                // enter edit mode on a row: pinned columns must stay aligned
                root.querySelector("tbody tr.o_data_row td:nth-child(3)").click();
                await sleep(800);
                check(root.querySelector("tbody tr.o_selected_row"), "editable: row did not enter edit mode");
                var th = root.querySelector("thead th[data-name=partner_id]");
                check(getComputedStyle(th).position === "sticky", "editable: pin lost while editing");
                var sc = scroller(tableOf(root));
                sc.scrollLeft = 700;
                await sleep(300);
                var row = root.querySelector("tbody tr.o_selected_row");
                var rel = function (el) { return el.getBoundingClientRect().left - sc.getBoundingClientRect().left; };
                var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
                check(Math.abs(rel(row.children[idx]) - rel(th)) < 3, "editable: edited row pinned cell misaligned: cell " + rel(row.children[idx]) + " th " + rel(th) + " idx " + idx + " cells " + row.children.length + " pos " + getComputedStyle(row.children[idx]).position + " rowclass " + row.className);
                sc.scrollLeft = 0;
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        }'''

FORM = r'''async function () {
            try {
                var form = document.querySelector(".o_form_view");
                var medium = form.querySelector(".o_field_widget[name=line_medium_ids]");
                var small = form.querySelector(".o_field_widget[name=line_small_ids]");
                check(small && medium, "form: x2many fields missing");
                check(small.querySelectorAll("thead th[data-name]").length >= 5, "form: small list columns");
                // pin in the medium list only
                medium.querySelector("thead th[data-name=product] .js_pin_this_column").click();
                await sleep(900);
                var owners = {};
                Array.prototype.forEach.call(document.head.querySelectorAll(STYLE), function (s) { owners[s.getAttribute("data-owner")] = 1; });
                check(Object.keys(owners).length === 1, "form: expected 1 owner style, got " + Object.keys(owners).length);
                check(getComputedStyle(small.querySelector("thead th:nth-child(2)")).position !== "sticky", "form: pin leaked into the small list");
                check(getComputedStyle(medium.querySelector("thead th:nth-child(3)")).position === "sticky", "form: medium col not sticky");
                // the medium list is wide: scroll horizontally inside it and check the pinned column stays at the left edge
                var mscroll = scroller(tableOf(medium));
                check(mscroll.scrollWidth > mscroll.clientWidth, "form: medium list should overflow horizontally (scrollWidth " + mscroll.scrollWidth + " vs " + mscroll.clientWidth + ")");
                mscroll.scrollLeft = 600;
                await sleep(300);
                var first = medium.querySelector("thead th:nth-child(1)");
                var pth = medium.querySelector("thead th:nth-child(3)");
                var left = pth.getBoundingClientRect().left - mscroll.getBoundingClientRect().left;
                var expected = first.getBoundingClientRect().width + medium.querySelector("thead th:nth-child(2)").getBoundingClientRect().width;
                check(Math.abs(left - expected) < 3, "form: pinned medium col at " + left + " instead of " + expected);
                mscroll.scrollLeft = 0;
            } catch (e) { fail(e.message + " " + e.stack); }
            document.body.classList.add("lab_done");
        }'''

TOURS = [
    ("lshc_lab_wide_list", [
        (".o_list_view .o_data_row", NOOP),
        (".o_list_view thead th[data-name=category_id]:has(.js_pin_this_column)", WIDE),
        ("body.lab_done", NOOP),
    ]),
    ("lshc_lab_editable_list", [
        (".o_list_view .o_data_row", NOOP),
        (".o_list_view thead th[data-name=partner_id]:has(.js_pin_this_column)", EDITABLE),
        ("body.lab_done", NOOP),
    ]),
    ("lshc_lab_form_lists", [
        (".o_list_view .o_data_row td:nth-child(3)", '"click"'),
        (".o_form_view .o_notebook", NOOP),
        (".o_form_view .o_field_widget[name=line_medium_ids] thead th[data-name=product]:has(.js_pin_this_column)", FORM),
        ("body.lab_done", NOOP),
    ]),
]
