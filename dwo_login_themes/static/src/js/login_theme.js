/* Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
 * Small helpers for the themed login page. Plain JavaScript, no Odoo module system: the page works without it
 * (it only closes the announcement, sets the tab title and icon, and adds a show/hide password button when
 * the standard page does not have one). */
(function () {
    "use strict";
    function ready(fn) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", fn);
        } else {
            fn();
        }
    }
    function storage() {
        try {
            return window.localStorage;
        } catch (e) {
            return null;
        }
    }
    ready(function () {
        var notice = document.querySelector(".dwo_notice[data-dwo-notice]");
        if (notice) {
            var key = "dwo_login_notice_closed_" + notice.getAttribute("data-dwo-notice");
            var store = storage();
            var closeButton = notice.querySelector(".dwo_notice_close");
            if (closeButton) {
                try {
                    if (store && store.getItem(key)) {
                        notice.parentNode.removeChild(notice);
                    }
                } catch (e) { /* private mode: show it */ }
                closeButton.addEventListener("click", function () {
                    try {
                        if (store) {
                            store.setItem(key, "1");
                        }
                    } catch (e) { /* not remembered */ }
                    if (notice.parentNode) {
                        notice.parentNode.removeChild(notice);
                    }
                });
            }
        }
        var root = document.querySelector(".dwo_lc");
        if (!root) {
            return;
        }
        var title = root.getAttribute("data-dwo-title");
        if (title) {
            document.title = title;
        }
        var icon = root.getAttribute("data-dwo-favicon");
        if (icon) {
            var links = document.querySelectorAll("link[rel~='icon']");
            for (var i = 0; i < links.length; i++) {
                links[i].parentNode.removeChild(links[i]);
            }
            var link = document.createElement("link");
            link.rel = "icon";
            link.type = "image/png";
            link.href = icon;
            document.head.appendChild(link);
        }
        var field = document.getElementById("password");
        if (root.getAttribute("data-dwo-pwd") === "1" && field && !document.querySelector(".o_show_password, .dwo_pwd_btn")) {
            var group = document.createElement("div");
            group.className = "input-group";
            field.parentNode.insertBefore(group, field);
            group.appendChild(field);
            var button = document.createElement("button");
            button.type = "button";
            button.className = "btn btn-sm border border-start-0 dwo_pwd_btn";
            button.setAttribute("aria-label", "Show or hide the password");
            button.innerHTML = '<i class="fa fa-eye" aria-hidden="true"></i>';
            button.addEventListener("click", function () {
                var show = field.type === "password";
                field.type = show ? "text" : "password";
                button.firstChild.className = show ? "fa fa-eye-slash" : "fa fa-eye";
            });
            group.appendChild(button);
        }
    });
})();
