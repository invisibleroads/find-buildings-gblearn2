<%def name="formatPercent(value, fromDecimal=True)">
<%
    value = float(value) * 100 if fromDecimal else float(value)
%>
${'%.2f %%' % value}
</%def>


<%def name="unstringifyList(title, string)">
<%
    from libraries import store
    items = store.unstringifyStringList(string)
%>
% if items:
${title}
<ul>
    % for item in items:
        <li>${item}</li>
    % endfor
</ul>
% endif
</%def>


<%def name="unstringifyListAsLine(string)">
<%
    from libraries import store
    items = store.unstringifyStringList(string)
    items.sort()
%>
% if items:
    % for item in items:
        ${item}<br>
    % endfor
% endif
</%def>
