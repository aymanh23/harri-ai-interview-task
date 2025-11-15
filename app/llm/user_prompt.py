from jinja2 import Template

user_prompt_template: Template = Template("""
    User query:
    "{{ query }}"

    Intents:
    {% for intent in intents -%}
    - {{ intent }}
    {% endfor %}

    Retrieved context:
    {% for r in retrievals %}
    [{{ loop.index }}]
    Source: {{ r.source }}

    {% if r.section is defined %}
    Section: {{ r.section }}
    {% endif %}

    {% if r.content is defined %}
    Content:
    {{ r.content.rstrip('-').rstrip() }}
    {% endif %}

    {% if r.data is defined %}
    Data:
    {{ r.data | tojson(indent=2) }}
    {% endif %}

    ---
    {% endfor %}
    
    """)