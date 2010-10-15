<%inherit file="/base.mako"/>

<%def name="title()">People</%def>

Here are ${len(c.random_people)} random people from our population of ${c.person_count}.<br>
<br>
% for person in c.random_people:
${person.nickname}
% endfor
