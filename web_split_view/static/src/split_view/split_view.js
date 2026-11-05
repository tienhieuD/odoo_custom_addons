import { registry } from "@web/core/registry";
import { SplitArchParser } from "./split_arch_parser";
import { SplitController } from "./split_controller";
import "./split_list_view";

export const splitView = {
    type: "split",
    ArchParser: SplitArchParser,
    Controller: SplitController,
    buttonTemplate: "web_split_view.SplitView.Buttons",
    // search bar, filters and pager belong to the embedded list view
    searchMenuTypes: [],

    props: (genericProps, view) => {
        const { ArchParser, buttonTemplate: viewButtonTemplate } = view;
        const { arch, buttonTemplate } = genericProps;
        return {
            ...genericProps,
            archInfo: new ArchParser().parse(arch),
            buttonTemplate: buttonTemplate || viewButtonTemplate,
        };
    },
};

registry.category("views").add("split", splitView);
