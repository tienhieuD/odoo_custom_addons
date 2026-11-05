# Wiki của project Odoo custom addons

Mỗi module có một thư mục riêng ở đây: kiến trúc, quyết định thiết kế, khác biệt theo phiên bản, cách test, cách đóng gói.
Thư mục này được chép vào **mọi nhánh** của repo `odoo_custom_addons` (12.0 đến 20.0) để ai checkout nhánh nào cũng có: khi sửa, sửa một nơi rồi chép sang các nhánh còn lại.

| Module | Nội dung |
|---|---|
| [web_split_view](web_split_view/README.md) | Chế độ Split (list + form cạnh nhau) tự động cho mọi list, bản 12 đến 20 (12 đến 15 kiến trúc legacy) |
| [listview_sticky_header_and_column](listview_sticky_header_and_column/README.md) | Ghim cột và header của list, bản 12 đến 20, kèm module test `lab` |

Các file liên quan nằm ngoài wiki:
- `listings/<module>.json` (trong wiki): cấu hình trang mô tả cho Odoo Apps (dùng với skill `odoo-apps-listing`).
- `~/.claude/skills/odoo-apps-listing`: sinh `index.html`, icon, banner, flow và kiểm tra theo Vendor Guidelines.
