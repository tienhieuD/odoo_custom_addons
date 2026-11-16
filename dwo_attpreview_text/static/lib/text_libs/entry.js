// Bundle of the libraries of dwo_attpreview_text (see static/lib/text_libs/BUILD.md), loaded on demand as the global
// DwoTextLibs: syntax colours (highlight.js), Markdown (markdown-it), YAML (js-yaml), TOML (smol-toml). Nothing here runs
// the content of a file.
import hljs from "highlight.js/lib/core";
import MarkdownIt from "markdown-it";
import { load as yamlLoad, loadAll as yamlLoadAll } from "js-yaml";
import { parse as tomlParse } from "smol-toml";
import hljsCss from "highlight.js/styles/github.css";

const LANGS = {
    xml: require("highlight.js/lib/languages/xml"),
    markdown: require("highlight.js/lib/languages/markdown"),
    json: require("highlight.js/lib/languages/json"),
    yaml: require("highlight.js/lib/languages/yaml"),
    ini: require("highlight.js/lib/languages/ini"),
    properties: require("highlight.js/lib/languages/properties"),
    python: require("highlight.js/lib/languages/python"),
    javascript: require("highlight.js/lib/languages/javascript"),
    typescript: require("highlight.js/lib/languages/typescript"),
    css: require("highlight.js/lib/languages/css"),
    scss: require("highlight.js/lib/languages/scss"),
    sql: require("highlight.js/lib/languages/sql"),
    bash: require("highlight.js/lib/languages/bash"),
    powershell: require("highlight.js/lib/languages/powershell"),
    dos: require("highlight.js/lib/languages/dos"),
    java: require("highlight.js/lib/languages/java"),
    kotlin: require("highlight.js/lib/languages/kotlin"),
    swift: require("highlight.js/lib/languages/swift"),
    c: require("highlight.js/lib/languages/c"),
    cpp: require("highlight.js/lib/languages/cpp"),
    csharp: require("highlight.js/lib/languages/csharp"),
    go: require("highlight.js/lib/languages/go"),
    rust: require("highlight.js/lib/languages/rust"),
    php: require("highlight.js/lib/languages/php"),
    ruby: require("highlight.js/lib/languages/ruby"),
    dart: require("highlight.js/lib/languages/dart"),
    lua: require("highlight.js/lib/languages/lua"),
    r: require("highlight.js/lib/languages/r"),
    perl: require("highlight.js/lib/languages/perl"),
    scala: require("highlight.js/lib/languages/scala"),
    groovy: require("highlight.js/lib/languages/groovy"),
    gradle: require("highlight.js/lib/languages/gradle"),
    dockerfile: require("highlight.js/lib/languages/dockerfile"),
    makefile: require("highlight.js/lib/languages/makefile"),
    nginx: require("highlight.js/lib/languages/nginx"),
    diff: require("highlight.js/lib/languages/diff"),
    latex: require("highlight.js/lib/languages/latex"),
    plaintext: require("highlight.js/lib/languages/plaintext"),
};
for (const [name, lang] of Object.entries(LANGS)) {
    hljs.registerLanguage(name, lang.default || lang);
}

export { hljs, MarkdownIt, yamlLoad, yamlLoadAll, tomlParse, hljsCss };
