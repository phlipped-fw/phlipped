"""Render a PHLIPPED assessment into a one-page HTML report."""
from __future__ import annotations

from jinja2 import Template

from .scoring import Item

_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PHLIPPED posture report</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:52rem;margin:2rem auto;padding:0 1rem;line-height:1.5}
 .score{font-size:3rem;font-weight:700}
 table{border-collapse:collapse;width:100%}
 th,td{text-align:left;padding:.4rem .6rem;border-bottom:1px solid #ccc;vertical-align:top}
 .w{text-align:right}
</style>
</head>
<body>
<h1>Physical Security Posture Score</h1>
<p class="score">{{ psps }} / 100</p>
{% if gaps %}
<h2>Top gaps (priority order)</h2>
<table>
<thead><tr><th>ID</th><th class="w">Weight</th><th>Recommendation</th><th>Threats</th><th class="w">&euro;</th><th class="w">hrs</th></tr></thead>
<tbody>
{% for g in gaps %}
<tr>
 <td>{{ g.id }}</td>
 <td class="w">{{ g.weight }}</td>
 <td>{{ g.recommendation }}</td>
 <td>{% for ref in g.threat_refs %}<a href="{{ base_url }}/{{ ref }}.html">{{ ref }}</a>{% if not loop.last %}, {% endif %}{% endfor %}</td>
 <td class="w">{{ g.cost_eur }}</td>
 <td class="w">{{ g.effort_hours }}</td>
</tr>
{% endfor %}
</tbody>
</table>
{% else %}
<p>No gaps recorded.</p>
{% endif %}
</body>
</html>
"""
)


def render_report(psps: float, gaps: list[Item], base_url: str = "/threats") -> str:
    """Render the report HTML. gaps are rendered in the order given."""
    return _TEMPLATE.render(psps=psps, gaps=gaps, base_url=base_url)
