from markupsafe import Markup, escape
from wtforms.widgets import html_params


class CooperativeMembershipListWidget:

    def __init__(self, can_change=True):
        self.can_change = can_change

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)

        tbody = []
        thead = []

        for row in field:
            if len(thead) == 0:
                thead.append("<tr>")
                for column_field in row:
                    thead.append(f"<th>{column_field.label()}</th>")
                thead.append("</tr>")

            tbody.append("<tr>")
            for column_field in row:
                tbody.append(f"<td>")
                tbody.append(column_field())

                if column_field.errors:
                    tbody.append('<ul class="padding-inline: 0; list-style: none; color: #ff206b;">')
                    for error in column_field.errors:
                        tbody.append(f'<li class="form-errors__item">{error}</li>')
                        tbody.append("</ul>")

                tbody.append(f"</td>")

            tbody.append("</tr>")

        name = f"{field.short_name}{field._separator}{{0}}"
        id = f"{field.id}{field._separator}{{0}}"
        template_field = field.unbound_field.bind(
            form=None,
            name=name,
            prefix=field._prefix,
            id=id,
            _meta=field.meta,
            translations=field._translations,
        )
        template_field.process(formdata=None)

        template = []
        template.append("<tr>")
        for column_field in template_field:
            template.append(f"<td>")
            template.append(column_field())

            if column_field.errors:
                template.append('<ul class="padding-inline: 0; list-style: none; color: #ff206b;">')
                for error in column_field.errors:
                    template.append(f'<li class="form-errors__item">{error}</li>')
                    template.append("</ul>")

            template.append(f"</td>")

        template.append("</tr>")

        return Markup(f"""
<div id="{kwargs['id']}">
<table>
    <thead>
        {''.join(thead)}
    </thead>
    <tbody>
        {''.join(tbody)}
    </tbody>
</table>
<template>
{''.join(template)}
</template>
<script>
(function() {{
    let lastIndex = {field.last_index};

    window.{kwargs['id']}AddRow = function {kwargs['id']}AddRow() {{
        const template = document.querySelector("#{kwargs['id']} template");
        const tbody = document.querySelector("#{kwargs['id']} tbody");
        const clone = template.content.cloneNode(true);
        const tr = clone.querySelector("tr");
        tr.innerHTML = tr.innerHTML.replace(/\\{{0\\}}/g, lastIndex + 1);
        tbody.appendChild(tr);

        lastIndex += 1;
    }}
}})()
</script>
<button type="button" onclick="{kwargs['id']}AddRow()">Добавить</button>
</div>
""")


class OwnerForeignKeyWidget:
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        id = kwargs['id'].replace("-", "_")
        value = kwargs["value"] if "value" in kwargs else field._value()

        return Markup(f"""
<span id="{id}">
<script>
function selectOwnerForeignKey() {{
    console.log(this)
    const win = window.open("/owners/search?popup=1", "_blank", "popup=1")
    if (!win) return;
    win.addEventListener("select_owner", (e) => {{
        const owner = e.detail;
        this.parentElement.querySelector("b").innerText = owner.name;
        this.parentElement.querySelector("input").value = owner.id;
        this.innerText = "Изменить"
        win.close();
    }}, {{ once: true }})
}}
</script>
<input type="hidden" {html_params(value=value, name=field.name)} />
<b></b>
<button type="button" onclick="selectOwnerForeignKey.apply(this)">Выбрать</button>
</span>
""")
