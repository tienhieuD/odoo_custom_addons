# Wiki của project Odoo custom addons

Mỗi module có một thư mục riêng ở đây: kiến trúc, quyết định thiết kế, khác biệt theo phiên bản, cách test, cách đóng gói.
Thư mục này tên **`.wiki`** (ẩn, nằm ở gốc repo) và được chép vào **mọi nhánh** của repo `odoo_custom_addons` (12.0 đến 20.0) để ai checkout nhánh nào cũng có. Bản gốc để sửa nằm ở `myproject/.wiki`: sửa ở đó rồi chép sang `.wiki/` của từng repo (`rsync -a --delete --exclude .DS_Store --exclude __pycache__ myproject/.wiki/ myproject/odoo_custom_addonsNN/.wiki/`).
Tương tự, module test nội bộ nằm ở thư mục ẩn **`.lab`** (`odoo_custom_addonsNN/.lab/listview_sticky_test_lab`): tên bắt đầu bằng dấu chấm để store và các công cụ quét thư mục bỏ qua, và `.../odoo_custom_addonsNN/.lab` phải có trong `addons_path` của conf.

| Module | Nội dung |
|---|---|
| [web_split_view](web_split_view/README.md) | Chế độ Split (list + form cạnh nhau) tự động cho mọi list, bản 12 đến 20 (12 đến 15 kiến trúc legacy) |
| [listview_sticky_header_and_column](listview_sticky_header_and_column/README.md) | Ghim cột và header của list, bản 12 đến 20, kèm module test `lab` |
| [dwo_record_concurrency](dwo_record_concurrency/README.md) | Cảnh báo mềm khi hai người cùng sửa một bản ghi (Record Concurrency Guard), bản 12 đến 20 (12 đến 15 kiến trúc legacy) |

Các file liên quan nằm ngoài wiki:
- `listings/<module>.json` (trong wiki): cấu hình trang mô tả cho Odoo Apps (dùng với skill `odoo-apps-listing`).
- `~/.claude/skills/odoo-apps-listing`: sinh `index.html`, icon, banner, flow và kiểm tra theo Vendor Guidelines.
