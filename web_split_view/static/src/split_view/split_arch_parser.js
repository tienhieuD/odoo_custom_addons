/** @odoo-module **/

/**
 * Parse the arch of a <split> view:
 *
 *   <split list_view_ref="module.xmlid" form_view_ref="module.xmlid"/>
 *
 * or with the sub views defined inline:
 *
 *   <split><list>...</list><form>...</form></split>
 *
 * (`tree_view_ref` / `<tree>` are accepted as aliases of the list ones.)
 */
export class SplitArchParser {
    parse(xmlDoc) {
        const serializer = new XMLSerializer();
        const child = (...tags) => [...xmlDoc.children].find((el) => tags.includes(el.tagName));
        const listNode = child("list", "tree");
        const formNode = child("form");
        return {
            listRef: xmlDoc.getAttribute("list_view_ref") || xmlDoc.getAttribute("tree_view_ref") || false,
            formRef: xmlDoc.getAttribute("form_view_ref") || false,
            listArch: listNode ? serializer.serializeToString(listNode) : false,
            formArch: formNode ? serializer.serializeToString(formNode) : false,
            className: xmlDoc.getAttribute("class") || "",
        };
    }
}
