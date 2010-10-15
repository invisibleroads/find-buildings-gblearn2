<%inherit file="/base.mako"/>\

<%def name="title()">Satellite Image Recognition System</%def>

<%def name="toolbar()">
<a class=linkOFF href="${h.url_for('new_job')}">Click here to create a new job</a>
</%def>

Satellite Image Recognition System
% if c.jobs:
<table>
<tr>
    <td>Job number</td>
    <td>Summary</td>
    <td>Shapefile and spreadsheet</td>
</tr>
% for job in c.jobs:
<tr>
    <td>
    ${job.id}
    </td>
    % if not job.pickled_output:
    <td>
        <a class=linkOFF href="${h.url_for('formatted_job', id=job.id, format='html')}">View input</a>
    </td>
    % else:
    <td>
        <a class=linkOFF href="${h.url_for('formatted_job', id=job.id, format='html')}">View input and output</a>
    </td>
    <td>
        <a class=linkOFF href="${h.url_for('formatted_job', id=job.id, format='zip')}">Download</a>
    </td>
    % endif
</tr>
% endfor
</table>
% endif

<%def name="css()"></%def>
<%def name="head()"></%def>
<%def name="js()"></%def>

<%def name="navigation()"></%def>
<%def name="board()"></%def>
<%def name="support()"></%def>
