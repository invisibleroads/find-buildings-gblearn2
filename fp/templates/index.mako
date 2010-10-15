<%inherit file="/base.mako"/>\


<%def name="title()">Satellite Image Recognition System</%def>


<%def name="toolbar()">
<a class=linkOFF href="${h.url_for('person_index')}">${c.personCount} people</a>, 
<a class=linkOFF href="${h.url_for('jobs')}">${c.jobCount} jobs</a>
% if c.jobPendingCount:
    (${100 * c.jobPendingCount / c.jobCount}% pending)
% endif
</%def>
