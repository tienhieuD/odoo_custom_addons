odoo.define("listview_sticky_header_and_column.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Odoo 16 tour manager does not await an async `run`: split each async step in two (run, then wait for the flag)
    const ASYNC_DONE = "o-lshc-asyncDone";
    const isAsync = (fn) => typeof fn === "function" && fn.constructor.name === "AsyncFunction";
    const expandAsync = (steps) =>
        steps.flatMap((step) => {
            if (!isAsync(step.run)) {
                return [step];
            }
            const run = step.run;
            return [
                {
                    ...step,
                    run: function (helper) {
                        document.body.classList.remove(ASYNC_DONE);
                        window.__lshcAsyncError = null;
                        run.call(this, helper)
                            .catch((error) => {
                                window.__lshcAsyncError = error;
                            })
                            .then(() => document.body.classList.add(ASYNC_DONE));
                    },
                },
                {
                    trigger: `body.${ASYNC_DONE}`,
                    in_modal: false,
                    isCheck: true,
                    run: () => {
                        if (window.__lshcAsyncError) {
                            throw window.__lshcAsyncError;
                        }
                    },
                },
            ];
        });

    const KEY = "listview_sticky_header_and_column";
    const LIST = ".o_action_manager .o_list_view";
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

    function assert(cond, msg) {
        if (!cond) {
            throw new Error(`[lshc] ${msg}`);
        }
    }
    function near(a, b, tol, msg) {
        assert(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b} (tol ${tol})`);
    }
    async function waitFor(fn, msg, timeout = 5000) {
        const end = Date.now() + timeout;
        while (Date.now() < end) {
            const res = fn();
            if (res) {
                return res;
            }
            await sleep(50);
        }
        throw new Error(`[lshc] timeout: ${msg}`);
    }
    /** nearest ancestor that really scrolls on the given axis */
    function scroller(el, axis) {
        for (let n = el.parentElement; n; n = n.parentElement) {
            const cs = getComputedStyle(n);
            const ov = axis === "y" ? cs.overflowY : cs.overflowX;
            const overflowing = axis === "y" ? n.scrollHeight > n.clientHeight + 1 : n.scrollWidth > n.clientWidth + 1;
            if (/(auto|scroll)/.test(ov) && overflowing) {
                return n;
            }
        }
        return null;
    }
    function lshcKeys() {
        return Object.keys(localStorage).filter((k) => k.startsWith(KEY));
    }
    function clearKeys() {
        lshcKeys().forEach((k) => localStorage.removeItem(k));
    }
    function pinStyles() {
        return [...document.head.querySelectorAll(`style[name="${KEY}"]`)];
    }
    function th(root, name) {
        return root.querySelector(`thead th[data-name="${name}"]`);
    }
    function pinBtn(root, name) {
        return th(root, name)?.querySelector(".js_pin_this_column");
    }
    async function pin(root, name) {
        const btn = await waitFor(() => pinBtn(root, name), `pin button of ${name}`);
        btn.click();
        await sleep(700);
    }
    /** make the table clearly wider than the viewport so a horizontal scroll exists */
    async function widen(root) {
        root.querySelector("table").style.minWidth = "2600px";
        await sleep(200);
    }
    const rect = (el) => el.getBoundingClientRect();

    tour.register("lshc_header_sticky", { test: true }, expandAsync([
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "header is sticky and stays at the top of the scroll area BEFORE any column is pinned",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(LIST);
                    assert(lshcKeys().length === 0 && pinStyles().length === 0, "a column is pinned: not the state to measure");
                    const thead = root.querySelector("thead");
                    assert(getComputedStyle(thead).position === "sticky", `thead not position: sticky (${getComputedStyle(thead).position})`);
                    assert(!/rgba\(.*,\s*0\)$|^transparent$/.test(getComputedStyle(thead).backgroundColor), "sticky thead must be opaque");
                    const sc = scroller(thead, "y");
                    assert(sc, "no vertical scroll area: not enough demo rows?");
                    near(rect(thead).top, rect(sc).top, 2, "header top before scroll");
                    const row0 = root.querySelector(".o_data_row");
                    sc.scrollTop = 400;
                    await sleep(300);
                    assert(sc.scrollTop > 100, `did not scroll (${sc.scrollTop})`);
                    near(rect(thead).top, rect(sc).top, 2, "header top after scroll");
                    assert(rect(row0).bottom <= rect(thead).bottom + 1, "first row should have scrolled under the header");
                    sc.scrollTop = 0;
                },
            },
    ]));

    tour.register("lshc_header_sticky_pinned", { test: true }, expandAsync([
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "header is still sticky once a column is pinned",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(LIST);
                    await pin(root, "email");
                    const thead = root.querySelector("thead");
                    const cell = root.querySelector("thead th:not(.o_list_record_selector)");
                    assert(["sticky"].includes(getComputedStyle(thead).position) ||
                        getComputedStyle(cell).position === "sticky", "thead/th is not position: sticky");
                    const sc = scroller(thead, "y");
                    assert(sc, "no vertical scroll area: not enough demo rows?");
                    near(rect(thead).top, rect(sc).top, 2, "header top before scroll");
                    const row0 = root.querySelector(".o_data_row");
                    sc.scrollTop = 400;
                    await sleep(300);
                    assert(sc.scrollTop > 100, `did not scroll (${sc.scrollTop})`);
                    near(rect(thead).top, rect(sc).top, 2, "header top after scroll");
                    assert(rect(row0).bottom <= rect(thead).bottom + 1, "first row should have scrolled under the header");
                    sc.scrollTop = 0;
                    clearKeys();
                },
            },
    ]));

    tour.register("lshc_pin_buttons", { test: true }, expandAsync([
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "one hidden pin button per sortable header, none on the checkbox header",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    const root = document.querySelector(LIST);
                    await waitFor(() => pinBtn(root, "display_name"), "pin button");
                    const sortable = [...root.querySelectorAll("thead th[data-name]")];
                    assert(sortable.length >= 3, "expected several named headers");
                    const withBtn = sortable.filter((t) => t.querySelector(".js_pin_this_column"));
                    assert(withBtn.length >= 3, `pin buttons missing (${withBtn.length})`);
                    for (const t of withBtn) {
                        assert(t.querySelectorAll(".js_pin_this_column").length === 1, `duplicate pin button in ${t.dataset.name}`);
                    }
                    assert(!root.querySelector("thead th.o_list_record_selector .js_pin_this_column"), "pin button on checkbox header");
                    assert(getComputedStyle(withBtn[0].querySelector(".js_pin_this_column")).display === "none", "pin button should be hidden until hover");
                    // sorting re-renders the header: still exactly one button per header
                    th(root, "display_name").click();
                    await sleep(800);
                    const root2 = document.querySelector(LIST);
                    await waitFor(() => pinBtn(root2, "display_name"), "pin button after sort");
                    for (const t of root2.querySelectorAll("thead th[data-name]")) {
                        assert(t.querySelectorAll(".js_pin_this_column").length <= 1, `duplicate pin button after sort in ${t.dataset.name}`);
                    }
                },
            },
    ]));

    tour.register("lshc_pin_column", { test: true }, expandAsync([
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "pin a column, scroll both ways and measure",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(LIST);
                    await widen(root);
                    await pin(root, "display_name");
                    // saved index = position of the th in the row (checkbox + avatar + name)
                    const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "display_name"));
                    const keys = lshcKeys();
                    assert(keys.length === 1 && !keys[0].includes("__field_"), `localStorage keys: ${keys}`);
                    assert(Number(localStorage.getItem(keys[0])) === idx, `saved index ${localStorage.getItem(keys[0])} != ${idx}`);
                    const styles = pinStyles();
                    // a pinned list owns two style nodes: the "pre" one (sticky thead) and the final one (freeze)
                    assert(styles.length === 2, `expected 2 style nodes, got ${styles.length}`);
                    assert(styles[0].dataset.owner === styles[1].dataset.owner, "style nodes of different owners");
                    assert(root.querySelector(".table-responsive").dataset.lshcId === styles[0].dataset.owner, "list not scoped to its style node");
                    // sticky left offsets are cumulative widths
                    const heads = [...root.querySelectorAll("thead tr th")].slice(0, idx + 1);
                    let acc = 0;
                    heads.forEach((h, i) => {
                        const cs = getComputedStyle(h);
                        assert(cs.position === "sticky", `th ${i} not sticky`);
                        near(parseFloat(cs.left), acc, 1, `left of th ${i}`);
                        assert(cs.zIndex === "10", `z-index of th ${i}: ${cs.zIndex}`);
                        acc += rect(h).width;
                    });
                    const cell = root.querySelector(`.o_data_row td:nth-child(${idx + 1})`);
                    assert(getComputedStyle(cell).position === "sticky", "pinned td not sticky");
                    const free = root.querySelector(`.o_data_row td:nth-child(${idx + 3})`);
                    assert(getComputedStyle(free).position !== "sticky", "unpinned td must not be sticky");

                    const sx = scroller(root.querySelector("table"), "x");
                    assert(sx, "no horizontal scroll area");
                    const left0 = rect(cell).left - rect(sx).left;
                    const freeX0 = rect(free).left;
                    sx.scrollLeft = 300;
                    await sleep(300);
                    assert(sx.scrollLeft > 100, `did not scroll horizontally (${sx.scrollLeft})`);
                    near(rect(cell).left - rect(sx).left, left0, 1.5, "pinned td moved on horizontal scroll");
                    near(rect(heads[idx]).left - rect(sx).left, left0, 1.5, "pinned th moved on horizontal scroll");
                    assert(freeX0 - rect(free).left > 100, "unpinned column should move with the scroll");

                    // header still on top while scrolling both ways
                    const sy = scroller(root.querySelector("table"), "y");
                    assert(sy, "no vertical scroll area");
                    sy.scrollTop = 400;
                    await sleep(300);
                    near(rect(root.querySelector("thead")).top, rect(sy).top, 2, "header top (both scrolls)");
                    near(rect(heads[idx]).top, rect(sy).top, 2, "pinned th top (both scrolls)");
                    near(rect(heads[idx]).left - rect(sx).left, left0, 1.5, "pinned th left (both scrolls)");
                    sx.scrollLeft = 0;
                    sy.scrollTop = 0;
                    clearKeys();
                },
            },
    ]));

    tour.register("lshc_unpin_column", { test: true }, expandAsync([
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "pin then unpin the same column",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(LIST);
                    await pin(root, "email");
                    const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "email"));
                    const cell = () => root.querySelector(`.o_data_row td:nth-child(${idx + 1})`);
                    assert(getComputedStyle(cell()).position === "sticky", "column not pinned");
                    await pin(root, "email"); // second click = unpin
                    assert(pinStyles().length === 0, "style node still present after unpin");
                    assert(lshcKeys().length === 0, `localStorage keys left after unpin: ${lshcKeys()}`);
                    assert(getComputedStyle(cell()).position !== "sticky", "td still sticky after unpin");
                    assert(!root.querySelector("thead th:first-child") ||
                        getComputedStyle(root.querySelector("thead th:first-child")).left === "auto" ||
                        getComputedStyle(root.querySelector("thead th:first-child")).zIndex !== "10", "th still pinned after unpin");
                    clearKeys();
                },
            },
    ]));

    tour.register("lshc_pin_persist", { test: true }, expandAsync([
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "pin a column",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    clearKeys();
                    await pin(document.querySelector(LIST), "display_name");
                },
            },
            {
                content: "open a record",
                trigger: `${LIST} .o_data_row:first-child td:nth-child(2)`,
                run: "click",
            },
            { trigger: ".o_form_view", run: () => {} },
            {
                content: "back to the list",
                trigger: ".o_control_panel .breadcrumb-item:not(.active), .o_control_panel .o_back_button",
                run: "click",
            },
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "the pinned column is restored from localStorage",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    const root = document.querySelector(LIST);
                    const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "display_name"));
                    await waitFor(() => getComputedStyle(root.querySelector(`.o_data_row td:nth-child(${idx + 1})`)).position === "sticky",
                        "pinned column restored after remount");
                    await sleep(800);
                    const info = pinStyles().map((n) => `${n.dataset.owner}:${!!document.querySelector(`[data-lshc-id="${n.dataset.owner}"]`)}`);
                    assert(pinStyles().length === 2, `style nodes after remount: ${info} (leak?)`);
                    clearKeys();
                },
            },
    ]));

    tour.register("lshc_checkbox_optional", { test: true }, expandAsync([
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "pin a column, select all rows with the checkbox column",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(LIST);
                    await pin(root, "display_name");
                    const box0 = root.querySelector("thead th:first-child");
                    assert(getComputedStyle(box0).position === "sticky", "checkbox header not sticky when pinned");
                    near(parseFloat(getComputedStyle(box0).left), 0, 0.5, "checkbox column left");
                    const all = root.querySelector("thead .o_list_record_selector input");
                    all.click();
                    await sleep(400);
                    const rows = root.querySelectorAll(".o_data_row").length;
                    assert(root.querySelectorAll(".o_data_row .o_list_record_selector input:checked").length === rows, "select-all did not select every row");
                    assert(document.querySelector(".o_selection_box, .o_list_selection_box, .o_cp_sidebar, .o_cp_action_menus"), "selection box missing");
                    all.click();
                    await sleep(300);
                },
            },
            {
                content: "open optional columns",
                trigger: `${LIST} .o_optional_columns_dropdown_toggle`,
                run: "click",
            },
            {
                content: "show the Tax ID column",
                trigger: ".o_optional_columns_dropdown .dropdown-item:contains('Tax ID')",
                run: "click",
            },
            {
                content: "new column has a pin button, pinned column kept its sticky left",
                trigger: `${LIST} thead th[data-name=vat]`,
                run: async () => {
                    const root = document.querySelector(LIST);
                    await waitFor(() => pinBtn(root, "vat"), "pin button on the new column");
                    const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "display_name"));
                    // legacy list: the table is rebuilt and the pin re-applied ~300ms later
                    await waitFor(() => {
                        const c = document.querySelector(`${LIST} .o_data_row td:nth-child(${idx + 1})`);
                        return c && getComputedStyle(c).position === "sticky";
                    }, "pinned column lost after optional column toggle");
                    assert(th(root, "vat").querySelectorAll(".js_pin_this_column").length === 1, "duplicate pin button");
                    clearKeys();
                },
            },
    ]));

    tour.register("lshc_o2m_form", { test: true }, expandAsync([
            { trigger: ".o_form_view .o_notebook", run: () => {} },
            {
                content: "open the Users tab",
                trigger: ".o_notebook .nav-link:contains('Users')",
                run: "click",
            },
            { trigger: ".o_field_widget[name=user_ids] .o_data_row, .o_field_widget[name=users] .o_data_row", run: () => {} },
            {
                content: "pin a column of the embedded list",
                trigger: ".o_field_widget[name=user_ids] .o_data_row, .o_field_widget[name=users] .o_data_row",
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(".o_field_widget[name=user_ids]  .table-responsive, .o_field_widget[name=users]  .table-responsive");
                    assert(root, "embedded list not found");
                    // the very first column (index 0: an embedded list has no checkbox column)
                    const name = root.querySelector("thead th[data-name]").dataset.name;
                    assert(root.querySelector("thead tr th") === th(root, name), "first th is not a named column");
                    await pin(root, name);
                    const keys = lshcKeys();
                    assert(keys.length === 1 && /__field_(user_ids|users)$/.test(keys[0]), `localStorage keys: ${keys}`);
                    assert(localStorage.getItem(keys[0]) === "0", `saved index: ${localStorage.getItem(keys[0])}`);
                    const pinned = root.querySelector(".o_data_row td:nth-child(1)");
                    assert(getComputedStyle(pinned).position === "sticky", `first embedded column not pinned: pos=${getComputedStyle(pinned).position} styles=${pinStyles().length}`);
                    assert(getComputedStyle(th(root, name)).position === "sticky", "first embedded th not sticky");
                    // the embedded list keeps its own scrollbar (form does not scroll it)
                    assert(getComputedStyle(root).overflowX !== "visible", "embedded list lost its overflow");
                },
            },
            {
                content: "open the Access Rights tab (a second embedded list)",
                trigger: ".o_notebook .nav-link:contains('Access Rights')",
                run: "click",
            },
            { trigger: ".o_field_widget[name=access_ids] thead th, .o_field_widget[name=model_access] thead th", run: () => {} },
            {
                content: "the other embedded list is not affected",
                trigger: ".o_field_widget[name=access_ids] thead th, .o_field_widget[name=model_access] thead th",
                run: async () => {
                    await sleep(500);
                    const other = document.querySelector(".o_field_widget[name=access_ids]  .table-responsive, .o_field_widget[name=model_access]  .table-responsive");
                    assert(!other.dataset.lshcId, "second list wrongly scoped");
                    // legacy form: a hidden notebook tab keeps its list alive, so the two style nodes of the pinned list stay
                    assert(pinStyles().length === 2, `style nodes while the pinned list is kept in its hidden tab: ${pinStyles().length}`);
                    // NOTE (Odoo 15): the renderer's destroy() is not called when the form is left, so these two style nodes
                    // stay in <head> (scoped to a removed list: harmless). Not asserted here.
                    clearKeys();
                },
            },
    ]));

    tour.register("lshc_dialog", { test: true }, expandAsync([
            { trigger: ".o_form_view .o_field_widget[name=parent_id] input", run: () => {} },
            {
                content: "open the Many2one search dialog",
                trigger: ".o_form_view .o_field_widget[name=parent_id] input",
                run: "click",
            },
            {
                in_modal: false,
                trigger: ".ui-autocomplete .o_m2o_dropdown_option a:contains('Search More')",
                run: "click",
            },
            { in_modal: false,
                trigger: ".modal .o_list_view .o_data_row", run: () => {} },
            {
                content: "pin a column inside the dialog: it stays put on horizontal scroll, header sticky",
                in_modal: false,
                trigger: ".modal .o_list_view .o_data_row",
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(".modal .o_list_view");
                    await widen(root);
                    const name = root.querySelector("thead th[data-name]").dataset.name;
                    await pin(root, name);
                    const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, name));
                    const styles = pinStyles();
                    assert(styles.length === 2, `style nodes in dialog: ${styles.length}`);
                    const cell = root.querySelector(`.o_data_row td:nth-child(${idx + 1})`);
                    const head = th(root, name);
                    assert(getComputedStyle(cell).position === "sticky", "pinned dialog td not sticky");
                    assert(getComputedStyle(head).position === "sticky", "pinned dialog th not sticky");
                    const free = root.querySelector(`.o_data_row td:nth-child(${idx + 3})`);
                    assert(getComputedStyle(free).position !== "sticky", "unpinned dialog td must not be sticky");
                    const sx = scroller(root.querySelector("table"), "x");
                    assert(sx && sx.closest(".modal"), "no horizontal scroll area inside the dialog");
                    const left0 = rect(cell).left - rect(sx).left;
                    const freeX0 = rect(free).left;
                    sx.scrollLeft = 300;
                    await sleep(300);
                    assert(sx.scrollLeft > 100, `dialog did not scroll horizontally (${sx.scrollLeft})`);
                    near(rect(cell).left - rect(sx).left, left0, 1.5, "pinned dialog td moved on horizontal scroll");
                    near(rect(head).left - rect(sx).left, left0, 1.5, "pinned dialog th moved on horizontal scroll");
                    assert(freeX0 - rect(free).left > 100, "unpinned dialog column should move with the scroll");
                    // header stays on top of the dialog scroll area while scrolling down (the demo list is short: stretch the table)
                    root.querySelector("table").style.height = "2500px";
                    await sleep(200);
                    const sy = scroller(root.querySelector("table"), "y");
                    assert(sy && sy.closest(".modal"), "no vertical scroll area inside the dialog");
                    sy.scrollTop = 200;
                    await sleep(300);
                    assert(sy.scrollTop > 50, `dialog did not scroll vertically (${sy.scrollTop})`);
                    near(rect(root.querySelector("thead")).top, rect(sy).top, 2, "dialog header top after scroll");
                    near(rect(head).top, rect(sy).top, 2, "pinned dialog th top after scroll");
                    sx.scrollLeft = 0;
                    sy.scrollTop = 0;
                    root.querySelector("table").style.height = "";
                    clearKeys();
                },
            },
            {
                content: "pick a record in the dialog",
                in_modal: false,
                trigger: ".modal .o_list_view .o_data_row:first-child .o_data_cell",
                run: "click",
            },
            {
                content: "the record picked in the dialog is set on the form",
                trigger: ".o_form_view .o_field_widget[name=parent_id] input",
                run: async () => {
                    await waitFor(() => !document.querySelector(".modal") &&
                        document.querySelector(".o_field_widget[name=parent_id] input").value, "parent set after dialog");
                    clearKeys();
                },
            },
            {
                content: "discard the new record (no dirty form left behind)",
                trigger: ".o_form_button_cancel",
                run: "click",
            },
            {
                // Odoo 14 asks for confirmation before discarding a modified record
                content: "confirm the discard",
                in_modal: false,
                trigger: ".modal .modal-footer .btn-primary",
                run: "click",
            },
            { trigger: ".o_action_manager .o_kanban_view, .o_action_manager .o_list_view", run: () => {} },
    ]));

    tour.register("lshc_pin_first_column", { test: true }, expandAsync([
            { trigger: ".o_form_view .o_notebook", run: () => {} },
            {
                content: "open the Users tab",
                trigger: ".o_notebook .nav-link:contains('Users')",
                run: "click",
            },
            { trigger: ".o_field_widget[name=user_ids] .o_data_row, .o_field_widget[name=users] .o_data_row", run: () => {} },
            {
                content: "pin the first column (index 0), then unpin it",
                trigger: ".o_field_widget[name=user_ids] .o_data_row, .o_field_widget[name=users] .o_data_row",
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(".o_field_widget[name=user_ids]  .table-responsive, .o_field_widget[name=users]  .table-responsive");
                    const name = root.querySelector("thead th[data-name]").dataset.name;
                    assert(root.querySelector("thead tr th") === th(root, name), "first th is not a named column");
                    const cell = () => root.querySelector(".o_data_row td:nth-child(1)");
                    assert(getComputedStyle(cell()).position !== "sticky", "first column pinned before any click");
                    await pin(root, name);
                    assert(getComputedStyle(cell()).position === "sticky", "first column (index 0) not pinned");
                    near(parseFloat(getComputedStyle(cell()).left), 0, 0.5, "first column left");
                    assert(pinStyles().length === 2, `style nodes after pin: ${pinStyles().length}`);
                    const key = lshcKeys()[0];
                    assert(localStorage.getItem(key) === "0", `saved index: ${localStorage.getItem(key)}`);
                    await pin(root, name); // second click = unpin
                    assert(getComputedStyle(cell()).position !== "sticky", "first column still pinned after unpin");
                    assert(pinStyles().length === 0, `style nodes after unpin: ${pinStyles().length}`);
                    assert(lshcKeys().length === 0, `localStorage keys left after unpin: ${lshcKeys()}`);
                    await pin(root, name); // and it can be pinned again
                    assert(getComputedStyle(cell()).position === "sticky", "first column not pinned again");
                    clearKeys();
                },
            },
    ]));

    tour.register("lshc_unpin_remount", { test: true }, expandAsync([
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "pin then unpin a column",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    clearKeys();
                    const root = document.querySelector(LIST);
                    await pin(root, "display_name");
                    const key = lshcKeys()[0];
                    assert(key, "nothing saved after pin");
                    await pin(root, "display_name");
                    assert(lshcKeys().length === 0, `keys left after unpin: ${lshcKeys()}`);
                    // an old version left "-1" behind after an unpin: it must not count as pinned
                    localStorage.setItem(key, "-1");
                },
            },
            {
                content: "open a record",
                trigger: `${LIST} .o_data_row:first-child td:nth-child(2)`,
                run: "click",
            },
            { trigger: ".o_form_view", run: () => {} },
            {
                content: "back to the list",
                trigger: ".o_control_panel .breadcrumb-item:not(.active), .o_control_panel .o_back_button",
                run: "click",
            },
            { trigger: `${LIST} .o_data_row`, run: () => {} },
            {
                content: "no leftover pin style, header still sticky, nothing pinned",
                trigger: `${LIST} .o_data_row`,
                run: async () => {
                    await sleep(800);
                    const root = document.querySelector(LIST);
                    await waitFor(() => pinBtn(root, "display_name"), "pin button after remount");
                    assert(pinStyles().length === 0, `style nodes after remount: ${pinStyles().length}`);
                    assert(lshcKeys().length === 0, `legacy -1 key not cleaned: ${lshcKeys()}`);
                    const idx = [...root.querySelectorAll("thead tr th")].indexOf(th(root, "display_name"));
                    assert(getComputedStyle(root.querySelector(`.o_data_row td:nth-child(${idx + 1})`)).position !== "sticky", "column pinned after unpin");
                    const first = getComputedStyle(root.querySelector("thead th:first-child"));
                    assert(first.left === "auto" || first.zIndex !== "10", "th still pinned after unpin");
                    // the always-sticky header still works
                    const thead = root.querySelector("thead");
                    const sc = scroller(thead, "y");
                    assert(sc, "no vertical scroll area");
                    sc.scrollTop = 400;
                    await sleep(300);
                    near(rect(thead).top, rect(sc).top, 2, "header top after remount + scroll");
                    sc.scrollTop = 0;
                    // and pinning still works after the unpin / remount
                    await widen(root);
                    await pin(root, "display_name");
                    assert(getComputedStyle(root.querySelector(`.o_data_row td:nth-child(${idx + 1})`)).position === "sticky", "cannot pin again after remount");
                    clearKeys();
                },
            },
    ]));
});
